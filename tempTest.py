from streamer.relations import classify_relation, compute_distance

# Object directly in front, 4m away
r = classify_relation(4, 0, compute_distance((4, 0)))
print('Front close:', r)

# Object to the left, 20m away
r = classify_relation(0, 20, compute_distance((0, 20)))
print('Left far:', r)

# Object behind, 8m away
r = classify_relation(-8, 0, compute_distance((-8, 0)))
print('Behind near:', r)

# Object too far, 50m away
r = classify_relation(50, 0, compute_distance((50, 0)))
print('Too far:', r)