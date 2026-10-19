import copy
import random
from kelasking import eff_dims, rotated_orientation, state

def _orientations(pkg):
    base = dict(pkg.orientation)
    return [
        base,
        rotated_orientation(base, "x"),
        rotated_orientation(base, "y"),
        rotated_orientation(base, "z"),
        rotated_orientation(rotated_orientation(base, "z"), "x"),
        rotated_orientation(rotated_orientation(base, "z"), "y"),
    ]

def _place_at_any_valid_position(chromosome, pkg, orientation):
    dimensions = chromosome.dimentions
    for z in range(dimensions["h"]):
        for y in range(dimensions["l"]):
            for x in range(dimensions["w"]):
                if chromosome.place_package(
                    pkg, {"x": x, "y": y, "z": z}, orientation
                ):
                    return True
    return False

def create_initial_population(trukkun, packages, N_population) -> list:
    population = []
    for _ in range(N_population):
        chromosome = state(trukkun.dimentions, [], [copy.copy(pkg) for pkg in packages], trukkun.max_capacity)
        try_packages = chromosome.remaining_pack.copy()
        random.shuffle(try_packages)
        for pkg in try_packages:
            orientations = _orientations(pkg)
            random.shuffle(orientations)
            for orientation in orientations:
                if _place_at_any_valid_position(chromosome, pkg, orientation):
                    break
        population.append(chromosome)
    return population

def _package_by_id(chromosome):
    return {pkg.id: pkg for pkg in chromosome.inserted_pack + chromosome.remaining_pack}

def _placement_candidates(chromosome, package_id):
    if package_id not in chromosome.coords:
        return []
    pkg = _package_by_id(chromosome)[package_id]
    return [
        (
            pkg,
            dict(chromosome.coords[package_id]),
            dict(chromosome.orientations[package_id]),
        )
    ]

def kawin(chromosome_a, chromosome_b):
    # cross package from one state with another state, if invalid try another coordinate
    parent_packages = _package_by_id(chromosome_a)
    parent_packages.update(_package_by_id(chromosome_b))
    child = state(chromosome_a.dimentions, [], [copy.copy(pkg) for pkg in parent_packages.values()], chromosome_a.max_weight)
    child_packages = _package_by_id(child)

    package_ids = list(parent_packages)
    random.shuffle(package_ids)
    package_ids.sort(key=lambda package_id: parent_packages[package_id].value, reverse=True)

    for package_id in package_ids:
        candidates = []
        if package_id in chromosome_a.coords:
            candidates.extend(_placement_candidates(chromosome_a, package_id))
        if package_id in chromosome_b.coords:
            candidates.extend(_placement_candidates(chromosome_b, package_id))
        random.shuffle(candidates)

        placed = False
        for pkg, coords, orientation in candidates:
            child_pkg = child_packages[package_id]
            if child.place_package(child_pkg, coords, orientation):
                placed = True
                break
            if _place_at_any_valid_position(child, child_pkg, orientation):
                placed = True
                break
        if not placed:
            continue
    return child

def _rebuild_with_mutation(chromosome, package_id):
    packages = _package_by_id(chromosome)
    rebuilt = state(chromosome.dimentions, [], [copy.copy(pkg) for pkg in packages.values()], chromosome.max_weight)
    rebuilt_packages = _package_by_id(rebuilt)
    order = [pkg.id for pkg in chromosome.inserted_pack if pkg.id != package_id]
    order.append(package_id)
    random.shuffle(order)

    for current_id in order:
        pkg = rebuilt_packages[current_id]
        orientations = _orientations(pkg)
        if current_id != package_id and current_id in chromosome.orientations:
            inherited = chromosome.orientations[current_id]
            orientations.insert(0, inherited)
        random.shuffle(orientations)
        for orientation in orientations:
            if _place_at_any_valid_position(rebuilt, pkg, orientation):
                break
    return rebuilt

def mutate(chromosome):
    if not chromosome.inserted_pack:
        return chromosome.copy()
    package_id = random.choice(chromosome.inserted_pack).id
    return _rebuild_with_mutation(chromosome, package_id)

# state validiy checking
def _constraint_violations(chromosome):
    violations = 0
    inserted_ids = [pkg.id for pkg in chromosome.inserted_pack]
    remaining_ids = [pkg.id for pkg in chromosome.remaining_pack]
    all_ids = inserted_ids + remaining_ids

    violations += len(all_ids) - len(set(all_ids))
    if chromosome.current_weight != sum(
        pkg.weight for pkg in chromosome.inserted_pack
    ):
        violations += 1
    if chromosome.current_weight > chromosome.max_weight:
        violations += 1

    occupied = set()
    for pkg in chromosome.inserted_pack:
        if pkg.id not in chromosome.coords or pkg.id not in chromosome.orientations:
            violations += 1
            continue
        dimensions = eff_dims(
            pkg.dimentions, chromosome.orientations[pkg.id]
        )
        coords = chromosome.coords[pkg.id]
        x0, y0, z0 = coords["x"], coords["y"], coords["z"]
        if (
            x0 < 0
            or y0 < 0
            or z0 < 0
            or x0 + dimensions["x"] > chromosome.dimentions["w"]
            or y0 + dimensions["y"] > chromosome.dimentions["l"]
            or z0 + dimensions["z"] > chromosome.dimentions["h"]
        ):
            violations += 1
            continue
        for z in range(z0, z0 + dimensions["z"]):
            for y in range(y0, y0 + dimensions["y"]):
                for x in range(x0, x0 + dimensions["x"]):
                    cell = (x, y, z)
                    if cell in occupied or chromosome.space[z, y, x] != pkg.id:
                        violations += 1
                    occupied.add(cell)

    if not chromosome.is_valid():
        violations += 1
    return violations

# basiclaly objective with penalty subtraction if state is not valid
def fitness(chromosome):
    value = chromosome.objective()
    violations = _constraint_violations(chromosome)
    if violations == 0:
        return value
    penalty = sum(abs(pkg.value) for pkg in chromosome.inserted_pack) + 1
    return value - penalty * violations

# rng select parent
def _select(population):
    scores = [fitness(chromosome) for chromosome in population]
    minimum = min(scores)
    weights = [score - minimum for score in scores]

    if sum(weights) == 0:
        weights = [1] * len(population)

    total_weight = sum(weights)
    rng_num = random.random() * total_weight
    cumulative_weight = 0

    for chromosome, weight in zip(population, weights):
        cumulative_weight += weight
        if rng_num < cumulative_weight:
            return chromosome

    return population[-1]

def genetic_algorithm(truckkun, packages, N_population=500, N_iter=1000, mutation_rate=0.05):
    population = create_initial_population(truckkun,packages,N_population,)
    
    max_objective_history = [max(chromosome.objective() for chromosome in population)]
    average_objective_history = [sum(chromosome.objective() for chromosome in population) / N_population]

    for i in range(N_iter):
        print(f"iter: {i}")
        new_population = [max(population, key=fitness).copy()]
        while len(new_population) < N_population:
            parent_a = _select(population)
            parent_b = _select(population)
            child = kawin(parent_a, parent_b)
            if random.random() < mutation_rate:
                child = mutate(child)
            new_population.append(child)
        population = new_population
        objectives = [chromosome.objective() for chromosome in population]
        max_objective_history.append(max(objectives))
        average_objective_history.append(sum(objectives) / N_population)
        print(f"max value: {max_objective_history[i]}")
        print(f"avg value: {average_objective_history[i]}")
        print(f"------------------------------------------")

    final = max(population, key=fitness)
    return final, max_objective_history, average_objective_history, N_population, N_iter
