"""
Example Demo Script - Trauma Knot RAG System
Demonstrates how to use the RAG system programmatically
"""

import os
from dotenv import load_dotenv
from rag_system import TraumaKnotRAG
from trauma_knot_kb import TraumaKnotKB

# Load environment variables
load_dotenv()


def demo_basic_chat():
    """Demo 1: Basic single-turn chat"""
    print("\n" + "="*70)
    print("DEMO 1: Basic Chat")
    print("="*70)
    
    rag = TraumaKnotRAG()
    
    user_message = """
    I was in a car accident 6 months ago and I've been struggling since then.
    I have nightmares about it and I avoid driving altogether. When I think about 
    getting behind the wheel, I start panicking. My relationships are suffering 
    because I can't even go on dates or visit friends anymore.
    """
    
    print(f"\n👤 User: {user_message.strip()}\n")
    
    response = rag.generate_response(user_message)
    
    print(f"🤖 AI Response:\n{response['response']}\n")
    
    if response.get("context"):
        print("\n📍 Analysis Context:")
        print(f"Relevant Nodes: {len(response['context'].get('relevant_nodes', []))}")
        print(f"Identified Cycles: {len(response['context'].get('trauma_cycles', []))}")
        print(f"Intervention Points: {len(response['context'].get('intervention_points', []))}\n")


def demo_multi_turn_conversation():
    """Demo 2: Multi-turn conversation with context"""
    print("\n" + "="*70)
    print("DEMO 2: Multi-turn Conversation")
    print("="*70)
    
    rag = TraumaKnotRAG()
    
    messages = [
        "I've been dealing with shame and rejection from my past relationship.",
        "How does avoidance make things worse?",
        "What can I do to break this cycle?",
    ]
    
    for i, msg in enumerate(messages, 1):
        print(f"\n👤 User (message {i}): {msg}")
        response = rag.generate_response(msg)
        print(f"\n🤖 AI: {response['response'][:300]}...")
    
    print("\n\n📜 Full Conversation History:")
    for i, msg in enumerate(rag.conversation_history, 1):
        role = "👤" if msg["role"] == "user" else "🤖"
        print(f"{i}. {role}: {msg['content'][:60]}...")
    
    # Save the conversation
    rag.save_conversation("conversations/demo_conversation.json")
    print("\n✅ Conversation saved!")


def demo_knowledge_base_exploration():
    """Demo 3: Explore the knowledge base"""
    print("\n" + "="*70)
    print("DEMO 3: Knowledge Base Exploration")
    print("="*70)
    
    kb = TraumaKnotKB()
    
    # Get all cycles
    cycles = kb.get_trauma_cycles()
    print(f"\n🔥 Found {len(cycles)} trauma cycles:")
    for i, cycle in enumerate(cycles[:3], 1):
        print(f"  {i}. {' → '.join(cycle)}")
    
    # Explore specific node
    node_name = "Avoidance"
    node_info = kb.get_node_description(node_name)
    print(f"\n📌 Node Details: {node_info['name']}")
    print(f"   Category: {node_info['category']}")
    print(f"   Description: {node_info['description']}")
    print(f"   Incoming: {node_info['connections']['incoming']}")
    print(f"   Outgoing: {node_info['connections']['outgoing']}")
    
    # Get intervention strategies
    print("\n🔧 Intervention Strategies for Top Cycle:")
    if cycles:
        top_cycle = cycles[0]
        interventions = kb.get_intervention_points(top_cycle)
        for intervention in interventions[:3]:
            print(f"  • {intervention['edge']}")
            print(f"    → {intervention['intervention']}")


def demo_context_retrieval():
    """Demo 4: See how context is retrieved"""
    print("\n" + "="*70)
    print("DEMO 4: Context Retrieval Process")
    print("="*70)
    
    rag = TraumaKnotRAG()
    
    user_input = "I'm having panic attacks and can't leave my house"
    
    print(f"\n📥 User Input: {user_input}")
    
    # Retrieve context
    context = rag.retrieve_context(user_input)
    
    print("\n🔍 Retrieved Context:")
    print(f"\n1️⃣ Relevant Psychological Nodes ({len(context['relevant_nodes'])}):")
    for node in context['relevant_nodes']:
        print(f"   • {node['name']}: {node['description']}")
    
    print(f"\n2️⃣ Trauma Cycles ({len(context['trauma_cycles'])}):")
    for cycle in context['trauma_cycles']:
        print(f"   • {' → '.join(cycle)}")
    
    print(f"\n3️⃣ Intervention Points ({len(context['intervention_points'])}):")
    for point in context['intervention_points'][:3]:
        print(f"   • {point['edge']}: {point['intervention']}")
    
    print(f"\n4️⃣ Healing Pathways ({len(context['healing_pathways'])}):")
    for pathway in context['healing_pathways'][:3]:
        print(f"   • {pathway['healing_factor']}: {pathway['description']}")


