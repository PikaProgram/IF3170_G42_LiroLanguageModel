from kelasking import eff_dims, rotated_orientation
import random, math

AXES = ("x", "y", "z")

def _apply(cur, actions):
    s = cur.copy()
    for act in actions:
        if act[0] == "remove":
            s.remove_package(act[1])
        elif not s.place_package(act[1], act[3], act[2]):
            return None
    return s if s.is_valid() else None


def hello_neighbor(cur):
    ins = sorted(cur.inserted_pack, key=lambda p: p.id)
    outs = sorted(cur.remaining_pack, key=lambda p: p.id)
    d = cur.dimentions
    for i, a in enumerate(ins): 
        for b in ins[i + 1:]:
            s = _apply(cur, [("remove", a), ("remove", b),
                             ("place", a, cur.orientations[a.id], cur.coords[b.id]),
                             ("place", b, cur.orientations[b.id], cur.coords[a.id])])
            if s is not None:
                yield s
    for a in ins:
        for b in outs:
            s = _apply(cur, [("remove", a), ("place", b, cur.orientations[b.id], cur.coords[a.id])])
            if s is not None:
                yield s
    for p in ins:
        orientation = cur.orientations[p.id]
        eff = eff_dims(p.dimentions, orientation)
        c0 = cur.coords[p.id]
        for z in range(d["h"] - eff["z"] + 1):
            for y in range(d["l"] - eff["y"] + 1):
                for x in range(d["w"] - eff["x"] + 1):
                    if x == c0["x"] and y == c0["y"] and z == c0["z"]:
                        continue
                    s = _apply(cur, [("remove", p), ("place", p, orientation, {"x": x, "y": y, "z": z})])
                    if s is not None:
                        yield s
    for p in ins:
        c0 = cur.coords[p.id]
        for axis in AXES:
            orientation = rotated_orientation(cur.orientations[p.id], axis)
            eff = eff_dims(p.dimentions, orientation)
            if (c0["x"] + eff["x"] > d["w"] or c0["y"] + eff["y"] > d["l"]
                    or c0["z"] + eff["z"] > d["h"]):
                continue
            s = _apply(cur, [("remove", p), ("place", p, orientation, dict(c0))])
            if s is not None:
                yield s

def simulated_annealing(initial, temp=100.0, cooling_rate=0.995, minimum_temp=0.01):
    cur = initial
    history = [cur.objective()]
    probability_history = []
    stuck_history = []
    iterations = 0
    
    while temp > minimum_temp:
        successors = list(hello_neighbor(cur))
        if not successors:
            break
        curr_value = cur.objective()
        best_neighbor_value = max(s.objective() for s in successors)
            
        stuck_history.append(best_neighbor_value <= curr_value)

        succ = random.choice(successors)
        delta_e = succ.objective() - curr_value
        probability = math.exp(delta_e / temp)

        if delta_e > 0:
            cur = succ    
        else: 
            if random.random() < probability:
                cur = succ        

        history.append(cur.objective())
        probability_history.append(probability)
        temp, iterations = temp * cooling_rate, iterations + 1

    return cur, history, probability_history, stuck_history, iterations