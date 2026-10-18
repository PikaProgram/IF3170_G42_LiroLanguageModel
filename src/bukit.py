from kelasking import state, package
import time

# takes initial state argument returns a dict? {state result, list time_taken_per_iteration, double time_taken, int iteration_count}
def bukittinggi(initial_state):
    curr = initial_state.copy()
    iter_count = 0
    time_per_iter = []
    ttime_start = time.time()
    while True:
        time_start = time.time()
        neigbour = None
        succs = generate_all_succs(curr)
        if len(succs) == 0: break
        best_successor = max(succs, key=lambda succ: succ.value)
        if best_successor.value <= curr.value:
            break
        curr = best_successor
        iter_count += 1
        time_end = time.time()
        time_per_iter.append((time_end-time_start))
    ttime_end = time.time()
    total_time = ttime_end-ttime_start
    return {"state": curr, "time_per_iter": time_per_iter, "ttime": total_time, "iter_count": iter_count}

# HC sideways move
def bukitsamping(initial_state):
    curr = initial_state.copy()
    iter_count = 0
    time_per_iter = []
    ttime_start = time.time()
    while True:
        time_start = time.time()
        neigbour = None
        succs = generate_all_succs(curr)
        if len(succs) == 0: break
        best_successor = max(succs, key=lambda succ: succ.value)
        if best_successor.value < curr.value:
            break
        curr = best_successor
        iter_count += 1
        time_end = time.time()
        time_per_iter.append((time_end-time_start))
    ttime_end = time.time()
    total_time = ttime_end-ttime_start
    return {"state": curr, "time_per_iter": time_per_iter, "ttime": total_time, "iter_count": iter_count}

# generate all successors
def generate_all_succs(state) -> list:
    res = []
    # move a package's location
    for pack in state.inserted_pack:
        for i in range(state.dimentions["h"]):
            for j in range(state.dimentions["l"]):
                for k in range(state.dimentions["w"]):
                    if not(i == pack.location["z"] and j == pack.location["y"] and k == pack.location["x"]):
                        curr = state.copy()
                        curr_pack = curr.get_pack_by_id(pack.id)
                        curr.remove_package(curr_pack)
                        if(curr.place_package(curr_pack, {"x": k, "y": j, "z": i})):
                            res.append(curr)
                    
    # rotate 90 degrees on x, y, or z axis once
    for pack in state.inserted_pack:
        # rotate x
        curr = state.copy()
        curr_pack = curr.get_pack_by_id(pack.id)
        curr.remove_package(curr_pack)
        curr_pack.rotate("x")
        if(curr.place_package(curr_pack, pack.location)):
            res.append(curr)
        
        # rotate y
        curr = state.copy()
        curr_pack = curr.get_pack_by_id(pack.id)
        curr.remove_package(curr_pack)
        curr_pack.rotate("y")
        if(curr.place_package(curr_pack, pack.location)):
            res.append(curr)
        
        # rotate z
        curr = state.copy()
        curr_pack = curr.get_pack_by_id(pack.id)
        curr.remove_package(curr_pack)
        curr_pack.rotate("z")
        if(curr.place_package(curr_pack, pack.location)):
            res.append(curr)
        
        # rotate x then z
        curr = state.copy()
        curr_pack = curr.get_pack_by_id(pack.id)
        curr.remove_package(curr_pack)
        curr_pack.rotate("x")
        curr_pack.rotate("z")
        if(curr.place_package(curr_pack, pack.location)):
            res.append(curr)
        
        # rotate y then z
        curr = state.copy()
        curr_pack = curr.get_pack_by_id(pack.id)
        curr.remove_package(curr_pack)
        curr_pack.rotate("y")
        curr_pack.rotate("z")
        if(curr.place_package(curr_pack, pack.location)):
            res.append(curr)
    
    # swap 2 packages both inside
    for i in range(len(state.inserted_pack)):
        for j in range(i,len(state.inserted_pack)):
            if(i!=j):
                curr = state.copy()
                curr_pack_a = curr.get_pack_by_id(state.inserted_pack[i].id)
                curr_pack_b = curr.get_pack_by_id(state.inserted_pack[j].id)
                location_a = state.inserted_pack[i].location
                location_b = state.inserted_pack[j].location
                curr.remove_package(curr_pack_a)
                curr.remove_package(curr_pack_b)
                if(curr.place_package(curr_pack_a, location_b) == True and
                   curr.place_package(curr_pack_b, location_a) == True):
                    res.append(curr)
    
    # swap package 1 from in, 1 from out
    for pack_in in state.inserted_pack:
        for pack_out in state.remaining_pack:
            curr = state.copy()
            location = pack_in.location
            curr_pack_in = curr.get_pack_by_id(pack_in.id)
            curr_pack_out = curr.get_pack_by_id(pack_out.id)
            curr.remove_package(curr_pack_in)
            if(curr.place_package(curr_pack_out, location)):
                res.append(curr)
    
    return res