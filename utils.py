import matplotlib.pyplot as plt
import pygame

from env.renderer import Renderer


def draw_results(algorithm_values: list, algorithm_names: list):
    plt.figure(figsize=(10, 5))

    for i in range(len(algorithm_values)):
        algorithm_value = algorithm_values[i]
        algorithm_name = algorithm_names[i]

        if len(algorithm_value) == 0:
            continue

        if len(algorithm_value) == 1:
            y_values = [algorithm_value[0], algorithm_value[0]]
            x_values = [0, 1]
        else:
            y_values = algorithm_value
            x_values = list(range(len(algorithm_value)))

        plt.plot(
            x_values,
            y_values,
            marker="o",
            markersize=3,
            label=algorithm_name
        )

    plt.title("Local Search Algorithms")
    plt.xlabel("Iteration")
    plt.ylabel("Cost")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()
    plt.close()


def get_state_report(state, world):
    targets = world.get_targets()
    covered_targets = set()
    redundant_coverage = 0

    for tx, ty in targets:
        cover_count = 0

        for sx, sy in state:
            distance = abs(sx - tx) + abs(sy - ty)

            if distance <= world.sensor_range:
                cover_count += 1

        if cover_count > 0:
            covered_targets.add((tx, ty))

        if cover_count > 1:
            redundant_coverage += cover_count - 1

    total_targets = len(targets)
    covered_count = len(covered_targets)
    uncovered_count = total_targets - covered_count
    used_sensors = len(state)

    return used_sensors, total_targets, covered_count, uncovered_count, redundant_coverage


def print_results(algorithm_states: list,
                  algorithm_costs: list,
                  algorithm_names: list,
                  world):
    for i in range(len(algorithm_states)):
        used_sensors, total_targets, covered_count, uncovered_count, redundant_coverage = get_state_report(
            algorithm_states[i],
            world
        )

        print("\n", algorithm_names[i])
        print("-" * 40)
        print("Final State        :", algorithm_states[i])
        print("Final Cost         :", algorithm_costs[i])
        print("Used Sensors       :", used_sensors)
        print("Total Targets      :", total_targets)
        print("Covered Targets    :", covered_count)
        print("Uncovered Targets  :", uncovered_count)
        print("Redundant Coverage :", redundant_coverage)


def render_history(algorithm_histories: list,
                   algorithm_evaluations: list,
                   algorithm_names: list,
                   world):
    renderer = Renderer(world)

    for i in range(len(algorithm_histories)):
        renderer.animate(
            algorithm_histories[i],
            algorithm_evaluations[i],
            algorithm_names[i],
            delay=1000,
        )

    pygame.quit()


def represent(best_states: list, best_costs: list,
              evaluations: list, histories: list,
              names: list, world):
    print_results(
        algorithm_states=best_states,
        algorithm_costs=best_costs,
        algorithm_names=names,
        world=world
    )

    draw_results(
        algorithm_values=evaluations,
        algorithm_names=names
    )

    render_history(
        algorithm_histories=histories,
        algorithm_evaluations=evaluations,
        algorithm_names=names,
        world=world
    )