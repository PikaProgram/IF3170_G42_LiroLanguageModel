import random

from algorithms.steepestascent import neighbors

def hill_climbing_sideways(initial, max_sideways=100):
    cur = initial
    history = [cur.objective()]
    average_history = [cur.objective()]
    iterations = sideways = 0
    while True:
        best, best_val, ties = None, cur.objective(), []
        values = []
        for s in neighbors(cur):
            v = s.objective()
            values.append(v)
            if v > best_val:
                best, best_val, ties = s, v, []
            elif v == best_val:
                ties.append(s)
        if best is None:
            if not ties or sideways >= max_sideways:
                break
            best = random.choice(ties)
            sideways += 1
        else:
            sideways = 0
        cur, iterations = best, iterations + 1
        history.append(cur.objective())
        average_history.append(
            sum(values) / len(values) if values else cur.objective())
    return cur, history, average_history, iterations
