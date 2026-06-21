# Trauma Knot Breaker v2

A graph-based psychological simulation framework for understanding, analyzing, and therapeutically intervening in trauma cycles and emotional knots.

## Overview

This project models trauma as interconnected cycles in a directed graph, where:
- **Nodes** represent psychological states (trauma triggers, emotions, cognitions, behaviors, healing factors)
- **Edges** represent causal relationships with weighted strength
- **Cycles** represent trauma knots—self-reinforcing loops of emotional distress

The framework provides tools to:
- Detect and analyze trauma cycles
- Simulate emotional activation spreading through psychological networks
- Identify intervention points (weakest links in trauma cycles)
- Model trauma reinforcement and healing processes

## Key Concepts

### Node Categories

1. **Trauma Triggers** (Primary stressors)
   - Fear nodes: Physical threats, accidents, violence exposure
   - Shame nodes: Rejection, humiliation, bullying, body shame
   - Guilt nodes: Moral failure, survivor guilt, neglect
   - Loss nodes: Death, breakup, separation, emotional neglect
   - Control nodes: Job loss, financial loss, chronic stress

2. **Emotional States**
   - Fear, Anxiety, Shame, Guilt, Anger, Helplessness
   - Hypervigilance, Startle Response
   - Intrusion/Flashback, Dissociation, Numbness

3. **Cognitive Patterns**
   - Negative Beliefs
   - Self-Doubt
   - Catastrophic Thinking

4. **Behavioral Responses**
   - Avoidance, Withdrawal, Overthinking, Compulsive Behavior

5. **Healing/Recovery Factors**
   - Support, Safety, Confidence, Empowerment
   - Awareness, Emotional Processing, Exposure
   - Resilience, Acceptance

### Core Mechanisms

#### Trauma-to-Emotion Mapping
Trauma triggers activate specific emotional states. For example:
- Fear triggers → Fear (9), Anxiety (8)
- Shame triggers → Shame (9), Fear (8)

#### The Trauma Knot Loop
The central reinforcing cycle in the model:
```
NegativeBelief → Avoidance → Fear → NegativeBelief
```

This creates a self-perpetuating loop where avoidance prevents exposure to feared situations, maintaining the negative belief.

#### Amplifier Loops
Additional reinforcing cycles that intensify trauma:
```
Fear → Hypervigilance → Startle Response → Fear
Fear → Intrusion/Flashback → Fear (strongest, weight=10)
```

#### Shutdown/Dissociation Path
Protective response under extreme fear:
```
Fear → Dissociation → Numbness → Avoidance
```

## Main Functions

### Graph Analysis

**`get_cycles(G)`**
- Returns all simple cycles in the directed graph
- Essential for identifying feedback loops

**`detect_trauma_cycles(G, cycles, weight_threshold=4)`**
- Filters cycles by average edge weight
- Identifies clinically significant trauma cycles
- Returns only cycles above the severity threshold

**`compute_K(G, cycles, alpha=1, beta=1)`**
- Computes overall trauma complexity
- `alpha`: weight of cycle strength
- `beta`: weight of cycle length
- K increases with stronger and longer cycles

### Simulation & Analysis

**`simulate_activation(G, start_node, steps=5, decay=0.5, threshold=0.01)`**
- Simulates emotional activation spreading from a trigger
- Tracks activation through the network over multiple time steps
- Returns: activation levels and influence path tracking
- Parameters:
  - `decay`: Reduces activation at each step (prevents infinite spread)
  - `threshold`: Minimum activation required to propagate
- Useful for understanding cascade effects of trauma triggers

**`detect_trauma_knots(G, top_k=5)`**
- Identifies strongest trauma cycles (knots)
- Returns top k cycles sorted by severity
- Each knot includes cycle path, severity score, and edges
- Helps prioritize intervention targets

**`find_break_point_for_knot(G, cycle)`**
- Identifies the weakest edge in a trauma cycle
- Scores edges by: `|weight| × role_importance`
- Prioritizes breaking edges involving key emotions:
  - Trigger emotions: Fear, Anxiety, Shame, Helplessness
  - Maintenance emotions: Avoidance, Fear, Intrusion/Flashback
