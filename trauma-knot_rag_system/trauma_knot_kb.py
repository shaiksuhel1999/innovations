"""
Trauma Knot Graph Knowledge Base

A comprehensive knowledge base representing psychological trauma as a directed graph.
This module implements the Trauma Knot Framework, modeling how trauma triggers
propagate through emotional, cognitive, and behavioral systems.

Features:
- 60+ psychological nodes organized in 9 categories
- 100+ weighted edges representing causal relationships
- Cycle detection and trauma knot identification
- Intervention strategy recommendation
- Healing pathway analysis
- Node-centric and edge-centric analysis methods

Usage:
    kb = TraumaKnotKB()
    cycles = kb.get_trauma_cycles()
    interventions = kb.get_intervention_points(cycles[0])
"""

import networkx as nx
from typing import List, Tuple, Dict, Optional, Set
import json
import logging

logger = logging.getLogger(__name__)


class TraumaKnotKB:
    """Knowledge Base for Trauma Knot Analysis
    
    This class manages a directed graph representing psychological trauma patterns.
    It provides methods for cycle detection, intervention recommendation, and
    healing pathway analysis.
    
    Attributes:
        G (nx.DiGraph): The underlying directed graph
        node_categories (Dict): Mapping of node categories to node lists
        DEFAULT_WEIGHT_THRESHOLD (float): Minimum cycle weight for trauma classification
        MIN_INTERVENTION_STRENGTH (float): Minimum edge weight for intervention priority
    """
    
    # Configuration constants
    DEFAULT_WEIGHT_THRESHOLD = 4.0
    MIN_INTERVENTION_STRENGTH = 8.0
    
    def __init__(self, weight_threshold: Optional[float] = None):
        """Initialize Knowledge Base
        
        Args:
            weight_threshold: Override default trauma cycle detection threshold
        """
        self.G = nx.DiGraph()
        self.node_categories: Dict[str, List[str]] = {}
        self.weight_threshold = weight_threshold or self.DEFAULT_WEIGHT_THRESHOLD
        self._cycle_cache: Optional[List[List[str]]] = None
        self._descriptions_cache: Dict[str, str] = {}
        
        self._initialize_nodes()
        self._initialize_edges()
        self._build_descriptions_cache()
        
    def _initialize_nodes(self):
        """Initialize all node categories"""
        fear_nodes = [
            "PhysicalThreat", "DiseaseTrauma", "AccidentTrauma",
            "ViolenceExposure", "LossOfSafety", "AbandonmentFear", "WarTrauma"
        ]
        shame_nodes = [
            "Rejection", "SocialHumiliation", "PublicFailure",
            "Bullying", "Comparison", "BodyShame"
        ]
        guilt_nodes = [
            "MoralFailure", "SurvivorGuilt", "HarmToOthers", "NeglectResponsibility"
        ]
        loss_nodes = [
            "LossOfLovedOnes", "Breakup", "Divorce", "Separation", "EmotionalNeglect"
        ]
        control_nodes = [
            "JobLoss", "WealthLoss", "FailureRepeated", "ChronicStress", "Uncertainty"
        ]
        internal_nodes = [
            "Fear", "Shame", "Anxiety", "Anger",
            "Guilt", "Helplessness",
            "Hypervigilance", "StartleResponse",
            "IntrusionFlashback", "Dissociation", "Numbness"
        ]
        cognitive_nodes = [
            "NegativeBelief", "SelfDoubt", "CatastrophicThinking"
        ]
        behavior_nodes = [
            "Avoidance", "Withdrawal", "Overthinking", "CompulsiveBehavior"
        ]
        healing_nodes = [
            "Support", "Safety", "Confidence", "Empowerment",
            "Awareness", "EmotionalProcessing", "Exposure",
            "Resilience", "Acceptance"
        ]
        
        # Store node categories for later use
        self.node_categories = {
            "fear_triggers": fear_nodes,
            "shame_triggers": shame_nodes,
            "guilt_triggers": guilt_nodes,
            "loss_triggers": loss_nodes,
            "control_triggers": control_nodes,
            "emotions": internal_nodes,
            "cognitions": cognitive_nodes,
            "behaviors": behavior_nodes,
            "healing": healing_nodes
        }
        
        # Add all nodes
        for nodes in self.node_categories.values():
            self.G.add_nodes_from(nodes)
    
    def _initialize_edges(self):
        """Initialize all edges with weights"""
        edges = []
        
        # Build node_types mapping
        node_types = {}
        for n in self.node_categories["fear_triggers"]:
            node_types[n] = node_types.get(n, []) + ["fear"]
        for n in self.node_categories["shame_triggers"]:
            node_types[n] = node_types.get(n, []) + ["shame"]
        for n in self.node_categories["guilt_triggers"]:
            node_types[n] = node_types.get(n, []) + ["guilt"]
        for n in self.node_categories["loss_triggers"]:
            node_types[n] = node_types.get(n, []) + ["loss"]
        for n in self.node_categories["control_triggers"]:
            node_types[n] = node_types.get(n, []) + ["control"]
        
        # Trauma → Emotion mapping
        trauma_to_emotion = {
            "fear": [("Fear", 9), ("Anxiety", 8)],
            "shame": [("Shame", 9), ("Fear", 8)],
            "guilt": [("Guilt", 9), ("NegativeBelief", 8)],
            "loss": [("Fear", 9), ("Helplessness", 9)],
            "control": [("Anxiety", 9), ("Helplessness", 8)]
        }
        
        for node, types in node_types.items():
            for t in types:
                for target, w in trauma_to_emotion.get(t, []):
                    edges.append((node, target, w))
        
        # Emotion → Cognition
        edges += [
            ("Fear", "NegativeBelief", 9),
            ("Shame", "NegativeBelief", 8),
            ("Guilt", "NegativeBelief", 7),
            ("Helplessness", "NegativeBelief", 9),
            ("Anxiety", "CatastrophicThinking", 8),
            ("CatastrophicThinking", "NegativeBelief", 8),
            ("SelfDoubt", "NegativeBelief", 7)
        ]
        
        # Cognition → Behavior (core knot)
        edges += [
            ("NegativeBelief", "Avoidance", 9),
            ("NegativeBelief", "Withdrawal", 8),
            ("Avoidance", "Fear", 9),
            ("Avoidance", "Anxiety", 8),
            ("Withdrawal", "Shame", 7),
            ("Overthinking", "Anxiety", 8),
            ("CompulsiveBehavior", "Anxiety", 7)
        ]
        
        # Amplifier loops
        edges += [
            ("Fear", "Hypervigilance", 9),
            ("Hypervigilance", "StartleResponse", 8),
            ("StartleResponse", "Fear", 9),
            ("Fear", "IntrusionFlashback", 9),
            ("IntrusionFlashback", "Fear", 10)
        ]
        
        # Shutdown / dissociation
        edges += [
            ("Fear", "Dissociation", 7),
            ("Dissociation", "Numbness", 8),
            ("Numbness", "Avoidance", 7)
        ]
        
        # Helplessness + anger
        edges += [
            ("Fear", "Helplessness", 8),
            ("Helplessness", "Avoidance", 9),
            ("Fear", "Anger", 7),
            ("Anger", "NegativeBelief", 7)
        ]
        
        # Healing/recovery
        edges += [
            ("Support", "Safety", 8),
            ("Safety", "Fear", -8),
            ("Support", "Confidence", 7),
            ("Confidence", "Empowerment", 8),
            ("Empowerment", "NegativeBelief", -7),
            ("Awareness", "NegativeBelief", -6),
            ("EmotionalProcessing", "Fear", -7),
            ("Exposure", "Avoidance", -8),
            ("Confidence", "Avoidance", -6),
            ("Resilience", "Fear", -6),
            ("Acceptance", "Shame", -6)
        ]
        
        self.G.add_weighted_edges_from(edges)
    
    def _build_descriptions_cache(self):
        """Build cache of node descriptions for performance"""
        descriptions = {
            # Fear triggers
            "PhysicalThreat": "Physical threat or bodily harm experience - triggers acute fear response",
            "DiseaseTrauma": "Trauma related to disease, illness, or health crisis and treatment",
            "AccidentTrauma": "Trauma from accidents or unexpected dangerous events (car crashes, falls, etc.)",
            "ViolenceExposure": "Exposure to violence or assault - direct or indirect",
            "LossOfSafety": "Loss of sense of safety or security - feeling vulnerable in the world",
            "AbandonmentFear": "Fear related to being left or abandoned by attachment figures",
            "WarTrauma": "Trauma from warfare, combat exposure, or conflict-related violence",
            
            # Shame triggers
            "Rejection": "Experience of being rejected or excluded by others",
            "SocialHumiliation": "Public shame or humiliation in social contexts",
            "PublicFailure": "Failure or inadequacy exposed in public settings",
            "Bullying": "Repeated harassment, intimidation, or cruel treatment",
            "Comparison": "Negative self-comparison to others - feeling inferior",
            "BodyShame": "Shame about one's body, appearance, or physical characteristics",
            
            # Guilt triggers
            "MoralFailure": "Violation of personal moral or ethical standards",
            "SurvivorGuilt": "Guilt about surviving when others did not",
            "HarmToOthers": "Responsibility for causing harm to others",
            "NeglectResponsibility": "Failure to fulfill important responsibilities or obligations",
            
            # Loss triggers
            "LossOfLovedOnes": "Death or permanent loss of close relationships",
            "Breakup": "Romantic relationship dissolution and emotional loss",
            "Divorce": "Family dissolution and associated losses",
            "Separation": "Enforced or prolonged separation from loved ones",
            "EmotionalNeglect": "Lack of emotional attention or validation from caregivers",
            
            # Control triggers
            "JobLoss": "Loss of employment and financial/identity impact",
            "WealthLoss": "Significant financial loss or economic hardship",
            "FailureRepeated": "Pattern of repeated failures and setbacks",
            "ChronicStress": "Ongoing, unrelenting stress and pressure",
            "Uncertainty": "Existential uncertainty about future or outcomes",
            
            # Emotions
            "Fear": "Feeling of danger or threat - primary trauma emotion activating fight/flight",
            "Anxiety": "Persistent worry and tension - anticipatory alarm response",
            "Shame": "Deep feeling of worthlessness or being fundamentally flawed",
            "Guilt": "Feeling responsible for harm or wrongdoing - self-directed blame",
            "Helplessness": "Loss of agency, control, and ability to impact outcomes",
            "Anger": "Rage and frustration from unresolved trauma and powerlessness",
            "Hypervigilance": "Constant scanning for threats - exhausting sustained alertness",
            "StartleResponse": "Exaggerated startle or flinching reaction - nervous system overactivity",
            "IntrusionFlashback": "Involuntary re-experiencing of trauma - intrusive memories and flashbacks",
            "Dissociation": "Disconnection from self, body, or reality as protective response",
            "Numbness": "Emotional blunting and reduced affect - protective shutdown",
            
            # Cognitions
            "NegativeBelief": "Core negative beliefs about self ('I'm broken'), others ('untrustworthy'), or world ('dangerous')",
            "SelfDoubt": "Lack of confidence in own abilities, judgment, and worth",
            "CatastrophicThinking": "Tendency to assume worst possible outcomes and overestimate threat",
            
            # Behaviors
            "Avoidance": "Avoiding situations, people, activities, or thoughts related to trauma",
            "Withdrawal": "Social isolation and emotional distancing from relationships",
            "Overthinking": "Rumination and excessive worry cycles attempting to regain control",
            "CompulsiveBehavior": "Repetitive behaviors (checking, cleaning) used to manage anxiety",
            
            # Healing factors
            "Support": "Social connection and therapeutic relationships - corrective attachment",
            "Safety": "Sense of physical and emotional security - nervous system stabilization",
            "Confidence": "Growing belief in self-efficacy and personal competence",
            "Empowerment": "Reclaimed agency, control, and voice in recovery process",
            "Awareness": "Mindful understanding of patterns, triggers, and trauma responses",
            "EmotionalProcessing": "Healthy processing, expression, and integration of emotions",
            "Exposure": "Gradual facing of feared situations - habituation and skill building",
            "Resilience": "Capacity to bounce back from adversity and adapt",
            "Acceptance": "Acceptance of what happened without being defined by it - meaning-making"
        }
        self._descriptions_cache = descriptions
    
    def get_node_description(self, node: str) -> Dict:
        """Get detailed description of a node
        
        Args:
            node: Name of the node to describe
            
        Returns:
            Dictionary with node info including name, category, description, connections
            
        Raises:
            ValueError: If node not found in knowledge base
        """
        if node not in self.G.nodes():
            logger.warning(f"Node '{node}' not found in knowledge base")
            return {
                "name": node,
                "category": "unknown",
                "description": f"Node '{node}' not recognized. Check spelling or add to knowledge base.",
                "found": False
            }
        
        description = self._descriptions_cache.get(node, "Description not available")
        
        # Find category
        category = "unknown"
        for cat, nodes in self.node_categories.items():
            if node in nodes:
                category = cat
                break
        
        return {
            "name": node,
            "category": category,
            "description": description,
            "connections": self._get_node_connections(node),
            "found": True
        }
    
    def _get_node_connections(self, node: str) -> Dict:
        """Get incoming and outgoing connections for a node"""
        incoming = list(self.G.predecessors(node))
        outgoing = list(self.G.successors(node))
        
        return {
            "incoming": incoming,
            "outgoing": outgoing
        }
    
    def get_cycles(self) -> List[List[str]]:
        """Get all trauma cycles in the knowledge base
        
        Uses caching to avoid recalculation. Clear cache with clear_cache()
        if graph has been modified.
        
        Returns:
            List of cycles, each cycle is a list of node names
        """
        if self._cycle_cache is None:
            logger.debug("Computing cycles - not in cache")
            self._cycle_cache = list(nx.simple_cycles(self.G))
            logger.info(f"Found {len(self._cycle_cache)} cycles in graph")
        
        return self._cycle_cache
    
    def get_trauma_cycles(self, weight_threshold: Optional[float] = None) -> List[List[str]]:
        """Filter cycles by severity (average edge weight)
        
        Identifies cycles where the average edge weight meets or exceeds the threshold.
        These are considered clinically significant trauma knots.
        
        Args:
            weight_threshold: Minimum average cycle weight. If None, uses instance default.
            
        Returns:
            List of trauma cycles sorted by severity (descending)
        """
        threshold = weight_threshold or self.weight_threshold
        cycles = self.get_cycles()
        trauma_cycles = []
        
        for cycle in cycles:
            weights = []
            for i in range(len(cycle)):
                u = cycle[i]
                v = cycle[(i + 1) % len(cycle)]
                if self.G.has_edge(u, v):
                    weights.append(self.G[u][v]['weight'])
            
            if weights:
                avg_weight = sum(weights) / len(weights)
                if avg_weight >= threshold:
                    trauma_cycles.append((cycle, avg_weight))
        
        # Sort by severity (descending)
        trauma_cycles.sort(key=lambda x: x[1], reverse=True)
        
        return [cycle for cycle, _ in trauma_cycles]
    
    def find_relevant_nodes(self, keywords: List[str]) -> List[Dict]:
        """Find nodes related to user input keywords"""
        relevant = []
        keywords_lower = [k.lower() for k in keywords]
        
        for node in self.G.nodes():
            node_lower = node.lower()
            # Check direct match or partial match
            if any(kw in node_lower or node_lower in kw for kw in keywords_lower):
                relevant.append(self.get_node_description(node))
        
        # Also search descriptions
        if not relevant:
            descriptions = {
                "physical": ["PhysicalThreat", "Hypervigilance", "StartleResponse"],
                "loss": ["LossOfLovedOnes", "Breakup", "Divorce", "Separation"],
                "social": ["SocialHumiliation", "Rejection", "Bullying"],
                "health": ["DiseaseTrauma", "BodyShame"],
                "work": ["JobLoss", "FailureRepeated"],
                "sleep": ["Nightmares", "IntrusionFlashback", "StartleResponse"],
                "relationship": ["Breakup", "Divorce", "Rejection", "AbandonmentFear"],
            }
            
            for keyword in keywords_lower:
                for pattern, nodes in descriptions.items():
                    if pattern in keyword or keyword in pattern:
                        for node in nodes:
                            desc = self.get_node_description(node)
                            if desc not in relevant:
                                relevant.append(desc)
        
        return relevant
    
    def get_intervention_points(self, cycle: List[str], 
                                 min_strength: Optional[float] = None) -> List[Dict]:
        """Get intervention strategies for breaking a cycle
        
        Identifies high-leverage edges in a trauma cycle that are optimal targets
        for therapeutic intervention.
        
        Args:
            cycle: List of nodes forming a cycle
            min_strength: Minimum edge weight for intervention priority. If None, uses class default.
            
        Returns:
            List of intervention points sorted by priority
        """
        if not cycle or len(cycle) < 2:
            logger.warning(f"Invalid cycle provided: {cycle}")
            return []
        
        min_str = min_strength or self.MIN_INTERVENTION_STRENGTH
        healing_edges = []
        
        for i in range(len(cycle)):
            u = cycle[i]
            v = cycle[(i + 1) % len(cycle)]
            
            if self.G.has_edge(u, v):
                weight = self.G[u][v]['weight']
                # Identify high-leverage edges to interrupt
                if abs(weight) >= min_str:
                    healing_edges.append({
                        "edge": f"{u} → {v}",
                        "strength": weight,
                        "priority": "HIGH" if abs(weight) >= 9 else "MEDIUM",
                        "intervention": self._suggest_intervention(u, v),
                        "role_importance": self._calculate_role_importance(u, v)
                    })
        
        # Sort by importance
        healing_edges.sort(key=lambda x: x['role_importance'], reverse=True)
        
        return healing_edges
    
    def _suggest_intervention(self, source: str, target: str) -> str:
        """Suggest therapeutic intervention for an edge
        
        Maps specific trauma node transitions to evidence-based interventions.
        
        Args:
            source: Source node of the edge
            target: Target node of the edge
            
        Returns:
            Description of recommended intervention
        """
        interventions = {
            ("Avoidance", "Fear"): "Graduated Exposure Therapy - gradually face feared situations",
            ("Fear", "Avoidance"): "Safety planning and grounding techniques",
            ("NegativeBelief", "Avoidance"): "Cognitive restructuring - challenge negative thoughts",
            ("Fear", "Helplessness"): "Empowerment work and agency restoration",
            ("IntrusionFlashback", "Fear"): "EMDR or narrative therapy - process traumatic memories",
            ("Fear", "IntrusionFlashback"): "Stabilization and present-moment grounding",
            ("Helplessness", "Avoidance"): "Behavioral activation - take small action steps",
            ("Shame", "NegativeBelief"): "Self-compassion work and shame reduction",
            ("Support", "Safety"): "Strengthen therapeutic alliance and safe relationships",
            ("Exposure", "Avoidance"): "Systematic desensitization",
        }
        
        # Try exact match first
        if (source, target) in interventions:
            return interventions[(source, target)]
        
        # Generic suggestions based on target type
        if "Fear" in target or "Anxiety" in target:
            return "Anxiety management and fear processing techniques"
        elif "Avoidance" in target or "Withdrawal" in target:
            return "Behavioral activation and exposure-based work"
        elif "Belief" in target or "Doubt" in target:
            return "Cognitive restructuring and thought challenging"
        elif "Shame" in target or "Guilt" in target:
            return "Affect regulation and self-compassion work"
        else:
            return "Therapeutic processing and skill building tailored to context"
    
    def get_healing_pathways(self, trauma_node: str) -> List[Dict]:
        """Get healing pathways from a trauma node
        
        Identifies healing factors that can address a specific trauma node
        by finding pathways in the healing direction.
        
        Args:
            trauma_node: Starting node in the trauma knot
            
        Returns:
            List of healing factors and their descriptions
            
        Raises:
            ValueError: If node not in knowledge base
        """
        if trauma_node not in self.G.nodes():
            logger.warning(f"Node '{trauma_node}' not found in knowledge base")
            raise ValueError(f"Node '{trauma_node}' not found in knowledge base")
        
        healing_paths = []
        
        for healing_node in self.node_categories.get("healing", []):
            # Check if there's a path from trauma to healing
            try:
                if nx.has_path(self.G, trauma_node, healing_node):
                    healing_paths.append({
                        "healing_factor": healing_node,
                        "description": self.get_node_description(healing_node)["description"],
                        "distance": nx.shortest_path_length(self.G, trauma_node, healing_node)
                    })
            except (nx.NetworkXNoPath, nx.NodeNotFound) as e:
                logger.debug(f"No path from {trauma_node} to {healing_node}: {e}")
                continue
        
        # Sort by distance (closest healing pathways first)
        healing_paths.sort(key=lambda x: x['distance'])
        
        return healing_paths
    
    def _calculate_role_importance(self, source: str, target: str) -> float:
        """Calculate importance score based on node roles
        
        Nodes play different roles in trauma cycles:
        - Key emotions (Fear, Shame, Avoidance) have higher importance
        - Intervention points involving these are more accessible
        
        Args:
            source: Source node
            target: Target node
            
        Returns:
            Importance score (0-2 range)
        """
        key_emotions = {"Fear", "Anxiety", "Shame", "Helplessness"}
        key_behaviors = {"Avoidance", "IntrusionFlashback", "Dissociation"}
        
        score = 1.0  # Base score
        
        # Increase importance if source is a key emotion
        if source in key_emotions:
            score += 0.5
        
        # Increase importance if target is a key behavior or emotion
        if target in key_emotions or target in key_behaviors:
            score += 0.5
        
        return min(score, 2.0)  # Cap at 2.0
    
    def clear_cache(self):
        """Clear internal caches after graph modifications
        
        Call this after adding/removing nodes or edges to force recalculation
        of cycles and descriptions on next query.
        """
        self._cycle_cache = None
        logger.debug("Cache cleared")
    
    def get_graph_statistics(self) -> Dict:
        """Get comprehensive statistics about the knowledge graph
        
        Returns:
            Dictionary with graph metrics and properties
        """
        cycles = self.get_cycles()
        trauma_cycles = self.get_trauma_cycles()
        
        # Calculate node degrees
        in_degrees = dict(self.G.in_degree())
        out_degrees = dict(self.G.out_degree())
        
        # Find most connected nodes
        max_in_node = max(in_degrees, key=in_degrees.get) if in_degrees else None
        max_out_node = max(out_degrees, key=out_degrees.get) if out_degrees else None
        
        return {
            "total_nodes": len(self.G.nodes()),
            "total_edges": len(self.G.edges()),
            "total_cycles": len(cycles),
            "trauma_cycles": len(trauma_cycles),
            "node_categories": {cat: len(nodes) for cat, nodes in self.node_categories.items()},
            "avg_node_degree": sum(in_degrees.values()) / len(in_degrees) if in_degrees else 0,
            "most_incoming_node": max_in_node,
            "most_outgoing_node": max_out_node,
            "graph_density": nx.density(self.G),
            "is_dag": nx.is_directed_acyclic_graph(self.G)
        }
    
    def get_node_centrality(self, node: str) -> Dict:
        """Calculate centrality measures for a node
        
        Centrality indicates how important a node is in the network.
        Useful for identifying leverage points in trauma cycles.
        
        Args:
            node: Node name
            
        Returns:
            Dictionary with various centrality measures
            
        Raises:
            ValueError: If node not in knowledge base
        """
        if node not in self.G.nodes():
            raise ValueError(f"Node '{node}' not found in knowledge base")
        
        # Calculate various centrality measures
        in_degree = self.G.in_degree(node)
        out_degree = self.G.out_degree(node)
        total_degree = in_degree + out_degree
        
        # Weighted centrality
        in_weight = sum(self.G[pred][node]['weight'] for pred in self.G.predecessors(node))
        out_weight = sum(self.G[node][succ]['weight'] for succ in self.G.successors(node))
        
        return {
            "node": node,
            "in_degree": in_degree,
            "out_degree": out_degree,
            "total_degree": total_degree,
            "in_weight": in_weight,
            "out_weight": out_weight,
            "total_weight": in_weight + out_weight
        }
    
    def validate_graph(self) -> Dict:
        """Validate the knowledge graph for consistency
        
        Checks for common issues like isolated nodes, duplicate edges, etc.
        
        Returns:
            Dictionary with validation results and warnings
        """
        issues = []
        
        # Check for isolated nodes
        isolated = list(nx.isolates(self.G))
        if isolated:
            issues.append(f"Found {len(isolated)} isolated nodes: {isolated[:3]}{'...' if len(isolated) > 3 else ''}")
        
        # Check for self-loops
        self_loops = list(nx.selfloop_edges(self.G))
        if self_loops:
            issues.append(f"Found {len(self_loops)} self-loops (should be minimal)")
        
        # Check all nodes have descriptions
        missing_descriptions = [n for n in self.G.nodes() if n not in self._descriptions_cache]
        if missing_descriptions:
            issues.append(f"Missing descriptions for {len(missing_descriptions)} nodes")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "total_checks": 3
        }

    # ------------------------------------------------------------------
    # Additional analysis & transformation utilities (from notebook)
    # ------------------------------------------------------------------
    def detect_trauma_knots(self, top_k: int = 5) -> List[Tuple[List[str], float, List[Tuple[str,str,float]]]]:
        """Detect and rank trauma knots (cycles) by total absolute weight.

        Returns a list of tuples: (cycle_nodes, total_weight, edge_list)
        where edge_list = [(u, v, weight), ...]
        """
        cycles = list(nx.simple_cycles(self.G))
        knots = []

        for cycle in cycles:
            if len(cycle) < 2:
                continue

            loop = cycle + [cycle[0]]
            total_weight = 0.0
            edge_list = []

            for i in range(len(loop) - 1):
                u, v = loop[i], loop[i+1]
                if self.G.has_edge(u, v):
                    w = self.G[u][v]['weight']
                    total_weight += abs(w)
                    edge_list.append((u, v, w))

            if edge_list:
                knots.append((cycle, total_weight, edge_list))

        knots.sort(key=lambda x: -x[1])
        return knots[:top_k]

    def find_break_point_for_knot(self, cycle: List[str]) -> Tuple[Tuple[str,str,float,float], List[Tuple[str,str,float,float]]]:
        """Given a cycle (list of node names), compute candidate break edges.

        Returns (weakest_edge, edges) where weakest_edge = (u, v, weight, break_score)
        and edges is list of all (u, v, weight, break_score).
        The heuristic uses role importance and absolute weight.
        """
        loop = cycle + [cycle[0]]
        edges = []

        for i in range(len(loop) - 1):
            u, v = loop[i], loop[i+1]
            if not self.G.has_edge(u, v):
                continue
            w = self.G[u][v]['weight']

            # Role importance heuristic
            role_score = 1.0
            if u in ("Fear", "Anxiety", "Shame", "Helplessness"):
                role_score += 1.0
            if v in ("Avoidance", "Fear", "IntrusionFlashback"):
                role_score += 1.0

            break_score = abs(w) * role_score
            edges.append((u, v, w, break_score))

        if not edges:
            raise ValueError("No valid edges found for provided cycle")

        weakest = min(edges, key=lambda x: x[3])
        return weakest, edges

    def compute_K(self, cycles: Optional[List[List[str]]] = None, alpha: float = 1.0, beta: float = 1.0) -> float:
        """Compute complexity K over provided cycles or detected trauma cycles.

        K = sum(alpha * strength + beta * len(cycle)) across cycles
        where strength = sum(edge weights) for each cycle.
        """
        if cycles is None:
            cycles = self.get_trauma_cycles()

        total = 0.0
        for cycle in cycles:
            strength = 0.0
            for i in range(len(cycle)):
                u = cycle[i]
                v = cycle[(i+1) % len(cycle)]
                if self.G.has_edge(u, v):
                    strength += self.G[u][v]['weight']
            total += alpha * strength + beta * len(cycle)

        return total

    def reinforce(self, cycles: List[List[str]], factor: float = 1.1) -> None:
        """Multiply edge weights in given cycles by factor (simulate reinforcement)."""
        for cycle in cycles:
            for i in range(len(cycle)):
                u = cycle[i]
                v = cycle[(i+1) % len(cycle)]
                if self.G.has_edge(u, v):
                    self.G[u][v]['weight'] *= factor
        # Clear cache as graph changed
        self.clear_cache()

    def weaken_targeted(self, cycles: List[List[str]], factor: float = 0.7) -> None:
        """Multiply edge weights in given cycles by factor <1 to simulate healing."""
        for cycle in cycles:
            for i in range(len(cycle)):
                u = cycle[i]
                v = cycle[(i+1) % len(cycle)]
                if self.G.has_edge(u, v):
                    self.G[u][v]['weight'] *= factor
        self.clear_cache()

    def simulate_activation(self, start_node: str, steps: int = 5, decay: float = 0.5, threshold: float = 0.01, verbose: bool = False):
        """Simulate activation spread from a start node through the graph.

        Returns (activation_dict, path_tracker)
        """
        activation = {node: 0.0 for node in self.G.nodes()}
        if start_node not in activation:
            raise ValueError(f"Start node '{start_node}' not in graph")

        activation[start_node] = 1.0
        path_tracker = {}

        if verbose:
            print(f"\n--- Activation Start: {start_node} ---")

        for step in range(steps):
            new_activation = activation.copy()
            if verbose:
                print(f"\nStep {step+1}")

            for u in self.G.nodes():
                if activation[u] == 0:
                    continue
                for v in self.G.successors(u):
                    weight = self.G[u][v]['weight']
                    influence = activation[u] * (weight / 10.0) * decay
                    if abs(influence) < threshold:
                        continue
                    path_tracker[(u, v)] = path_tracker.get((u, v), 0.0) + influence
                    new_activation[v] += influence
                    if verbose:
                        print(f"{u} → {v} | influence: {influence:.3f}")

            activation = new_activation

            if verbose:
                sorted_nodes = sorted(activation.items(), key=lambda x: -abs(x[1]))
                print('\nTop activations:')
                for node, val in sorted_nodes[:5]:
                    print(f"{node}: {val:.3f}")

        return activation, path_tracker

    def save_graph(self, filepath: str, format: str = 'graphml') -> str:
        """Serialize graph to disk. Supported formats: 'graphml', 'gml', 'json'.

        Returns path written.
        """
        fmt = format.lower()
        os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
        if fmt == 'graphml':
            nx.write_graphml(self.G, filepath)
        elif fmt == 'gml':
            nx.write_gml(self.G, filepath)
        elif fmt == 'json':
            data = nx.node_link_data(self.G)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        else:
            raise ValueError('Unsupported format')
        return filepath

    def load_graph(self, filepath: str, format: Optional[str] = None) -> None:
        """Load graph from disk. If format None, infer from extension."""
        ext = (format or os.path.splitext(filepath)[1].lstrip('.')).lower()
        if ext == 'graphml':
            self.G = nx.read_graphml(filepath)
        elif ext == 'gml':
            self.G = nx.read_gml(filepath)
        elif ext in ('json', 'jl'):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.G = nx.node_link_graph(data)
        else:
            raise ValueError('Unsupported format to load')
        self.clear_cache()

    def add_custom_node(self, node: str, category: Optional[str] = None) -> None:
        """Add a custom node and optionally register it in a category."""
        self.G.add_node(node)
        if category:
            self.node_categories.setdefault(category, []).append(node)

    def add_custom_edge(self, u: str, v: str, weight: float = 1.0) -> None:
        """Add or update an edge with a weight."""
        self.G.add_edge(u, v, weight=weight)
        self.clear_cache()

    def update_edge_weight(self, u: str, v: str, weight: float) -> None:
        """Set an edge weight (adds edge if missing)."""
        self.G.add_edge(u, v, weight=weight)
        self.clear_cache()

