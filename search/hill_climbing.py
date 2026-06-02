import random
from search.local_search_base import LocalSearchBase

class HillClimbing(LocalSearchBase):

    def run(self, initial_state, **kwargs):
        max_iterations = kwargs.get("max_iterations", 350)
        neighbor_count = kwargs.get("neighbor_count", 90)
        restarts = kwargs.get("restarts", 10)
        max_sideways = kwargs.get("max_sideways", 15)
        stochastic_probability = kwargs.get("stochastic_probability", 0.25)
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
            sideways_count = 0
            evaluations.append(current_cost)
            states_history.append(current_state)
            if current_cost < best_cost:
                best_state = current_state
                best_cost = current_cost
            for _ in range(max_iterations):
                neighbors = self.get_neighbors(current_state, neighbor_count)
                if not neighbors:
                    break
                better_neighbors = []
                equal_neighbors = []
                for neighbor in neighbors:
                    cost = self.evaluate(neighbor)
                    if cost < current_cost:
                        better_neighbors.append((neighbor, cost))
                    elif cost == current_cost:
                        equal_neighbors.append((neighbor, cost))
                if better_neighbors:
                    better_neighbors.sort(key=lambda item: item[1])
                    if random.random() < stochastic_probability:
                        top_neighbors = better_neighbors[:min(5, len(better_neighbors))]
                        chosen_state, chosen_cost = random.choice(top_neighbors)
                    else:
                        chosen_state, chosen_cost = better_neighbors[0]
                    sideways_count = 0
                elif equal_neighbors and sideways_count < max_sideways:
                    chosen_state, chosen_cost = random.choice(equal_neighbors)
                    sideways_count += 1
                else:
                    break
                current_state = self.normalize_state(chosen_state)
                current_cost = chosen_cost
                evaluations.append(current_cost)
                states_history.append(current_state)
                if current_cost < best_cost:
                    best_state = current_state
                    best_cost = current_cost
        return best_state, best_cost, evaluations, states_history