- Returns: weakest edge and all edges in the cycle with scores

### Therapeutic Interventions

**`reinforce(G, cycles, factor=1.1)`**
- Increases edge weights in trauma cycles
- Models trauma worsening or unresolved triggers
- `factor > 1` strengthens the cycle

**`weaken_targeted(G, trauma_cycles, factor=0.7)`**
- Reduces edge weights in trauma cycles
- Models therapeutic intervention and healing
- `factor < 1` weakens the cycle
- More targeted than general weakening

### Visualization

**`draw_graph(G, title)`**
- Visualizes the complete graph structure
- Shows nodes and weighted edges
- Displays edge weights on connections

**`plot_node_activation(activation, top_n=10)`**
- Bar chart of top activated emotional nodes
- Shows which nodes are most strongly triggered

**`plot_edge_influence(path_tracker, top_n=10)`**
- Bar chart of most influential transmission paths
- Shows which edges carry the most activation

**`plot_break_point(cycle, weakest_edge, all_edges)`**
- Highlights the weakest link in a trauma cycle
- Visualizes break scores for all edges in the cycle
- Helps identify optimal intervention point

## Simulation Workflow

The notebook follows a three-phase therapeutic simulation:

### Phase 1: Initial Assessment
```
INITIAL STATE
├── Detect trauma cycles
├── Compute initial complexity (K)
├── Simulate activation spreading
└── Identify trauma knots and break points
```

### Phase 2: Trauma Reinforcement (Worsening)
```
REINFORCEMENT
├── Strengthen trauma cycle edges (factor=1.2)
├── Recompute complexity (K increases)
├── Show impact on activation patterns
└── Re-identify top knots
```

### Phase 3: Therapeutic Intervention (Healing)
```
HEALING/WEAKENING
├── Apply targeted weakening (factor=0.5)
├── Recompute complexity (K decreases)
├── Show activation patterns improve
└── Verify knots become less severe
```

## Key Insights

1. **Avoidance Paradox**: The more someone avoids feared situations (Avoidance→Fear), the stronger the fear becomes, creating the central trauma knot

2. **Healing Reversal**: Healing factors have negative weights
   - `Safety → Fear: -8` (safety reduces fear)
   - `Exposure → Avoidance: -8` (facing fears breaks avoidance cycle)

3. **Break Point Strategy**: The weakest edge in a trauma cycle is the optimal intervention point, often involving key emotions like Avoidance or Fear

4. **Role-Based Scoring**: Edges involving high-impact emotions (Fear, Shame, Avoidance) have higher break scores, making them easier to address therapeutically

## Dependencies

- `networkx`: Graph analysis and cycle detection
- `matplotlib`: Visualization and plotting

## Usage

Run the notebook cells sequentially to:
1. Initialize the trauma network
2. Analyze initial trauma cycles
3. Simulate activation cascades
4. Model reinforcement/worsening
5. Apply targeted healing interventions
6. Compare complexity metrics across phases

## Therapeutic Applications

This framework can inform:
- **Treatment Planning**: Identifying leverage points (break points) for intervention
- **Patient Education**: Visualizing how trauma cycles self-perpetuate
- **Progress Tracking**: Monitoring complexity metrics (K) as treatment progresses
- **Mechanism Understanding**: Clarifying how different interventions break specific cycles
- **Personalization**: Adapting the model to individual trauma patterns

## Limitations & Future Work

- Current model is deterministic; stochastic elements could add realism
- Human psychology is far more complex; this is a simplified abstraction
- Weights are illustrative and would need validation through clinical data
- Missing some important constructs (e.g., dissociation severity, polyvagal states)
- Could integrate with therapeutic modalities (CBT, EMDR, CPT, somatic work)

## References

Concepts inspired by:
- Trauma-focused Cognitive Behavioral Therapy (TF-CBT)
- Trauma Informed Care principles
- Complex PTSD models
- Graph-based psychological network analysis

