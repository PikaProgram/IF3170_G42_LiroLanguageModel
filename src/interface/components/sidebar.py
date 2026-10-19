import json
from pathlib import Path

import streamlit as st

DEFAULT_CONFIG = Path(__file__).parents[2] / "config_test.json"

ALGORITHMS = {
    "hc": {"label": "HC steepest-ascent", "record": "hill_climbing_steepest_ascent"},
    "sa": {"label": "Simulated annealing", "record": "simulated_annealing"},
}

_PKG_FIELDS = ("id", "dimentions", "orientation",
               "value", "weight", "is_fragile", "ETA")
_TRUCK_KEYS = {"w": "truck_w", "l": "truck_l",
               "h": "truck_h", "max_capacity": "truck_cap"}


def _is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _parse_dims(d, label, minimum):
    if not isinstance(d, dict):
        raise ValueError(f"{label}: must be an object with w, l, h.")
    missing = [k for k in ("w", "l", "h") if k not in d]
    if missing:
        raise ValueError(f"{label}: missing {', '.join(missing)}.")
    for k in ("w", "l", "h"):
        if not _is_int(d[k]) or d[k] < minimum:
            raise ValueError(
                f"{label}: '{k}' must be a whole number >= {minimum}.")
    return {k: d[k] for k in ("w", "l", "h")}


def _parse_package(p, i):
    if not isinstance(p, dict):
        raise ValueError(f"Package #{i}: must be an object.")
    missing = [k for k in _PKG_FIELDS if k not in p]
    if missing:
        raise ValueError(f"Package #{i}: missing {', '.join(missing)}.")
    if not (_is_int(p["id"]) or isinstance(p["id"], str)):
        raise ValueError(
            f"Package #{i}: 'id' must be a whole number or string.")
    dims = _parse_dims(p["dimentions"], f"Package #{i} 'dimentions'", 1)
    orient = p["orientation"]
    if not isinstance(orient, dict):
        raise ValueError(
            f"Package #{i} 'orientation': must be an object with w, l, h.")
    missing = [k for k in ("w", "l", "h") if k not in orient]
    if missing:
        raise ValueError(f"Package #{i} 'orientation': missing {', '.join(missing)}.")
    axes = [orient[k] for k in ("w", "l", "h")]
    if any(a not in ("x", "y", "z") for a in axes) or len(set(axes)) != 3:
        raise ValueError(
            f"Package #{i} 'orientation': w, l, h must map to distinct axes x, y, z.")
    for k in ("value", "weight", "ETA"):
        if not _is_num(p[k]) or p[k] < 0:
            raise ValueError(f"Package #{i}: '{k}' must be a number >= 0.")
    if not isinstance(p["is_fragile"], bool):
        raise ValueError(f"Package #{i}: 'is_fragile' must be true or false.")
    return {
        "id": p["id"],
        "dimentions": dims,
        "orientation": {k: orient[k] for k in ("w", "l", "h")},
        "value": p["value"],
        "weight": p["weight"],
        "is_fragile": p["is_fragile"],
        "ETA": p["ETA"],
    }


def _parse_truck(t):
    if not isinstance(t, dict):
        raise ValueError(
            "'truck': must be an object with dimentions and max_capacity.")
    missing = [k for k in ("dimentions", "max_capacity") if k not in t]
    if missing:
        raise ValueError(f"'truck': missing {', '.join(missing)}.")
    dims = _parse_dims(t["dimentions"], "'truck' 'dimentions'", 0)
    if not _is_num(t["max_capacity"]) or t["max_capacity"] < 0:
        raise ValueError("'truck' 'max_capacity': must be a number >= 0.")
    return {**dims, "max_capacity": t["max_capacity"]}


def parse_config(text):
    try:
        j = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}.") from e
    if not isinstance(j, dict):
        raise ValueError("Config root must be a JSON object.")
    raw = j.get("packages")
    if not isinstance(raw, list):
        raise ValueError("'packages' must be a list.")
    packages = [_parse_package(p, i) for i, p in enumerate(raw)]
    ids = [p["id"] for p in packages]
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate package ids in config.")
    return packages, _parse_truck(j.get("truck"))


def init_state():
    ss = st.session_state
    if "packages" in ss:
        return
    packages, truck_fields = parse_config(DEFAULT_CONFIG.read_text())
    ss["packages"] = packages
    for field, key in _TRUCK_KEYS.items():
        ss[key] = truck_fields[field]
    ss["algo"] = "hc"
    ss["sa_temp"] = 100.0
    ss["sa_cooling"] = 0.995
    ss["sa_min_temp"] = 0.01


