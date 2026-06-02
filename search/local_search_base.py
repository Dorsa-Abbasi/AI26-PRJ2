import random

class LocalSearchBase:

    def __init__(self, world):
        self.world = world
        self.targets = self.world.get_targets()
        self.target_set = set(self.targets)
        self.valid_positions = self.available_cells()
        self.cell_targets = {}
        for position in self.valid_positions:
            self.cell_targets[position] = self.targets_covered_by_cell(position)

    def normalize_state(self, state):
        return sorted(list(set(state)))

    def state_is_legal(self, state):
        if len(state) > self.world.max_sensors:
            return False
        if len(state) != len(set(state)):
            return False
        for x, y in state:
            if not self.world.is_valid_position(x, y):
                return False
        return True

    def available_cells(self):
        cells = []
        for x in range(self.world.rows):
            for y in range(self.world.cols):
                if self.world.is_valid_position(x, y):
                    cells.append((x, y))
        return cells

    def targets_covered_by_cell(self, cell):
        x, y = cell
        covered = set()
        for tx, ty in self.targets:
            distance = abs(x - tx) + abs(y - ty)
            if distance <= self.world.sensor_range:
                covered.add((tx, ty))
        return covered

    def covered_targets_of(self, state):
        covered_targets = set()
        for sensor in state:
            covered_targets.update(self.cell_targets.get(sensor, set()))
        return covered_targets

    def count_redundant_coverage(self, state):
        target_cover_counts = {}
        for sensor in state:
            for target in self.cell_targets.get(sensor, set()):
                target_cover_counts[target] = target_cover_counts.get(target, 0) + 1
        redundant_coverage = 0
        for count in target_cover_counts.values():
            if count > 1:
                redundant_coverage += count - 1
        return redundant_coverage

    def get_sensor_unique_cover_count(self, state, sensor):
        sensor_targets = self.cell_targets.get(sensor, set())
        other_targets = set()
        for other_sensor in state:
            if other_sensor != sensor:
                other_targets.update(self.cell_targets.get(other_sensor, set()))
        return len(sensor_targets - other_targets)

    def evaluate(self, state):
        state = self.normalize_state(state)
        if not self.state_is_legal(state):
            return 10**12
        covered_targets = self.covered_targets_of(state)
        uncovered_count = len(self.targets) - len(covered_targets)
        sensor_count = len(state)
        redundant_coverage = self.count_redundant_coverage(state)
        uncovered_penalty = 1000 * uncovered_count
        sensor_penalty = 5 * sensor_count
        overlap_penalty = 2 * redundant_coverage
        return uncovered_penalty + sensor_penalty + overlap_penalty

    def position_score(self, position, uncovered_targets):
        covered_by_position = self.cell_targets.get(position, set())
        new_coverage = len(covered_by_position & uncovered_targets)
        total_coverage = len(covered_by_position)
        return 1000 * new_coverage + 10 * total_coverage

    def get_priority_positions(self, state, limit=80):
        state = self.normalize_state(state)
        covered_targets = self.covered_targets_of(state)
        uncovered_targets = self.target_set - covered_targets
        candidates = [
            position for position in self.valid_positions
            if position not in state
        ]
        candidates.sort(
            key=lambda position: self.position_score(position, uncovered_targets),
            reverse=True
        )
        priority_positions = candidates[:limit]
        if len(candidates) > limit:
            random_positions = random.sample(
                candidates[limit:],
                min(20, len(candidates[limit:]))
            )
            priority_positions.extend(random_positions)
        return priority_positions

    def initialize_state(self, mode="mixed"):
        if mode == "random":
            if not self.valid_positions:
                return []
            sensor_count = random.randint(
                1,
                min(self.world.max_sensors, len(self.valid_positions))
            )
            return self.normalize_state(
                random.sample(self.valid_positions, sensor_count)
            )
        state = []
        uncovered_targets = set(self.target_set)
        while len(state) < self.world.max_sensors and uncovered_targets:
            scored_positions = []
            for position in self.valid_positions:
                if position in state:
                    continue
                covered_targets = self.cell_targets[position] & uncovered_targets
                score = len(covered_targets)
                if score > 0:
                    scored_positions.append((score, position, covered_targets))
            if not scored_positions:
                break
            scored_positions.sort(reverse=True, key=lambda item: item[0])
            if mode == "greedy":
                _, selected_position, selected_covered_targets = scored_positions[0]
            else:
                top_candidates = scored_positions[:min(8, len(scored_positions))]
                _, selected_position, selected_covered_targets = random.choice(top_candidates)
            state.append(selected_position)
            uncovered_targets -= selected_covered_targets
        if not state:
            return self.initialize_state(mode="random")
        return self.normalize_state(state)

    def get_neighbor(self, state):
        state = self.normalize_state(state)
        operations = []
        if len(state) > 0:
            operations.append("move")
        if len(state) < self.world.max_sensors:
            operations.append("add")
        if len(state) > 1:
            operations.append("remove")
        if not operations:
            return state
        operation = random.choice(operations)
        if operation == "move":
            available_positions = [
                position for position in self.valid_positions
                if position not in state
            ]
            if not available_positions:
                return state
            neighbor = list(state)
            index = random.randrange(len(neighbor))
            neighbor[index] = random.choice(available_positions)
            return self.normalize_state(neighbor)
        if operation == "add":
            available_positions = [
                position for position in self.valid_positions
                if position not in state
            ]
            if not available_positions:
                return state
            neighbor = list(state)
            neighbor.append(random.choice(available_positions))
            return self.normalize_state(neighbor)
        if operation == "remove":
            neighbor = list(state)
            index = random.randrange(len(neighbor))
            neighbor.pop(index)
            return self.normalize_state(neighbor)
        return state

    def get_neighbors(self, state, count=100):
        state = self.normalize_state(state)
        state_key = tuple(state)
        neighbors = []
        seen = set()

        def add_neighbor(candidate):
            candidate = self.normalize_state(candidate)
            candidate_key = tuple(candidate)
            if candidate_key == state_key:
                return
            if candidate_key in seen:
                return
            if not self.state_is_legal(candidate):
                return
            seen.add(candidate_key)
            neighbors.append(candidate)
        priority_positions = self.get_priority_positions(state, limit=80)

        if len(state) < self.world.max_sensors:
            for position in priority_positions[:35]:
                candidate = list(state)
                candidate.append(position)
                add_neighbor(candidate)

                if len(neighbors) >= count:
                    neighbors.sort(key=self.evaluate)
                    return neighbors[:count]
        weak_sensors = sorted(
            state,
            key=lambda sensor: self.get_sensor_unique_cover_count(state, sensor)
        )
        weak_sensors = weak_sensors[:min(8, len(weak_sensors))]
        for sensor in weak_sensors:
            for position in priority_positions[:50]:
                candidate = list(state)
                index = candidate.index(sensor)
                candidate[index] = position
                add_neighbor(candidate)
                if len(neighbors) >= count:
                    neighbors.sort(key=self.evaluate)
                    return neighbors[:count]
        for sensor in weak_sensors:
            candidate = list(state)
            candidate.remove(sensor)
            add_neighbor(candidate)
            if len(neighbors) >= count:
                neighbors.sort(key=self.evaluate)
                return neighbors[:count]
        attempts = 0
        max_attempts = count * 2
        while len(neighbors) < count and attempts < max_attempts:
            candidate = self.get_neighbor(state)
            add_neighbor(candidate)
            attempts += 1
        neighbors.sort(key=self.evaluate)
        return neighbors[:count]