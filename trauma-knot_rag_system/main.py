"""
FastAPI Server for Trauma Knot RAG System
Provides REST API endpoints for the RAG system
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import os
from pathlib import Path
import json
from datetime import datetime
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import networkx as nx

from rag_system import TraumaKnotRAG
from trauma_knot_kb import TraumaKnotKB

# Initialize FastAPI app
app = FastAPI(
    title="Trauma Knot RAG System",
    description="AI-powered analysis and suggestions based on Trauma Knot Framework",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global RAG instance and storage
rag_sessions: Dict[str, TraumaKnotRAG] = {}
conversations_dir = Path("conversations")
conversations_dir.mkdir(exist_ok=True)

# ========================
# Request/Response Models
# ========================

class UserMessage(BaseModel):
    """User message input"""
    message: str = Field(..., min_length=10, description="User's problem or question")
    session_id: Optional[str] = Field(None, description="Optional session ID for conversation continuity")


class TraumaNodeInfo(BaseModel):
    """Information about a trauma node"""
    name: str
    category: str
    description: str
    connections: Dict


class ContextInfo(BaseModel):
    """Context retrieved from knowledge base"""
    relevant_nodes: List[TraumaNodeInfo]
    trauma_cycles: List[List[str]]
    intervention_points: List[Dict]
    healing_pathways: List[Dict]


class AIResponse(BaseModel):
    """AI-generated response"""
    response: str
    context: ContextInfo
    session_id: str
    timestamp: str


class ConversationHistory(BaseModel):
    """Conversation history"""
    session_id: str
    message_count: int
    exchanges: int
    created_at: str
    messages: List[Dict]


class TraumaCycleVisualization(BaseModel):
    """Trauma cycle visualization data"""
    cycle: List[str]
    edges: List[Dict]
    break_points: List[Dict]
    severity_score: float


# ========================
# Helper Functions
# ========================

def get_or_create_session(session_id: Optional[str]) -> tuple[str, TraumaKnotRAG]:
    """Get existing session or create new one"""
    if session_id and session_id in rag_sessions:
        return session_id, rag_sessions[session_id]
    
    new_session_id = datetime.now().isoformat()
    rag = TraumaKnotRAG()
    rag_sessions[new_session_id] = rag
    return new_session_id, rag


def save_session(session_id: str, rag: TraumaKnotRAG):
    """Save session to disk"""
    filepath = conversations_dir / f"{session_id}.json"
    rag.save_conversation(str(filepath))


# ========================
# Endpoints
# ========================

@app.get("/")
async def root():
    """API information"""
    return {
        "name": "Trauma Knot RAG System",
        "version": "1.0.0",
        "description": "AI-powered trauma analysis using Retrieval Augmented Generation",
        "endpoints": {
            "POST /chat": "Submit a message and get AI response",
            "GET /sessions/{session_id}": "Get conversation history",
            "DELETE /sessions/{session_id}": "Delete a session",
            "GET /cycles": "Get trauma cycles in the knowledge base",
            "GET /nodes": "Get all trauma nodes",
            "POST /visualize-cycle": "Visualize a specific trauma cycle",
            "GET /interventions": "Get intervention strategies"
        }
    }


@app.post("/chat", response_model=Dict)
async def chat(message: UserMessage, background_tasks: BackgroundTasks):
    """
    Chat endpoint - submit user problem, get AI analysis and suggestions
    """
    try:
        # Get or create session
        session_id, rag = get_or_create_session(message.session_id)
        
        # Generate response
        result = rag.generate_response(message.message)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Save session in background
        background_tasks.add_task(save_session, session_id, rag)
        
        return {
            "success": True,
            "session_id": session_id,
            "response": result["response"],
            "relevant_nodes": result["context"].get("relevant_nodes", []),
            "trauma_cycles": result["context"].get("trauma_cycles", []),
            "intervention_points": result["context"].get("intervention_points", []),
            "healing_pathways": result["context"].get("healing_pathways", []),
            "timestamp": result["timestamp"]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/clinical/assess", response_model=Dict)
async def clinical_assess(message: UserMessage, background_tasks: BackgroundTasks):
    """Run clinical assessment and generate a prioritized plan + follow-up questions"""
    try:
        session_id, rag = get_or_create_session(message.session_id)

        # Quick safety check for crisis language
        crisis_terms = ["suicide", "kill myself", "harm myself", "self-harm", "overdose", "end my life", "want to die"]
        text_lower = message.message.lower()
        if any(term in text_lower for term in crisis_terms):
            # Immediate crisis advice response
            crisis_advice = (
                "If you are in immediate danger or thinking about harming yourself, please call your local emergency number now. "
                "If you are in the United States, you can call or text 988 for the Suicide & Crisis Lifeline. "
                "If you are elsewhere, contact local emergency services or a crisis helpline. "
                "If possible, reach out to someone you trust and stay in a safe place until you can get help."
            )
            return {
                "success": False,
                "crisis": True,
                "crisis_advice": crisis_advice,
                "session_id": session_id
            }

        # Run clinical assessment
        result = rag.clinical_assess_and_plan(message.message, followup_questions=3)

        # Save session in background
        background_tasks.add_task(save_session, session_id, rag)

        return {
            "success": True,
            "session_id": session_id,
            "analysis": result.get("analysis"),
            "knot_summaries": result.get("knot_summaries"),
            "context": result.get("context"),
            "timestamp": result.get("timestamp")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/clinical/followup")
async def clinical_followup(session_id: Optional[str] = None):
    """Generate a clinician-style follow-up question for the given session (or latest)."""
    try:
        if session_id and session_id in rag_sessions:
            rag = rag_sessions[session_id]
        else:
            # Use the most recent session if available
            if not rag_sessions:
                raise HTTPException(status_code=404, detail="No active sessions available")
            # pick latest by key ordering (ISO timestamps)
            latest = sorted(rag_sessions.keys())[-1]
            rag = rag_sessions[latest]

        question = rag.generate_followup_question()
        return {"success": True, "question": question, "session_id": rag.session_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get conversation history for a session"""
    try:
        if session_id in rag_sessions:
            rag = rag_sessions[session_id]
        else:
            # Try to load from disk
            filepath = conversations_dir / f"{session_id}.json"
            if not filepath.exists():
                raise HTTPException(status_code=404, detail="Session not found")
            
            rag = TraumaKnotRAG()
            rag.load_conversation(str(filepath))
            rag_sessions[session_id] = rag
        
        summary = rag.get_conversation_summary()
        
        return {
            "session_id": session_id,
            "summary": summary,
            "messages": rag.conversation_history
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    try:
        # Remove from memory
        if session_id in rag_sessions:
            del rag_sessions[session_id]
        
        # Remove from disk
        filepath = conversations_dir / f"{session_id}.json"
        if filepath.exists():
            filepath.unlink()
        
        return {"success": True, "message": "Session deleted"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/cycles")
async def get_trauma_cycles():
    """Get all trauma cycles from knowledge base"""
    try:
        kb = TraumaKnotKB()
        cycles = kb.get_trauma_cycles()
        
        return {
            "total_cycles": len(cycles),
            "cycles": [" → ".join(cycle) for cycle in cycles]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/nodes")
async def get_nodes():
    """Get all trauma nodes organized by category"""
    try:
        kb = TraumaKnotKB()
        
        nodes_by_category = {}
        for category, nodes in kb.node_categories.items():
            nodes_by_category[category] = nodes
        
        return {
            "total_nodes": sum(len(n) for n in nodes_by_category.values()),
            "categories": nodes_by_category
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/visualize-cycle")
async def visualize_cycle(data: Dict):
    """Generate visualization of a specific trauma cycle"""
    try:
        cycle = data.get("cycle", [])
        if not cycle or len(cycle) < 2:
            raise HTTPException(status_code=400, detail="Invalid cycle provided")
        
        kb = TraumaKnotKB()
        G = kb.G
        
        # Create visualization
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Create subgraph for the cycle
        cycle_nodes = cycle
        subgraph = G.subgraph(cycle_nodes)
        
        # Layout
        pos = nx.circular_layout(subgraph)
        
        # Draw
        nx.draw_networkx_nodes(subgraph, pos, node_color='lightblue', node_size=2000, ax=ax)
        nx.draw_networkx_labels(subgraph, pos, font_size=8, ax=ax)
        
        # Draw edges
        edges = [(cycle[i], cycle[(i+1) % len(cycle)]) for i in range(len(cycle))]
        nx.draw_networkx_edges(subgraph, pos, edgelist=edges, 
                               edge_color='red', arrows=True, 
                               arrowsize=20, arrowstyle='->', width=2, ax=ax)
        
        # Add edge labels
        edge_labels = {}
        for u, v in edges:
            if G.has_edge(u, v):
                edge_labels[(u, v)] = f"{G[u][v]['weight']}"
        
        nx.draw_networkx_edge_labels(subgraph, pos, edge_labels, font_size=8, ax=ax)
        
        ax.set_title(f"Trauma Cycle: {' → '.join(cycle)}", fontsize=14, fontweight='bold')
        ax.axis('off')
        plt.tight_layout()
        
        # Save
        viz_dir = Path("visualizations")
        viz_dir.mkdir(exist_ok=True)
        viz_path = viz_dir / f"cycle_{datetime.now().timestamp()}.png"
        plt.savefig(viz_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        # Get intervention points
        interventions = kb.get_intervention_points(cycle)
        
        return {
            "cycle": cycle,
            "visualization_path": str(viz_path),
            "interventions": interventions,
            "severity": sum([G[cycle[i]][cycle[(i+1) % len(cycle)]]['weight'] 
                            for i in range(len(cycle))]) / len(cycle)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/interventions")
async def get_interventions():
    """Get intervention strategies for common trauma cycles"""
    try:
        kb = TraumaKnotKB()
        cycles = kb.get_trauma_cycles()
        
        interventions = []
        for cycle in cycles[:5]:  # Top 5 cycles
            cycle_interventions = kb.get_intervention_points(cycle)
            if cycle_interventions:
                interventions.append({
                    "cycle": " → ".join(cycle),
                    "strategies": cycle_interventions
                })
        
        return {
            "total_cycles_analyzed": len(cycles),
            "interventions": interventions
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "active_sessions": len(rag_sessions),
        "timestamp": datetime.now().isoformat()
    }


# ========================
# Startup/Shutdown
# ========================

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    print("Trauma Knot RAG System started")
    print(f"Conversations directory: {conversations_dir}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    # Save all active sessions
    for session_id, rag in rag_sessions.items():
        save_session(session_id, rag)
    print("All sessions saved. System shutdown.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

