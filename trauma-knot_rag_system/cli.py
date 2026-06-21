"""
CLI Interface for Trauma Knot RAG System
Allows direct command-line interaction without FastAPI server
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from rag_system import TraumaKnotRAG
from trauma_knot_kb import TraumaKnotKB


class TraumaKnotCLI:
    """Command-line interface for Trauma Knot RAG"""
    
    def __init__(self):
        """Initialize CLI"""
        try:
            self.rag = TraumaKnotRAG()
            self.kb = TraumaKnotKB()
            self.session_file = None
        except ValueError as e:
            print(f"❌ Error: {e}")
            print("Please set OPENAI_API_KEY environment variable or in .env file")
            sys.exit(1)
    
    def print_header(self):
        """Print welcome header"""
        print("\n" + "="*70)
        print("🧠 TRAUMA KNOT RAG SYSTEM - CLI Interface")
        print("="*70)
        print("AI-powered analysis and suggestions based on Trauma Knot Framework")
        print("Type 'help' for commands, 'quit' to exit\n")
    
    def print_help(self):
        """Print help information"""
        help_text = """
📋 AVAILABLE COMMANDS:

Interactive Chat:
  chat <message>       - Chat with AI about your trauma/problems
  continue             - Continue previous conversation
  save <filename>      - Save current session
  load <filename>      - Load previous session
  history              - Show conversation history

Knowledge Base:
  cycles               - Show all trauma cycles
  nodes                - Show all psychological nodes
  interventions        - Show intervention strategies
  node <name>          - Get details about specific node

Visualization:
  visualize <cycle>    - Visualize a trauma cycle (e.g., "visualize Fear Avoidance NegativeBelief")

System:
  clear                - Clear conversation history
  info                 - Show system information
  help                 - Show this help message
  quit                 - Exit the program

