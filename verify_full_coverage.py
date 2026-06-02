import time
from env.grid_world import GridWorld


ALLOW_SENSOR_ON_TARGET = True


def get_max_sensors(world):
    if hasattr(world, "max_sensors"):
        return world.max_sensors

    if hasattr(world, "sensors_max"):
        return world.sensors_max

    raise AttributeError("Could not find max_sensors or sensors_max in GridWorld.")


def get_sensor_range(world):
    if hasattr(world, "sensor_range"):
        return world.sensor_range

    if hasattr(world, "range_sensor"):
        return world.range_sensor

    raise AttributeError("Could not find sensor_range or range_sensor in GridWorld.")


def get_rows(world):
    if hasattr(world, "rows"):
        return world.rows

    if hasattr(world, "row"):
        return world.row

    raise AttributeError("Could not find rows or row in GridWorld.")


def get_cols(world):
    if hasattr(world, "cols"):
        return world.cols

    if hasattr(world, "col"):
        return world.col

    raise AttributeError("Could not find cols or col in GridWorld.")


def build_candidates(world, allow_sensor_on_target=True):
    targets = world.get_targets()
    target_to_index = {target: i for i, target in enumerate(targets)}
    target_set = set(targets)

    rows = get_rows(world)
    cols = get_cols(world)
    sensor_range = get_sensor_range(world)

    candidates_by_mask = {}

    for x in range(rows):
        for y in range(cols):
            position = (x, y)

            if not world.is_valid_position(x, y):
                continue

            if not allow_sensor_on_target and position in target_set:
                continue

            mask = 0

            for target in targets:
                tx, ty = target
                distance = abs(x - tx) + abs(y - ty)

                if distance <= sensor_range:
                    index = target_to_index[target]
                    mask |= 1 << index

            if mask != 0:
                if mask not in candidates_by_mask:
                    candidates_by_mask[mask] = position

    candidates = [
        (position, mask)
        for mask, position in candidates_by_mask.items()
    ]

    candidates.sort(
        key=lambda item: item[1].bit_count(),
        reverse=True
    )

    pruned = []

    for position, mask in candidates:
        dominated = False

        for _, kept_mask in pruned:
            if mask | kept_mask == kept_mask:
                dominated = True
                break

        if not dominated:
            pruned.append((position, mask))

    return targets, pruned


def exact_full_cover(map_name):
    world = GridWorld(map_name)
    max_sensors = get_max_sensors(world)

    targets, candidates = build_candidates(
        world,
        allow_sensor_on_target=ALLOW_SENSOR_ON_TARGET
    )

    target_count = len(targets)
    full_mask = (1 << target_count) - 1

    union_mask = 0

    for _, mask in candidates:
        union_mask |= mask

    if union_mask != full_mask:
        return False, []

    coverers = [[] for _ in range(target_count)]

    for index, (_, mask) in enumerate(candidates):
        for target_index in range(target_count):
            if mask & (1 << target_index):
                coverers[target_index].append(index)

    impossible_states = set()

    def dfs(uncovered_mask, remaining_sensors):
        if uncovered_mask == 0:
            return []

        if remaining_sensors == 0:
            return None

        key = (uncovered_mask, remaining_sensors)

        if key in impossible_states:
            return None

        max_single_gain = 0

        for _, mask in candidates:
            gain = (mask & uncovered_mask).bit_count()

            if gain > max_single_gain:
                max_single_gain = gain

        if max_single_gain == 0:
            impossible_states.add(key)
            return None

        min_needed = (
            uncovered_mask.bit_count() + max_single_gain - 1
        ) // max_single_gain

        if min_needed > remaining_sensors:
            impossible_states.add(key)
            return None

        uncovered_indices = [
            i for i in range(target_count)
            if uncovered_mask & (1 << i)
        ]

        selected_options = None

        for target_index in uncovered_indices:
            options = [
                candidate_index
                for candidate_index in coverers[target_index]
                if candidates[candidate_index][1] & uncovered_mask
            ]

            if not options:
                impossible_states.add(key)
                return None

            if selected_options is None or len(options) < len(selected_options):
                selected_options = options

        selected_options.sort(
            key=lambda idx: (
                candidates[idx][1] & uncovered_mask
            ).bit_count(),
            reverse=True
        )

        for candidate_index in selected_options:
            position, mask = candidates[candidate_index]
            new_uncovered_mask = uncovered_mask & ~mask

            result = dfs(new_uncovered_mask, remaining_sensors - 1)

            if result is not None:
                return [position] + result

        impossible_states.add(key)
        return None

    solution = dfs(full_mask, max_sensors)

    if solution is None:
        return False, []

    return True, solution


