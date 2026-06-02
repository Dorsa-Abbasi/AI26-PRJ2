import numpy as np


class GridWorld:

    EMPTY = '.'
    TARGET = 'T'
    OBSTACLE = 'X'

    def __init__(self, map_name):

        (
            self.grid,
            self.sensor_range,
            self.max_sensors
        ) = self.load_map(
            f"env/maps/{map_name}.txt"
        )

        self.rows = len(self.grid)
        self.cols = len(self.grid[0])

    def load_map(self, path):

        with open(path, "r") as file:

            lines = [
                line.strip()
                for line in file
                if line.strip()
            ]

        sensor_range = int(lines[-2])
        max_sensors = int(lines[-1])

        grid_lines = lines[:-2]

        grid = np.array([
            list(row)
            for row in grid_lines
        ])

        return (
            grid,
            sensor_range,
            max_sensors
        )

    def is_valid_position(self, x, y):

        if x < 0 or x >= self.rows:
            return False

        if y < 0 or y >= self.cols:
            return False

        if self.grid[x][y] == self.OBSTACLE:
            return False

        return True

    def get_targets(self):

        targets = []

        for i in range(self.rows):
            for j in range(self.cols):

                if self.grid[i][j] == self.TARGET:
                    targets.append((i, j))

        return targets
