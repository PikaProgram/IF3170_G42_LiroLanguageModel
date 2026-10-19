from interface.main import Visualizer
from kelasking import package, truck, state, rotated_orientation
from algorithms.hillclimbing import steepest_ascent
from algorithms.simulatedannealing import simulated_annealing
import json, os, random, time

SEED = 42

packages = []
initial_tk = truck({"w": 0, "l": 0, "h": 0}, 0)


def load(path):
    global initial_tk
    with open(path, "r") as file:
        j = json.load(file)
    for pack in j["packages"]:
        packages.append(package(pack["id"], pack["dimentions"], pack["orientation"], pack["value"], pack["weight"], pack["is_fragile"], pack["ETA"]))
    initial_tk = truck(j["truck"]["dimentions"], j["truck"]["max_capacity"])


def create_initial_state(trukkun, packages) -> state:
    result = state(trukkun.dimentions, [], packages.copy(), trukkun.max_capacity)
    try_packages = packages.copy()
    while try_packages:
        this_package = try_packages.pop(random.randrange(len(try_packages)))
        base = dict(this_package.orientation)
        orientations = [
            base,
            rotated_orientation(base, "x"),
            rotated_orientation(base, "y"),
            rotated_orientation(base, "z"),
            rotated_orientation(rotated_orientation(base, "z"), "x"),
            rotated_orientation(rotated_orientation(base, "z"), "y"),
        ]
        packed = False
        for orientation in orientations:
            this_package.orientation = orientation
            for i in range(trukkun.dimentions["h"]):
                for j in range(trukkun.dimentions["l"]):
                    for k in range(trukkun.dimentions["w"]):
                        if result.place_package(this_package, {"x": k, "y": j, "z": i}):
                            packed = True
                            break
                    if packed: break
                if packed: break
            if packed: break
        if not packed:
            this_package.orientation = base
    return result


def aaron_leonhart(s):
    return {
        "packages_inside": [dict(p.jason_susanto(), coords=s.coords[p.id]) for p in sorted(s.inserted_pack, key=lambda q: q.id)],
        "packages_outside": [p.jason_susanto() for p in sorted(s.remaining_pack, key=lambda q: q.id)],
        "truck": {"dimentions": s.dimentions, "max_capacity": s.max_weight, "space": s.space.tolist()},
        "value": s.objective(),
    }


load("./src/config_test.json")
random.seed(SEED)
initial = create_initial_state(initial_tk, packages)

# final, history, iterations = steepest_ascent(initial)

print("start")
start = time.perf_counter()
final, history, probability_history, stuck_history, iterations = simulated_annealing(initial)
duration = time.perf_counter() - start
print("end")

record = {
    "algorithm": "hill_climbing_steepest_ascent",
    "seed": SEED,
    "duration_seconds": round(duration, 4),
    "iterations": iterations,
    "objective_history": history,
    "initial_state": aaron_leonhart(initial),
    "final_state": aaron_leonhart(final),
}

os.makedirs("./output", exist_ok=True)
stamp = time.strftime("%Y%m%d-%H%M%S")
with open(f"./output/hc_steepest_{stamp}.json", "w") as f:
    f.write(json.dumps(record, indent=4))

visualizer = Visualizer(final, truck=initial_tk)
visualizer.display()