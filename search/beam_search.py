import random
from search.local_search_base import LocalSearchBase

class BeamSearch(LocalSearchBase):

    def run(self, initial_state, **kwargs):
        max_iterations = kwargs.get("max_iterations", 700)
        beam_width = kwargs.get("beam_width", 10)
        neighbor_count = kwargs.get("neighbor_count", 100)
        restarts = kwargs.get("restarts", 6)
        patience = kwargs.get("patience", 100)
        best_state = None
        best_cost = float("inf")
        evaluations = []
        states_history = []

        for restart in range(restarts):
            beam = []
            seen = set()

            def add_to_beam(state):
                state = self.normalize_state(state)
                key = tuple(state)
                if key in seen:
                    return
                if not self.state_is_legal(state):
                    return
                seen.add(key)
                beam.append(state)
    
            if restart == 0 and initial_state is not None:
                add_to_beam(list(initial_state))
            
            while len(beam) < beam_width:
                if random.random() < 0.7:
                    state = self.initialize_state(mode="mixed")
                else:
                    state = self.initialize_state(mode="random")
                add_to_beam(state)
            beam_costs = [(state, self.evaluate(state)) for state in beam]
            beam_costs.sort(key=lambda item: item[1])
            current_best_state, current_best_cost = beam_costs[0]
            evaluations.append(current_best_cost)
            states_history.append(current_best_state)

            if current_best_cost < best_cost:
                best_state = current_best_state
                best_cost = current_best_cost
            
            no_improvement_count = 0
            for _ in range(max_iterations):
                candidates = []
                candidate_keys = set()

                def add_candidate(state):
                    state = self.normalize_state(state)
                    key = tuple(state)
                    if key in candidate_keys:
                        return
                    if not self.state_is_legal(state):
                        return
                    candidate_keys.add(key)
                    candidates.append(state)
                
                for state in beam:
                    add_candidate(state)
                for state in beam:
                    neighbors = self.get_neighbors(state, neighbor_count)
                    for neighbor in neighbors:
                        add_candidate(neighbor)
                if not candidates:
                    break
                candidate_costs = [
                    (state, self.evaluate(state))
                    for state in candidates
                ]
                candidate_costs.sort(key=lambda item: item[1])

                new_beam = [
                    state
                    for state, _ in candidate_costs[:beam_width]
                ]
                iteration_best_state, iteration_best_cost = candidate_costs[0]
                evaluations.append(iteration_best_cost)
                states_history.append(iteration_best_state)
                
                if iteration_best_cost < best_cost:
                    best_state = iteration_best_state
                    best_cost = iteration_best_cost
                    no_improvement_count = 0
                else:
                    no_improvement_count += 1
                beam = new_beam
                if no_improvement_count >= patience:
                    break
        return best_state, best_cost, evaluations, states_history