"""
University: University of Isfahan
Faculty: Mathematics and Statistics
Branch: Computer Science
Course: Artificial Intelligence
Professor: Dr. Faria Nasiri Mofakham
TAs: MehrAzin Marzough, Mohammad Karimi, Anahita Honarmandian
Project: Implementing Local Search Algorithms for a Sensor Placement Optimization Problem
"""
from env.grid_world import GridWorld
from search.hill_climbing import HillClimbing
from search.simulated_annealing import SimulatedAnnealing
from utils import represent
from search.tabu_search import TabuSearch
from search.beam_search import BeamSearch

import re
import matplotlib
matplotlib.use("TkAgg")

def run_algorithms(world, initial_state, algorithm_classes):
    best_states = []
    best_costs = []
    evaluations = []
    histories = []
    names = []

    for algorithm_class in algorithm_classes:
        name = re.sub(r'(?<!^)([A-Z])', r' \1', algorithm_class.__name__)
        names.append(name)
        
        algorithm_instance = algorithm_class(world)
        
        print(f"\nRunning {name}...")
        
        state, cost, evals, hist = algorithm_instance.run(initial_state)
        
        best_states.append(state)
        best_costs.append(cost)
        evaluations.append(evals)
        histories.append(hist)

    represent(
        best_states=best_states,
        best_costs=best_costs,
        evaluations=evaluations,
        histories=histories,
        names=names,
        world=world
    )

if __name__ == "__main__":

    algorithm_classes = [
        HillClimbing,
        SimulatedAnnealing,
        TabuSearch,
        BeamSearch
    ]

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
        print("\n" + "=" * 60)
        print(f"Current Map: {map_name}")
        print("=" * 60)

        world = GridWorld(map_name)

        initial_state = HillClimbing(world).initialize_state()
        run_algorithms(world, initial_state, algorithm_classes)