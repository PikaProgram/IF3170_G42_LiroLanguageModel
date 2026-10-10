from kelasking import package, truck, state
import json, random

packages = []
initial_tk = truck({"w":0, "l":0, "h":0}, 0)

def load(path):
    global initial_tk
    with open(path, "r") as file:
        j = json.load(file)
    for pack in j["packages"]:
        packages.append(package(pack["id"], pack["dimentions"], pack["orientation"], pack["value"], pack["weight"], pack["is_fragile"], pack["ETA"]))
    initial_tk = truck(j["truck"]["dimentions"], j["truck"]["max_capacity"])

def create_initial_state(trukkun, packages)->state:
    result = state(trukkun.dimentions, [], packages, trukkun.max_capacity)
    try_packages = packages.copy()
    while len(try_packages)!=0:
        num = random.randrange(len(try_packages))
        this_package = try_packages[num]
        original_orientation = this_package.orientation.copy()
        packed = False
        # loop placement sampe bisa
        # kalo gaada yang bisa rotate, loop placement lagi
        # rotate lagi sampe gaada config rotate
        # kalo tetep gabisa remove dari try_packages
        
        # original orientation
        if packed == False:
            for i in range(trukkun.dimentions["h"]):
                for j in range(trukkun.dimentions["l"]):
                    for k in range(trukkun.dimentions["w"]):
                        if(result.place_package(this_package, {"x":k, "y": j, "z": i}) == True): 
                            packed = True
                            break
                    if packed: break
                if packed: break
        # rotasi sb. x
        if packed == False:
            this_package.rotate("x")
            for i in range(trukkun.dimentions["h"]):
                for j in range(trukkun.dimentions["l"]):
                    for k in range(trukkun.dimentions["w"]):
                        if(result.place_package(this_package, {"x":k, "y": j, "z": i}) == True): 
                            packed = True
                            break
                    if packed: break
                if packed: break
        # rotasi sb. y
        if packed == False:
            this_package.rotate("x")
            this_package.rotate("y")
            for i in range(trukkun.dimentions["h"]):
                for j in range(trukkun.dimentions["l"]):
                    for k in range(trukkun.dimentions["w"]):
                        if(result.place_package(this_package, {"x":k, "y": j, "z": i})): 
                            packed = True
                            break
                    if packed: break
                if packed: break
        # rotasi sb. z
        if packed == False:
            this_package.rotate("y")
            this_package.rotate("z")
            for i in range(trukkun.dimentions["h"]):
                for j in range(trukkun.dimentions["l"]):
                    for k in range(trukkun.dimentions["w"]):
                        if(result.place_package(this_package, {"x":k, "y": j, "z": i})): 
                            packed = True
                            break
                    if packed: break
                if packed: break
        # rotasi sb. x & z
        if packed == False:
            this_package.rotate("z")
            this_package.rotate("x")
            this_package.rotate("z")
            for i in range(trukkun.dimentions["h"]):
                for j in range(trukkun.dimentions["l"]):
                    for k in range(trukkun.dimentions["w"]):
                        if(result.place_package(this_package, {"x":k, "y": j, "z": i})): 
                            packed = True
                            break
                    if packed: break
                if packed: break
        # rotasi sb. y & z
        if packed == False:
            this_package.rotate("x")
            this_package.rotate("z")
            for i in range(trukkun.dimentions["h"]):
                for j in range(trukkun.dimentions["l"]):
                    for k in range(trukkun.dimentions["w"]):
                        if(result.place_package(this_package, {"x":k, "y": j, "z": i})): 
                            packed = True
                            break
                    if packed: break
                if packed: break
        
        if packed:
            result.remaining_pack.remove(this_package)
        else:
            this_package.orientation = original_orientation
        try_packages.remove(this_package)
    
    # create initial state json
    package_in = [
        p.jason_susanto() for p in result.inserted_pack
    ]
    package_out = [
        p.jason_susanto() for p in result.remaining_pack
    ]
    
    json_data = {
        "packages_outside": package_out,
        "truck": {
            "dimentions": result.dimentions,
            "max_capacity": trukkun.max_capacity,
            "space": result.space.tolist(),
            "inserted_packages": package_in
        }
    }
    
    with open("out_test.json", "w") as f:
        f.write(json.dumps(json_data, indent=4))
    
    return result


load("config_test.json")

test = create_initial_state(initial_tk, packages)

# Create initial state
# Do HC or SA or GA -- Masing2 1 file .py, final state dibikin di sini
# Show Final state
# Done
