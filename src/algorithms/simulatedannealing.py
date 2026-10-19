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
    if not ins:
        return None

    d = cur.dimentions
    actions = ["move", "rotate"]
    if len(ins) >= 2:
        actions.append("swap_inside")
    if outs:
        actions.append("swap_outside")

    for _ in range(100):
        action = random.choice(actions)

        if action == "swap_inside":
            a, b = random.sample(ins, 2)
            candidate = _apply(cur, [
                ("remove", a), ("remove", b),
                ("place", a, cur.orientations[a.id], cur.coords[b.id]),
                ("place", b, cur.orientations[b.id], cur.coords[a.id]),
            ])
        elif action == "swap_outside":
            a = random.choice(ins)
            b = random.choice(outs)
            candidate = _apply(cur, [
                ("remove", a),
                ("place", b, cur.orientations[b.id], cur.coords[a.id]),
            ])
        elif action == "move":
            p = random.choice(ins)
            orientation = cur.orientations[p.id]
            eff = eff_dims(p.dimentions, orientation)
            c0 = {
                "x": random.randrange(d["w"] - eff["x"] + 1),
                "y": random.randrange(d["l"] - eff["y"] + 1),
                "z": random.randrange(d["h"] - eff["z"] + 1),
            }
            if c0 == cur.coords[p.id]:
                continue
            candidate = _apply(cur, [
                ("remove", p),
                ("place", p, orientation, c0),
            ])
        else:
            p = random.choice(ins)
            axis = random.choice(AXES)
            orientation = rotated_orientation(cur.orientations[p.id], axis)
            c0 = cur.coords[p.id]
            eff = eff_dims(p.dimentions, orientation)
            if (c0["x"] + eff["x"] > d["w"]
                    or c0["y"] + eff["y"] > d["l"]
                    or c0["z"] + eff["z"] > d["h"]):
                continue
            candidate = _apply(cur, [
                ("remove", p),
                ("place", p, orientation, dict(c0)),
            ])

        if candidate is not None:
            return candidate

    return None


def simulated_annealing(initial):
    cur = initial
    temp = 100.0
    cooling_rate = 0.995
    minimum_temp = 0.01
    history = [cur.objective()]
    probability_history = []
    stuck_history = []
    iterations = 0
    
    while temp > minimum_temp:
        succ = hello_neighbor(cur)
        if succ is None:
            break
        curr_value = cur.objective()
        stuck_history.append(succ.objective() <= curr_value)
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