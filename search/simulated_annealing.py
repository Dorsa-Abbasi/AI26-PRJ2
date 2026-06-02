import math
import random
from search.local_search_base import LocalSearchBase

class SimulatedAnnealing(LocalSearchBase):

    def run(self, initial_state, **kwargs):
        max_iterations = kwargs.get("max_iterations", 1500)
        initial_temperature = kwargs.get("initial_temperature", 500)
        cooling_rate = kwargs.get("cooling_rate", 0.99)
        min_temperature = kwargs.get("min_temperature", 1)
        restarts = kwargs.get("restarts", 3)
        best_state = None
        best_cost = float("inf")
        evaluations = []
        states_history = []

        for restart in range(restarts):
            if restart == 0 and initial_state is not None:
                current_state = self.normalize_state(list(initial_state))
            else:
                current_state = self.initialize_state(mode="random")
            current_cost = self.evaluate(current_state)
            temperature = initial_temperature
            evaluations.append(current_cost)
            states_history.append(current_state)
            if current_cost < best_cost:
                best_state = current_state
                best_cost = current_cost
            
            for _ in range(max_iterations):
                if temperature <= min_temperature:
                    break
                next_state = self.get_neighbor(current_state)
                next_cost = self.evaluate(next_state)
                delta = next_cost - current_cost
                if delta < 0:
                    current_state = next_state
                    current_cost = next_cost
                else:
                    probability = math.exp(-delta / temperature)
                    if random.random() < probability:
                        current_state = next_state
                        current_cost = next_cost
                evaluations.append(current_cost)
                states_history.append(current_state)
                if current_cost < best_cost:
                    best_state = current_state
                    best_cost = current_cost
                temperature *= cooling_rate
        return best_state, best_cost, evaluations, states_history