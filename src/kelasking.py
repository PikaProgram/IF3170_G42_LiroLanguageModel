from copy import deepcopy
import numpy as np


def rotated_orientation(orientation, axis):
    side_of = {ax: side for side, ax in orientation.items()}
    a, b = (ax for ax in ("x", "y", "z") if ax != axis)
    new = dict(orientation)
    new[side_of[a]], new[side_of[b]] = orientation[side_of[b]], orientation[side_of[a]]
    return new


def eff_dims(dimentions, orientation):
    return {ax: dimentions[side] for side, ax in orientation.items()}


class package:
    def __init__(self, id, dimentions, orientation, value, weight, is_fragile, ETA):
        self.id = id                        # int/str
        self.dimentions = dimentions        # dict, ex.{"w":1, "l":1, "h":1}
        self.orientation = orientation      # dict, ex.{"w":"x", "l":"y", "h":"z"}
        self.value = value                  # int/float
        self.weight = weight                # int/float
        self.is_fragile = is_fragile        # bool
        self.ETA = ETA                      # int
    def rotate(self, sumbu):
        self.orientation = rotated_orientation(self.orientation, sumbu)

    def jason_susanto(self) -> dict:
        return {
            "id": self.id,
            "dimentions": self.dimentions,
            "orientation": self.orientation,
            "value": self.value,
            "weight": self.weight,
            "is_fragile": self.is_fragile,
            "ETA": self.ETA,
        }


class truck:
    def __init__(self, dimentions, max_capacity):
        self.dimentions = dimentions        # dict, ex.{"w":10, "l":20, "h":30}
        self.max_capacity = max_capacity    # int, satuan unit berat
        self.space = np.full((dimentions["h"], dimentions["l"], dimentions["w"]), None, dtype=object)
        self.inserted_pack = []


class state:
    def __init__(self, dimentions, inserted_pack, remaining_pack, max_weight):
        self.dimentions = dimentions
        # space[z][y][x] = package.id atau None (kosong); id boleh int/str
        self.space = np.full((dimentions["h"], dimentions["l"], dimentions["w"]), None, dtype=object)
        self.inserted_pack = inserted_pack   # packages dalam truk
        self.remaining_pack = remaining_pack # packages di luar truk
        self.max_weight = max_weight
        self.current_weight = sum(p.weight for p in inserted_pack)
        self.coords = {}  # package.id -> sudut kiri-bawah-belakang {"x","y","z"}
        self.orientations = {p.id: dict(p.orientation) for p in inserted_pack + remaining_pack}
        self.fragile_ids = frozenset(p.id for p in inserted_pack + remaining_pack if p.is_fragile)

    def copy(self):
        s = state(self.dimentions, list(self.inserted_pack), list(self.remaining_pack), self.max_weight)
        s.space = self.space.copy()
        s.coords = {k: dict(v) for k, v in self.coords.items()}
        s.orientations = {k: dict(v) for k, v in self.orientations.items()}
        return s

    def objective(self):
        return sum(p.value for p in self.inserted_pack)

    def fits(self, pkg, orientation, coords) -> bool:
        """Batas dinding, tabrakan, >=1 titik alas ditopang, dan tidak ada fragile tepat di bawah alas."""
        eff = eff_dims(pkg.dimentions, orientation)
        x0, y0, z0 = coords["x"], coords["y"], coords["z"]
        if (x0 < 0 or y0 < 0 or z0 < 0
                or x0 + eff["x"] > self.dimentions["w"]
                or y0 + eff["y"] > self.dimentions["l"]
                or z0 + eff["z"] > self.dimentions["h"]):
            return False
        region = self.space[z0:z0 + eff["z"], y0:y0 + eff["y"], x0:x0 + eff["x"]]
        if any(c is not None for c in region.flat):
            return False
        if z0 == 0:
            return True  # bersandar ke alas truk
        supported = False
        for cell in self.space[z0 - 1, y0:y0 + eff["y"], x0:x0 + eff["x"]].flat:
            if cell is not None:
                supported = True
                if cell in self.fragile_ids:
                    return False  # fragile menjadi support
        return supported

    def is_valid(self):
        if self.current_weight > self.max_weight:
            return False
        for p in self.inserted_pack:
            eff = eff_dims(p.dimentions, self.orientations[p.id])
            c = self.coords[p.id]
            x0, y0, z0 = c["x"], c["y"], c["z"]
            if z0 > 0 and not any(c is not None for c in self.space[z0 - 1, y0:y0 + eff["y"], x0:x0 + eff["x"]].flat):
                return False  # melayang
            if (p.is_fragile and z0 + eff["z"] < self.dimentions["h"]
                    and any(c is not None for c in self.space[z0 + eff["z"], y0:y0 + eff["y"], x0:x0 + eff["x"]].flat)):
                return False  # fragile menjadi support
        return True

    def _write(self, pkg, orientation, coords):
        eff = eff_dims(pkg.dimentions, orientation)
        self.space[coords["z"]:coords["z"] + eff["z"],
                   coords["y"]:coords["y"] + eff["y"],
                   coords["x"]:coords["x"] + eff["x"]] = pkg.id

    def place_package(self, pkg, coords, orientation=None) -> bool:
        if pkg in self.inserted_pack:
            return False
        if orientation is None:
            orientation = self.orientations.get(pkg.id, pkg.orientation)
        if self.current_weight + pkg.weight > self.max_weight:
            return False
        if not self.fits(pkg, orientation, coords):
            return False
        self._write(pkg, orientation, coords)
        self.inserted_pack.append(pkg)
        self.remaining_pack.remove(pkg)
        self.current_weight += pkg.weight
        self.coords[pkg.id] = dict(coords)
        self.orientations[pkg.id] = dict(orientation)
        return True

    def remove_package(self, pkg):
        c = self.coords.pop(pkg.id, None)
        if c is None:
            return
        eff = eff_dims(pkg.dimentions, self.orientations[pkg.id])
        self.space[c["z"]:c["z"] + eff["z"], c["y"]:c["y"] + eff["y"], c["x"]:c["x"] + eff["x"]] = None
        self.remaining_pack.append(pkg)
        self.inserted_pack.remove(pkg)
        self.current_weight -= pkg.weight