def demo_trauma_cycle_analysis():
    """Demo 5: Analyze specific trauma cycle"""
    print("\n" + "="*70)
    print("DEMO 5: Trauma Cycle Analysis")
    print("="*70)
    
    kb = TraumaKnotKB()
    
    # Get the strongest cycles
    cycles = kb.get_trauma_cycles()
    
    if cycles:
        cycle = cycles[0]
        print(f"\n🎯 Analyzing Cycle: {' → '.join(cycle)}")
        
        # Get intervention points
        interventions = kb.get_intervention_points(cycle)
        
        print(f"\n🔧 Intervention Strategy:")
        for intervention in interventions:
            print(f"  Break Point: {intervention['edge']}")
            print(f"  Priority: {intervention['priority']}")
            print(f"  Strategy: {intervention['intervention']}")
        
        # Get healing pathways
        print(f"\n🌱 Healing Pathways from first node:")
        healing = kb.get_healing_pathways(cycle[0])
        for pathway in healing[:3]:
            print(f"  • {pathway['healing_factor']}")


def demo_session_management():
    """Demo 6: Session management"""
    print("\n" + "="*70)
    print("DEMO 6: Session Management")
    print("="*70)
    
    # Create and save a session
    rag = TraumaKnotRAG()
    
    print(f"\n📝 New Session ID: {rag.session_id}")
    
    # Have a short conversation
    rag.generate_response("I'm feeling anxious about my future")
    rag.generate_response("What can help me feel more in control?")
    
    # Save
    session_file = "conversations/demo_session.json"
    rag.save_conversation(session_file)
    print(f"✅ Saved to: {session_file}")
    
    # Create new instance and load
    rag2 = TraumaKnotRAG()
    rag2.load_conversation(session_file)
    print(f"✅ Loaded session with {len(rag2.conversation_history)} messages")
    
    summary = rag2.get_conversation_summary()
    print(f"\n📊 Session Summary:")
    print(f"   Total Exchanges: {summary['total_exchanges']}")
    print(f"   Message Count: {summary['message_count']}")


def demo_visualize_cycle():
    """Demo 7: Visualize trauma cycle"""
    print("\n" + "="*70)
    print("DEMO 7: Trauma Cycle Visualization")
    print("="*70)
    
    try:
        import matplotlib.pyplot as plt
        import networkx as nx
        
        kb = TraumaKnotKB()
        cycles = kb.get_trauma_cycles()
        
        if not cycles:
            print("No cycles to visualize")
            return
        
        cycle = cycles[0]
        print(f"\n📊 Visualizing: {' → '.join(cycle)}")
        
        # Create visualization
        fig, ax = plt.subplots(figsize=(10, 6))
        subgraph = kb.G.subgraph(cycle)
        pos = nx.circular_layout(subgraph)
        
        # Draw nodes
        nx.draw_networkx_nodes(subgraph, pos, node_color='lightblue', 
                               node_size=2000, ax=ax)
        nx.draw_networkx_labels(subgraph, pos, font_size=8, ax=ax)
        
        # Draw edges
        edges = [(cycle[i], cycle[(i+1) % len(cycle)]) for i in range(len(cycle))]
        nx.draw_networkx_edges(subgraph, pos, edgelist=edges,
                               edge_color='red', arrows=True,
                               arrowsize=20, arrowstyle='->', width=2, ax=ax)
        
        # Edge labels
        edge_labels = {}
        for u, v in edges:
            if kb.G.has_edge(u, v):
                edge_labels[(u, v)] = f"{kb.G[u][v]['weight']}"
        
        nx.draw_networkx_edge_labels(subgraph, pos, edge_labels, font_size=8, ax=ax)
        
        ax.set_title(f"Trauma Cycle: {' → '.join(cycle)}", fontsize=14, fontweight='bold')
        ax.axis('off')
        plt.tight_layout()
        
        # Save
        import os
        os.makedirs("visualizations", exist_ok=True)
        filepath = "visualizations/demo_cycle.png"
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Visualization saved to: {filepath}")
    
    except ImportError:
        print("⚠️ Matplotlib not available for visualization")


def main():
    """Run all demos"""
    print("\n" + "="*70)
    print("🧠 TRAUMA KNOT RAG SYSTEM - DEMONSTRATION")
    print("="*70)
    
    try:
        # Check if API key is set
        if not os.getenv("OPENAI_API_KEY"):
            print("\n❌ OPENAI_API_KEY not set")
            print("Please create .env file with your API key")
            return
        
        print("\nRunning demonstrations...\n")
        
        # Run demos
        demo_basic_chat()
        demo_multi_turn_conversation()
        demo_knowledge_base_exploration()
        demo_context_retrieval()
        demo_trauma_cycle_analysis()
        demo_session_management()
        demo_visualize_cycle()
        
        print("\n" + "="*70)
        print("✅ All demonstrations completed!")
        print("="*70)
        print("\nNext steps:")
        print("1. Run the FastAPI server: uvicorn main:app --reload")
        print("2. Visit: http://localhost:8000/docs")
        print("3. Or use CLI: python cli.py")
        print()
    
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