def truck_fields():
    ss = st.session_state
    return {"w": ss["truck_w"], "l": ss["truck_l"], "h": ss["truck_h"],
            "max_capacity": ss["truck_cap"]}


def _file_section():
    st.subheader("Load config")
    up = st.file_uploader("Config JSON", type=["json"], key="cfg_upload")
    if up is not None and st.session_state.get("_tried_upload") != up.file_id:
        st.session_state["_tried_upload"] = up.file_id
        try:
            packages, truck_fields = parse_config(
                up.getvalue().decode("utf-8"))
        except (ValueError, UnicodeDecodeError) as e:
            st.session_state["_input_error"] = str(e)
        else:
            st.session_state["_input_error"] = None
            st.session_state["packages"] = packages
            for field, key in _TRUCK_KEYS.items():
                st.session_state[key] = truck_fields[field]
    if st.session_state.get("_input_error"):
        st.error(st.session_state["_input_error"])


def _package_section():
    st.subheader("Packages")
    packages = st.session_state["packages"]

    with st.form("add_package", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        w = c1.number_input("Width w", min_value=1, value=1, step=1, key="f_w")
        l = c2.number_input("Length l", min_value=1,
                            value=1, step=1, key="f_l")
        h = c3.number_input("Height h", min_value=1,
                            value=1, step=1, key="f_h")
        c4, c5, c6 = st.columns(3)
        value = c4.number_input("Value", min_value=0,
                                value=1, step=1, key="f_value")
        weight = c5.number_input(
            "Weight", min_value=0, value=1, step=1, key="f_weight")
        eta = c6.number_input("ETA", min_value=0, value=1, step=1, key="f_eta")
        fragile = st.checkbox("Fragile", key="f_fragile")
        added = st.form_submit_button("Add package")

    if added:
        next_id = max((p["id"]
                      for p in packages if _is_int(p["id"])), default=0) + 1
        packages.append({
            "id": next_id,
            "dimentions": {"w": w, "l": l, "h": h},
            "orientation": {"w": "x", "l": "y", "h": "z"},
            "value": value,
            "weight": weight,
            "is_fragile": fragile,
            "ETA": eta,
        })

    if not packages:
        st.caption("No packages yet.")
    to_delete = None
    for p in packages:
        c1, c2 = st.columns([5, 1])
        d = p["dimentions"]
        fragile_note = ", fragile" if p["is_fragile"] else ""
        c1.caption(f"#{p['id']} · {d['w']}×{d['l']}×{d['h']} · value {p['value']} · "
                   f"weight {p['weight']} · ETA {p['ETA']}{fragile_note}")
        if c2.button("×", key=f"del_{p['id']}"):
            to_delete = p["id"]
    if to_delete is not None:
        packages[:] = [p for p in packages if p["id"] != to_delete]


def _truck_section():
    st.subheader("Truck")
    c1, c2 = st.columns(2)
    c1.number_input("Width w", min_value=0, step=1, key="truck_w")
    c2.number_input("Length l", min_value=0, step=1, key="truck_l")
    c3, c4 = st.columns(2)
    c3.number_input("Height h", min_value=0, step=1, key="truck_h")
    c4.number_input("Max capacity", min_value=0, step=1, key="truck_cap")


def _algorithm_section():
    st.subheader("Algorithm")
    st.selectbox("Algorithm", options=list(ALGORITHMS),
                 format_func=lambda a: ALGORITHMS[a]["label"], key="algo")
    if st.session_state["algo"] == "sa":
        st.number_input("Initial temperature", min_value=0.01,
                        step=0.01, key="sa_temp")
        st.number_input("Cooling rate", min_value=0.0001, max_value=0.9999,
                        step=0.0001, key="sa_cooling")
        st.number_input("Minimum temperature", min_value=0.01,
                        step=0.01, key="sa_min_temp")
    else:
        st.caption("Steepest ascent takes no parameters.")


def render_sidebar():
    with st.sidebar:
        _file_section()
        _package_section()
        _truck_section()
        _algorithm_section()
        st.divider()
        if not st.button("Run", type="primary", width='stretch'):
            return None
        if not st.session_state["packages"]:
            st.warning("Add at least one package or load a config file.")
            return None
        fields = truck_fields()
        if any(fields[k] <= 0 for k in ("w", "l", "h", "max_capacity")):
            st.warning(
                "Set truck dimensions and capacity (or load a config file).")
            return None
        algo = st.session_state["algo"]
        params = None
        if algo == "sa":
            params = {
                "temp": float(st.session_state["sa_temp"]),
                "cooling_rate": float(st.session_state["sa_cooling"]),
                "minimum_temp": float(st.session_state["sa_min_temp"]),
            }
        return {"algorithm": algo, "params": params}
