import numpy as np

class package:
    def __init__(self, id, dimentions, orientation, value, weight, is_fragile, ETA):
        self.id = id                        # int
        self.dimentions = dimentions        # dict, ex.{"w":1, "l":1, "h":1}
        self.orientation = orientation      # dict, ex.{"w":"x", "l":"y", "h":"z"}
        self.value = value                  # int/float ig
        self.weight = weight                # int/float ig
        self.is_fragile = is_fragile        # bool
        self.ETA = ETA                      # int
    
    def rotate(self, sumbu):
        if(sumbu=="x"):
            self.orientation = {"w":self.orientation["w"], "l":self.orientation["h"], "h":self.orientation["l"]}
        elif(sumbu=="y"):
            self.orientation = {"w":self.orientation["h"], "l":self.orientation["l"], "h":self.orientation["w"]}
        else:   #sumbu=="z"
            self.orientation = {"w":self.orientation["l"], "l":self.orientation["w"], "h":self.orientation["h"]}
    
    def jason_susanto(self)->dict:
        return {
            "id": self.id,
            "dimentions": self.dimentions,
            "orientation": self.orientation,
            "value": self.value,
            "weight": self.weight,
            "is_fragile": self.is_fragile,
            "ETA": self.ETA
        }

class truck:
    def __init__(self, dimentions, max_capacity):
        self.dimentions = dimentions        # dict, ex.{"w":10, "l":20, "h":30}
        self.max_capacity = max_capacity      # int
        self.space = np.zeros((dimentions["h"], dimentions["l"], dimentions["w"]), dtype=int)
        self.inserted_pack = []
    
    
