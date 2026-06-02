from collections import deque
from search.local_search_base import LocalSearchBase

class TabuSearch(LocalSearchBase):

    def run(self, initial_state, **kwargs):
        max_iterations = kwargs.get("max_iterations", 450)
        neighbor_count = kwargs.get("neighbor_count", 100)
        tabu_size = kwargs.get("tabu_size", 45)
        restarts = kwargs.get("restarts", 4)
        best_state = None
        best_cost = float("inf")
        evaluations = []
        states_history = []

        for restart in range(restarts):
            if restart == 0 and initial_state is not None:
                current_state = self.normalize_state(list(initial_state))
            else:
                current_state = self.initialize_state(mode="mixed")
            current_cost = self.evaluate(current_state)
            tabu_queue = deque(maxlen=tabu_size)
            tabu_set = set()
            current_key = tuple(current_state)
            tabu_queue.append(current_key)
            tabu_set.add(current_key)
            evaluations.append(current_cost)
            states_history.append(current_state)

            if current_cost < best_cost:
                best_state = current_state
                best_cost = current_cost

            for _ in range(max_iterations):
                neighbors = self.get_neighbors(current_state, neighbor_count)
                if not neighbors:
                    break
                selected_state = None
                selected_cost = float("inf")
                for neighbor in neighbors:
                    neighbor = self.normalize_state(neighbor)
                    neighbor_key = tuple(neighbor)
                    neighbor_cost = self.evaluate(neighbor)
                    is_tabu = neighbor_key in tabu_set
                    aspiration = neighbor_cost < best_cost
                    if not is_tabu or aspiration:
                        if neighbor_cost < selected_cost:
                            selected_state = neighbor
                            selected_cost = neighbor_cost
                if selected_state is None:
                    break
                current_state = selected_state
                current_cost = selected_cost
                current_key = tuple(current_state)
                if len(tabu_queue) == tabu_queue.maxlen:
                    old_key = tabu_queue.popleft()
                    tabu_set.discard(old_key)
                tabu_queue.append(current_key)
                tabu_set.add(current_key)
                evaluations.append(current_cost)
                states_history.append(current_state)
                if current_cost < best_cost:
                    best_state = current_state
                    best_cost = current_cost
        return best_state, best_cost, evaluations, states_history