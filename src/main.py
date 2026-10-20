import json
import os
import random
import time

import streamlit as st

from interface.main import Visualizer
from interface.components.box import TruckGraph
from interface.components.charts import AcceptanceProbabilityGraph, ObjectiveGraph
from interface.components.sidebar import ALGORITHMS, init_state, render_sidebar, truck_fields
from kelasking import package, truck, state, rotated_orientation
from algorithms.steepestascent import steepest_ascent
from algorithms.simulatedannealing import simulated_annealing
from algorithms.sidewaysmove import hill_climbing_sideways
from algorithms.geneticalgorithm import genetic_algorithm

SEED = 42

st.set_page_config(layout="wide")


def create_initial_state(trukkun, packages) -> state:
    result = state(trukkun.dimentions, [],
                   packages.copy(), trukkun.max_capacity)
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
                    if packed:
                        break
                if packed:
                    break
            if packed:
                break
        if not packed:
            this_package.orientation = base
    return result


def aaron_leonhart(s):
    return {
        "packages_inside": [
            dict(p.jason_susanto(),
                 orientation=s.orientations[p.id], coords=s.coords[p.id])
            for p in sorted(s.inserted_pack, key=lambda q: q.id)
        ],
        "packages_outside": [p.jason_susanto() for p in sorted(s.remaining_pack, key=lambda q: q.id)],
        "truck": {"dimentions": s.dimentions, "max_capacity": s.max_weight, "space": s.space.tolist()},
        "value": s.objective(),
    }


def build_initial(tk, packages_raw) -> state:
    random.seed(SEED)
    objs = [package(p["id"], dict(p["dimentions"]), dict(p["orientation"]),
                    p["value"], p["weight"], p["is_fragile"], p["ETA"])
            for p in packages_raw]
    return create_initial_state(tk, objs)


def run_algorithm(req):
    fields = truck_fields()
    tk = truck({k: fields[k] for k in ("w", "l", "h")}, fields["max_capacity"])
    with st.spinner("Running algorithm..."):
        initial = build_initial(tk, st.session_state["packages"])
        started = time.perf_counter()
        probability_history = None
        stuck_history = None
        if req["algorithm"] == "hc":
            final, history, average_history, iterations = steepest_ascent(initial)
        elif req["algorithm"] == "hc_sideways":
            final, history, average_history, iterations = hill_climbing_sideways(
                initial, **req["params"])
        elif req["algorithm"] == "sa":
            final, history, average_history, probability_history, stuck_history, iterations = \
                simulated_annealing(initial, **req["params"])
        else:
            final, history, average_history, _, iterations = genetic_algorithm(
                initial, **req["params"])
        duration = time.perf_counter() - started

    meta = ALGORITHMS[req["algorithm"]]
    record = {
        "algorithm": meta["record"],
        "params": req["params"],
        "seed": SEED,
        "duration_seconds": round(duration, 4),
        "iterations": iterations,
        "objective_history": history,
        "average_objective_history": average_history,
        "initial_state": aaron_leonhart(initial),
        "final_state": aaron_leonhart(final),
    }
    if probability_history is not None:
        record["probability_history"] = probability_history
    if stuck_history is not None:
        record["stuck_history"] = stuck_history
    os.makedirs("./output", exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    with open(f"./output/{meta['record']}_{stamp}.json", "w") as f:
        f.write(json.dumps(record, indent=4))

    st.session_state["result"] = {
        "label": meta["label"],
        "params": req["params"],
        "final": final,
        "objective": final.objective(),
        "iterations": iterations,
        "duration": duration,
    }
    st.session_state["fig"] = TruckGraph(final, tk, "Final state").draw()
    st.session_state["initial_fig"] = TruckGraph(initial, tk, "Initial state").draw()
    charts = [ObjectiveGraph(history, average_history).draw()]
    if probability_history is not None:
        charts.append(AcceptanceProbabilityGraph(probability_history).draw())
    st.session_state["charts"] = charts


def result_summary(result):
    summary = (f"{result['label']} — objective {result['objective']}, "
               f"{result['iterations']} iterations, {result['duration']:.4f}s")
    p = result["params"]
    if p:
        summary += " · " + ", ".join(f"{k}={v}" for k, v in p.items())
    return summary


init_state()
requested = render_sidebar()
if requested:
    run_algorithm(requested)

if "fig" not in st.session_state:
    fields = truck_fields()
    tk = truck({k: fields[k] for k in ("w", "l", "h")}, fields["max_capacity"])
    initial = build_initial(tk, st.session_state["packages"])
    st.session_state["fig"] = TruckGraph(initial, tk).draw()

result = st.session_state.get("result")
Visualizer(st.session_state["fig"],
           summary=result_summary(result) if result else None,
           charts=st.session_state.get("charts"),
           left_fig=st.session_state.get("initial_fig")).display()
