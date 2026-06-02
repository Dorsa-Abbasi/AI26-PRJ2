import pygame
import time

from env.config import *


class Renderer:

    def __init__(self, world):

        pygame.init()

        self.world = world

        self.width = world.cols * CELL_SIZE
        self.height = world.rows * CELL_SIZE + 80

        self.screen = pygame.display.set_mode(
            (self.width, self.height)
        )

        pygame.display.set_caption(WINDOW_TITLE)

        self.font = pygame.font.SysFont('Arial', 24)

    def draw(self,
             state,
             sensor_range,
             iteration,
             cost,
             algorithm_name):

        self.screen.fill(WHITE)

        for i in range(self.world.rows):
            for j in range(self.world.cols):

                x = j * CELL_SIZE
                y = i * CELL_SIZE

                rect = pygame.Rect(
                    x,
                    y,
                    CELL_SIZE - MARGIN,
                    CELL_SIZE - MARGIN
                )

                value = self.world.grid[i][j]

                color = WHITE

                if value == 'X':
                    color = GRAY

                elif value == 'T':
                    color = RED

                pygame.draw.rect(
                    self.screen,
                    color,
                    rect
                )

                pygame.draw.rect(
                    self.screen,
                    BLACK,
                    rect,
                    1
                )

        for (sx, sy) in state:
            center_x = sy * CELL_SIZE + CELL_SIZE // 2
            center_y = sx * CELL_SIZE + CELL_SIZE // 2

            # coverage area (manhattan distance)
            for i in range(self.world.rows):
                for j in range(self.world.cols):

                    distance = abs(sx - i) + abs(sy - j)

                    if distance <= sensor_range:
                        overlay = pygame.Surface(
                            (
                                CELL_SIZE - MARGIN,
                                CELL_SIZE - MARGIN
                            ),
                            pygame.SRCALPHA
                        )

                        overlay.fill((50, 100, 255, 60))

                        self.screen.blit(
                            overlay,
                            (
                                j * CELL_SIZE,
                                i * CELL_SIZE
                            )
                        )

            # sensor
            pygame.draw.circle(
                self.screen,
                BLUE,
                (center_x, center_y),
                CELL_SIZE // 4
            )

        text = (
            f'{algorithm_name} | '
            f'Iteration: {iteration} | '
            f'Cost: {cost}'
        )

        surface = self.font.render(
            text,
            True,
            BLACK
        )

        self.screen.blit(
            surface,
            (10, self.world.rows * CELL_SIZE + 20)
        )

        pygame.display.flip()

    def animate(self,
                states_history,
                evaluations,
                algorithm_name,
                delay=50):

        for iteration, state in enumerate(states_history):

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    return

            self.draw(
                state,
                self.world.sensor_range,
                iteration,
                evaluations[iteration],
                algorithm_name
            )

            pygame.time.delay(delay)