💡 TIPS:
  - Be specific when describing your experiences
  - Use multiple messages for deeper exploration
  - Save important sessions for later reference
  - Type "chat " followed by your problem to start
        """
        print(help_text)
    
    def show_cycles(self):
        """Display all trauma cycles"""
        cycles = self.kb.get_trauma_cycles()
        
        if not cycles:
            print("ℹ️ No trauma cycles found")
            return
        
        print(f"\n🔥 {len(cycles)} Trauma Cycles Identified:\n")
        for i, cycle in enumerate(cycles, 1):
            print(f"{i}. {' → '.join(cycle)}")
        print()
    
    def show_nodes(self):
        """Display all nodes by category"""
        print("\n📊 PSYCHOLOGICAL NODES BY CATEGORY:\n")
        
        for category, nodes in self.kb.node_categories.items():
            category_name = category.replace("_", " ").title()
            print(f"\n{category_name}:")
            for node in nodes:
                print(f"  • {node}")
        print()
    
    def show_node_details(self, node_name: str):
        """Show details about a specific node"""
        node_info = self.kb.get_node_description(node_name)
        
        if not node_info or "description" not in node_info:
            print(f"❌ Node '{node_name}' not found")
            return
        
        print(f"\n📌 NODE DETAILS: {node_info['name']}")
        print(f"Category: {node_info['category']}")
        print(f"Description: {node_info['description']}")
        
        if "connections" in node_info:
            connections = node_info["connections"]
            if connections.get("incoming"):
                print(f"Incoming from: {', '.join(connections['incoming'][:3])}")
            if connections.get("outgoing"):
                print(f"Leading to: {', '.join(connections['outgoing'][:3])}")
        print()
    
    def show_interventions(self):
        """Show intervention strategies"""
        trauma_cycles = self.kb.get_trauma_cycles()
        
        print("\n🔧 INTERVENTION STRATEGIES:\n")
        
        for i, cycle in enumerate(trauma_cycles[:3], 1):
            print(f"For Cycle {i}: {' → '.join(cycle)}")
            interventions = self.kb.get_intervention_points(cycle)
            for intervention in interventions[:3]:
                print(f"  • {intervention['edge']}")
                print(f"    Strategy: {intervention['intervention']}")
            print()
    
    def visualize_cycle(self, cycle_str: str):
        """Visualize a specific cycle"""
        try:
            cycle = cycle_str.split()
            if len(cycle) < 2:
                print("❌ Invalid cycle. Example: visualize Fear Avoidance NegativeBelief")
                return
            
            print(f"\n📊 Generating visualization for: {' → '.join(cycle)}...")
            
            import matplotlib.pyplot as plt
            import networkx as nx
            
            # Create visualization
            fig, ax = plt.subplots(figsize=(10, 6))
            subgraph = self.kb.G.subgraph(cycle)
            pos = nx.circular_layout(subgraph)
            
            # Draw
            nx.draw_networkx_nodes(subgraph, pos, node_color='lightblue', node_size=2000, ax=ax)
            nx.draw_networkx_labels(subgraph, pos, font_size=8, ax=ax)
            
            edges = [(cycle[i], cycle[(i+1) % len(cycle)]) for i in range(len(cycle))]
            nx.draw_networkx_edges(subgraph, pos, edgelist=edges,
                                   edge_color='red', arrows=True,
                                   arrowsize=20, arrowstyle='->', width=2, ax=ax)
            
            edge_labels = {}
            for u, v in edges:
                if self.kb.G.has_edge(u, v):
                    edge_labels[(u, v)] = f"{self.kb.G[u][v]['weight']}"
            
            nx.draw_networkx_edge_labels(subgraph, pos, edge_labels, font_size=8, ax=ax)
            
            ax.set_title(f"Trauma Cycle: {' → '.join(cycle)}", fontsize=14, fontweight='bold')
            ax.axis('off')
            plt.tight_layout()
            
            # Save
            viz_dir = Path("visualizations")
            viz_dir.mkdir(exist_ok=True)
            viz_path = viz_dir / f"cycle_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(viz_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            print(f"✅ Visualization saved to: {viz_path}\n")
        
        except Exception as e:
            print(f"❌ Error creating visualization: {e}\n")
    
    def process_chat(self, message: str):
        """Process chat message"""
        if not message.strip():
            return
        
        print("\n⏳ Analyzing...")
        
        try:
            result = self.rag.generate_response(message)
            
            print("\n" + "="*70)
            print("🤖 AI RESPONSE:")
            print("="*70)
            print(result["response"])
            
            # Show context
            if result.get("context"):
                context = result["context"]
                
                if context.get("relevant_nodes"):
                    print("\n📍 RELEVANT NODES:")
                    for node in context["relevant_nodes"][:3]:
                        print(f"  • {node['name']}: {node['description']}")
                
                if context.get("trauma_cycles"):
                    print("\n🔥 IDENTIFIED CYCLES:")
                    for cycle in context["trauma_cycles"][:2]:
                        print(f"  • {' → '.join(cycle)}")
                
                if context.get("intervention_points"):
                    print("\n🔧 INTERVENTION POINTS:")
                    for point in context["intervention_points"][:2]:
                        print(f"  • {point['edge']}: {point['intervention']}")
            
            print("\n" + "="*70 + "\n")
        
        except Exception as e:
            print(f"❌ Error: {e}\n")
    
    def save_session(self, filename: Optional[str] = None):
        """Save current session"""
        if not filename:
            filename = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = Path("conversations") / filename
        try:
            self.rag.save_conversation(str(filepath))
            print(f"✅ Session saved to: {filepath}\n")
            self.session_file = str(filepath)
        except Exception as e:
            print(f"❌ Error saving session: {e}\n")
    
    def load_session(self, filename: str):
        """Load previous session"""
        filepath = Path("conversations") / filename
        
        if not filepath.exists():
            print(f"❌ Session file not found: {filepath}")
            print("Available sessions:")
            conv_dir = Path("conversations")
            if conv_dir.exists():
                for f in conv_dir.glob("*.json"):
                    print(f"  • {f.name}")
            print()
            return
        
        try:
            self.rag.load_conversation(str(filepath))
            print(f"✅ Session loaded from: {filepath}")
            print(f"Messages: {len(self.rag.conversation_history)}\n")
            self.session_file = str(filepath)
        except Exception as e:
            print(f"❌ Error loading session: {e}\n")
    
    def show_history(self):
        """Show conversation history"""
        if not self.rag.conversation_history:
            print("ℹ️ No conversation history yet\n")
            return
        
        print("\n📜 CONVERSATION HISTORY:\n")
        for i, msg in enumerate(self.rag.conversation_history, 1):
            role = "👤 USER" if msg["role"] == "user" else "🤖 AI"
            content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
            print(f"{i}. {role}: {content}")
        print()
    
    def show_info(self):
        """Show system information"""
        print("\n📊 SYSTEM INFORMATION:")
        print(f"Total Nodes: {len(self.kb.G.nodes())}")
        print(f"Total Edges: {len(self.kb.G.edges())}")
        print(f"Trauma Cycles: {len(self.kb.get_trauma_cycles())}")
        print(f"Conversation Messages: {len(self.rag.conversation_history)}")
        print(f"Session ID: {self.rag.session_id}")
        if self.session_file:
            print(f"Current Session File: {self.session_file}")
        print()
    
    def run(self):
        """Main CLI loop"""
        self.print_header()
        
        while True:
            try:
                user_input = input("trauma-knot> ").strip()
                
                if not user_input:
                    continue
                
                # Parse command
                parts = user_input.split(maxsplit=1)
                command = parts[0].lower()
                args = parts[1] if len(parts) > 1 else ""
                
                if command == "quit":
                    print("\n👋 Goodbye! Stay strong. 💪\n")
                    break
                
                elif command == "help":
                    self.print_help()
                
                elif command == "chat":
                    if not args:
                        print("Usage: chat <your message>")
                    else:
                        self.process_chat(args)
                
                elif command == "continue":
                    message = input("Your message: ").strip()
                    if message:
                        self.process_chat(message)
                
                elif command == "history":
                    self.show_history()
                
                elif command == "save":
                    self.save_session(args if args else None)
                
                elif command == "load":
                    if not args:
                        print("Usage: load <filename>")
                    else:
                        self.load_session(args)
                
                elif command == "clear":
                    self.rag.reset_conversation()
                    print("✅ Conversation cleared\n")
                
                elif command == "cycles":
                    self.show_cycles()
                
                elif command == "nodes":
                    self.show_nodes()
                
                elif command == "node":
                    if not args:
                        print("Usage: node <node_name>")
                    else:
                        self.show_node_details(args)
                
                elif command == "interventions":
                    self.show_interventions()
                
                elif command == "visualize":
                    if not args:
                        print("Usage: visualize <cycle> (e.g., visualize Fear Avoidance NegativeBelief)")
                    else:
                        self.visualize_cycle(args)
                
                elif command == "info":
                    self.show_info()
                
                else:
                    print(f"❌ Unknown command: {command}")
                    print("Type 'help' for available commands\n")
            
            except KeyboardInterrupt:
                print("\n\n👋 Session interrupted. Goodbye!\n")
                break
            except Exception as e:
                print(f"❌ Error: {e}\n")


def main():
    """Entry point"""
    cli = TraumaKnotCLI()
    cli.run()


if __name__ == "__main__":
    main()

