import random


def random_position(world):

    while True:

        x = random.randint(0, world.rows - 1)
        y = random.randint(0, world.cols - 1)

        if world.is_valid_position(x, y):
            return x, y