from kelasking import eff_dims, rotated_orientation

AXES = ("x", "y", "z")


def _apply(cur, actions):
    s = cur.copy()
    for act in actions:
        if act[0] == "remove":
            s.remove_package(act[1])
        elif not s.place_package(act[1], act[3], act[2]):
            return None
    return s if s.is_valid() else None


def neighbors(cur):
    ins = sorted(cur.inserted_pack, key=lambda p: p.id)
    outs = sorted(cur.remaining_pack, key=lambda p: p.id)
    d = cur.dimentions
    for i, a in enumerate(ins): 
        for b in ins[i + 1:]:
            s = _apply(cur, [("remove", a), ("remove", b),
                             ("place", a, a.orientation, cur.coords[b.id]),
                             ("place", b, b.orientation, cur.coords[a.id])])
            if s is not None:
                yield s
    for a in ins:
        for b in outs:
            s = _apply(cur, [("remove", a), ("place", b, b.orientation, cur.coords[a.id])])
            if s is not None:
                yield s
    for p in ins:
        eff = eff_dims(p.dimentions, p.orientation)
        c0 = cur.coords[p.id]
        for z in range(d["h"] - eff["z"] + 1):
            for y in range(d["l"] - eff["y"] + 1):
                for x in range(d["w"] - eff["x"] + 1):
                    if x == c0["x"] and y == c0["y"] and z == c0["z"]:
                        continue
                    s = _apply(cur, [("remove", p), ("place", p, p.orientation, {"x": x, "y": y, "z": z})])
                    if s is not None:
                        yield s
    for p in ins:
        c0 = cur.coords[p.id]
        for axis in AXES:
            orientation = rotated_orientation(p.orientation, axis)
            eff = eff_dims(p.dimentions, orientation)
            if (c0["x"] + eff["x"] > d["w"] or c0["y"] + eff["y"] > d["l"]
                    or c0["z"] + eff["z"] > d["h"]):
                continue
            s = _apply(cur, [("remove", p), ("place", p, orientation, dict(c0))])
            if s is not None:
                yield s


def steepest_ascent(initial):
    cur = initial
    history = [cur.objective()]
    iterations = 0
    while True:
        best, best_val = None, cur.objective()
        for s in neighbors(cur):
            v = s.objective()
            if v > best_val:
                best, best_val = s, v
        if best is None:
            return cur, history, iterations
        cur, iterations = best, iterations + 1
        history.append(best_val)