def exact_max_coverage(map_name):
    world = GridWorld(map_name)
    max_sensors = get_max_sensors(world)

    targets, candidates = build_candidates(
        world,
        allow_sensor_on_target=ALLOW_SENSOR_ON_TARGET
    )

    target_count = len(targets)
    full_mask = (1 << target_count) - 1

    full_possible, full_solution = exact_full_cover(map_name)

    if full_possible:
        return target_count, target_count, full_solution

    candidates.sort(
        key=lambda item: item[1].bit_count(),
        reverse=True
    )

    suffix_union = [0] * (len(candidates) + 1)

    for i in range(len(candidates) - 1, -1, -1):
        suffix_union[i] = suffix_union[i + 1] | candidates[i][1]

    best_mask = 0
    best_solution = []

    def dfs(start_index, selected_positions, covered_mask):
        nonlocal best_mask, best_solution

        covered_count = covered_mask.bit_count()

        if covered_count > best_mask.bit_count():
            best_mask = covered_mask
            best_solution = list(selected_positions)

        if len(selected_positions) == max_sensors:
            return

        if start_index >= len(candidates):
            return

        possible_mask = covered_mask | suffix_union[start_index]

        if possible_mask.bit_count() <= best_mask.bit_count():
            return

        remaining_slots = max_sensors - len(selected_positions)
        uncovered_mask = full_mask & ~covered_mask

        gains = []

        for _, mask in candidates[start_index:]:
            gain = (mask & uncovered_mask).bit_count()

            if gain > 0:
                gains.append(gain)

        if not gains:
            return

        gains.sort(reverse=True)

        optimistic_upper_bound = covered_count + sum(gains[:remaining_slots])

        if optimistic_upper_bound <= best_mask.bit_count():
            return

        for i in range(start_index, len(candidates)):
            position, mask = candidates[i]
            new_mask = covered_mask | mask

            if new_mask == covered_mask:
                continue

            selected_positions.append(position)
            dfs(i + 1, selected_positions, new_mask)
            selected_positions.pop()

    dfs(0, [], 0)

    return best_mask.bit_count(), target_count, best_solution


def run_full_cover_check():
    map_names = [
        "map1",
        "map2",
        "map3",
        "map4",
        "map5",
        "map6",
        "map7"
    ]

    for map_name in map_names:
        possible, solution = exact_full_cover(map_name)

        print("=" * 60)
        print(f"Map: {map_name}")

        if possible:
            print("Full coverage possible: YES")
            print("Number of sensors:", len(solution))
            print("Sensor positions:", sorted(solution))
        else:
            print("Full coverage possible: NO")


def run_exact_analysis_for_all_maps():
    map_names = [
        "map1",
        "map2",
        "map3",
        "map4",
        "map5",
        "map6",
        "map7"
    ]

    # These are the best coverage values obtained from your local search run.
    # If you run the algorithms again and get different results, update them.
    local_search_best_coverage = {
        "map1": 31,
        "map2": 24,
        "map3": 38,
        "map4": 9,
        "map5": 35,
        "map6": 38,
        "map7": 12
    }

    for map_name in map_names:
        print("=" * 60)
        print(f"Map: {map_name}")

        start_time = time.perf_counter()

        max_covered, total_targets, solution = exact_max_coverage(map_name)

        elapsed_time = time.perf_counter() - start_time

        local_best = local_search_best_coverage.get(map_name)

        print(f"Exact maximum coverage: {max_covered} / {total_targets}")
        print(f"Number of sensors in exact solution: {len(solution)}")
        print(f"Exact best sensor positions: {sorted(solution)}")
        print(f"Elapsed time: {elapsed_time:.2f} seconds")

        if local_best is not None:
            print(f"Best local search coverage: {local_best} / {total_targets}")

            if local_best == max_covered:
                print("Result: Local search reached the exact maximum coverage.")
            elif local_best < max_covered:
                print("Result: Local search did NOT reach the exact maximum coverage.")
                print("Interpretation: This may indicate local optimum or insufficient parameters.")
            else:
                print("Result: Please check the data; local search coverage cannot exceed exact maximum.")


if __name__ == "__main__":
    print("\nFULL COVERAGE CHECK")
    run_full_cover_check()

    print("\nEXACT MAXIMUM COVERAGE ANALYSIS")
    run_exact_analysis_for_all_maps()