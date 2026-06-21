from trauma_knot_kb import TraumaKnotKB

kb = TraumaKnotKB()
print('Nodes:', len(kb.G.nodes()))

knots = kb.detect_trauma_knots(top_k=3)
print('Detected knots:', len(knots))
for cycle, score, edges in knots:
    print('Cycle:', cycle, 'Score:', score)
    weakest, all_edges = kb.find_break_point_for_knot(cycle)
    print('Weakest edge:', weakest)

# Compute K
K = kb.compute_K([k[0] for k in knots])
print('K for top knots:', K)

# Simulate activation
activation, path_tracker = kb.simulate_activation('Fear', steps=3, verbose=False)
print('Top activated nodes:', sorted(activation.items(), key=lambda x: -abs(x[1]))[:5])

# Test reinforcing then weakening
cycles_only = [k[0] for k in knots]
kb.reinforce(cycles_only, factor=1.2)
kb.weaken_targeted(cycles_only, factor=0.5)

print('Test complete')