class state:
    def __init__(self, dimentions, inserted_pack, remaining_pack, max_weight):
        self.dimentions = dimentions
        self.space = np.zeros((dimentions["h"], dimentions["l"], dimentions["w"]), dtype=int)
        self.inserted_pack = inserted_pack  # packages dalam truk
        self.remaining_pack = remaining_pack # packages diluar truk
        self.max_weight = max_weight
        self.current_weight = 0
        self.value = 0
    
    def __get_fragile_by_id(self, id) -> bool:
        for package in self.inserted_pack:
            if(package.id == id): return package.is_fragile
        
    def __validate_placement(self, package, coords) -> bool:
        if(self.current_weight + package.weight > self.max_weight):
            return False
        floating_indices = 0
        checked_ids = set()
        if package.orientation["w"] == "x":
            footprint = package.dimentions["w"] * (
                package.dimentions["l"]
                if package.orientation["l"] == "y"
                else package.dimentions["h"]
            )
        elif package.orientation["w"] == "y":
            footprint = package.dimentions["l"] * package.dimentions["w"]
        else:
            footprint = package.dimentions["h"] * package.dimentions["l"]
        if(package.orientation["w"]=="x"):  #check if out of bounds or if space already filled by other package
            if(package.orientation["l"]=="y"):          # no rotation
                if(coords["z"] + package.dimentions["h"]-1 >= self.dimentions["h"] or
                   coords["y"] + package.dimentions["l"]-1 >= self.dimentions["l"] or
                   coords["x"] + package.dimentions["w"]-1 >= self.dimentions["w"]) : return False
                for i in range(coords["z"], coords["z"] + package.dimentions["h"]):
                    for j in range(coords["y"], coords["y"] + package.dimentions["l"]):
                        for k in range(coords["x"], coords["x"] + package.dimentions["w"]):
                            if(self.space[i, j, k] != 0): return False
                            if(i == coords["z"] and coords["z"]-1 != -1):
                                if(self.space[i-1,j,k] == 0): floating_indices+=1
                                else:   # check if one of boxes underneath is fragile
                                    if(self.space[i-1,j,k] not in checked_ids):
                                        if(self.__get_fragile_by_id(self.space[i-1,j,k])): return False
                                        checked_ids.add(self.space[i-1,j,k])
            elif(package.orientation["l"]=="z"):        # sumbu width
                if(coords["z"] + package.dimentions["l"]-1 >= self.dimentions["h"] or
                   coords["y"] + package.dimentions["h"]-1 >= self.dimentions["l"] or
                   coords["x"] + package.dimentions["w"]-1 >= self.dimentions["w"]) : return False
                for i in range(coords["z"], coords["z"] + package.dimentions["l"]):
                    for j in range(coords["y"], coords["y"] + package.dimentions["h"]):
                        for k in range(coords["x"], coords["x"] + package.dimentions["w"]):
                            if(self.space[i, j, k] != 0): return False
                            if(i == coords["z"] and coords["z"]-1 != -1):
                                if(self.space[i-1,j,k] == 0): floating_indices+=1
                                else:   # check if one of boxes underneath is fragile
                                    if(self.space[i-1,j,k] not in checked_ids):
                                        if(self.__get_fragile_by_id(self.space[i-1,j,k])): return False
                                        checked_ids.add(self.space[i-1,j,k])
        elif(package.orientation["w"]=="y"):            # sumbu height
            if(coords["z"] + package.dimentions["h"]-1 >= self.dimentions["h"] or
               coords["y"] + package.dimentions["w"]-1 >= self.dimentions["l"] or
               coords["x"] + package.dimentions["l"]-1 >= self.dimentions["w"]) : return False
            for i in range(coords["z"], coords["z"] + package.dimentions["h"]):
                for j in range(coords["y"], coords["y"] + package.dimentions["w"]):
                    for k in range(coords["x"], coords["x"] + package.dimentions["l"]):
                        if(self.space[i, j, k] != 0): return False
                        if(i == coords["z"] and coords["z"]-1 != -1):
                            if(self.space[i-1,j,k] == 0): floating_indices+=1
                            else:   # check if one of boxes underneath is fragile
                                if(self.space[i-1,j,k] not in checked_ids):
                                    if(self.__get_fragile_by_id(self.space[i-1,j,k])): return False
                                    checked_ids.add(self.space[i-1,j,k])
        elif(package.orientation["w"]=="z"):            # sumbu length
            if(coords["z"] + package.dimentions["w"]-1 >= self.dimentions["h"] or
               coords["y"] + package.dimentions["l"]-1 >= self.dimentions["l"] or
               coords["x"] + package.dimentions["h"]-1 >= self.dimentions["w"]) : return False
            for i in range(coords["z"], coords["z"] + package.dimentions["w"]):
                for j in range(coords["y"], coords["y"] + package.dimentions["l"]):
                    for k in range(coords["x"], coords["x"] + package.dimentions["h"]):
                        if(self.space[i, j, k] != 0): return False
                        if(i == coords["z"] and coords["z"]-1 != -1):
                            if(self.space[i-1,j,k] == 0): floating_indices+=1
                            else:   # check if one of boxes underneath is fragile
                                if(self.space[i-1,j,k] not in checked_ids):
                                    if(self.__get_fragile_by_id(self.space[i-1,j,k])): return False
                                    checked_ids.add(self.space[i-1,j,k])
        if(floating_indices == footprint): return False
        return True
    
    def place_package(self, package, coords) -> bool:
        if(package in self.inserted_pack): 
            return False
        if(self.__validate_placement(package,coords)):
            if(package.orientation["w"]=="x"):
                if(package.orientation["l"]=="y"):          # no rotation
                    for i in range(coords["z"], coords["z"] + package.dimentions["h"]):
                        for j in range(coords["y"], coords["y"] + package.dimentions["l"]):
                            for k in range(coords["x"], coords["x"] + package.dimentions["w"]):
                                self.space[i, j, k] = package.id
                elif(package.orientation["l"]=="z"):        # sumbu width
                    for i in range(coords["z"], coords["z"] + package.dimentions["l"]):
                        for j in range(coords["y"], coords["y"] + package.dimentions["h"]):
                            for k in range(coords["x"], coords["x"] + package.dimentions["w"]):
                                self.space[i, j, k] = package.id
            elif(package.orientation["w"]=="y"):            # sumbu height
                for i in range(coords["z"], coords["z"] + package.dimentions["h"]):
                    for j in range(coords["y"], coords["y"] + package.dimentions["w"]):
                        for k in range(coords["x"], coords["x"] + package.dimentions["l"]):
                            self.space[i, j, k] = package.id
            elif(package.orientation["w"]=="z"):            # sumbu length
                for i in range(coords["z"], coords["z"] + package.dimentions["w"]):
                    for j in range(coords["y"], coords["y"] + package.dimentions["l"]):
                        for k in range(coords["x"], coords["x"] + package.dimentions["h"]):
                            self.space[i, j, k] = package.id
            self.inserted_pack.append(package)
            self.current_weight+=package.weight
            return True
        else:
            return False

    def remove_package(self, package):
        for i in range(self.dimentions["h"]):
            for j in range(self.dimentions["l"]):
                for k in range(self.dimentions["w"]):
                    if(self.space[i,j,k]==package.id):
                        self.space[i,j,k]=0
        if package in self.inserted_pack:
            self.inserted_pack.remove(package)
            self.remaining_pack.append(package)
    
    