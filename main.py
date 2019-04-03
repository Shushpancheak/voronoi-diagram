#!python3
"""
Terrain Generator.
-------------------------
Author: Maximelian Mumladze.
"""

import sys
import numpy as np
import matplotlib.tri
import time
import pygame
import logging
import const
import voronoi
import math


class World:
    def __init__(self, width=const.DEFAULT_WIDTH, height=const.DEFAULT_HEIGHT):
        pass

if __name__ == '__main__':
    pygame.init()

    # Loop until the user clicks the close button.
    done = False

    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s \
                        - %(message)s',
                        level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    # for displaying text in the game
    pygame.font.init()
    screen = pygame.display.set_mode(const.DEFAULT_RESOLUTION)
    pygame.display.set_caption("TerraGen")
    world = World()

    # Initial random points. Two-dimensional array.
    points = np.random.rand(const.POINTS_NUMBER, 2) * const.POINTS_MODIFIER

    # Using voronoi diagram to make polygons around points.
    lines = voronoi.get_voronoi_polygons(points)

    # Making points suitable for draw.circle.
    points = [(int(point[0]), int(point[1])) for point in points]

    while not done:
        clock.tick(10)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        screen.fill(const.BLACK)

        for point in points:
            pygame.draw.circle(screen, const.BLUE, point, 5, 5)
        for segment in lines:
            pygame.draw.line(screen, const.RED, segment[0], segment[1], 3)

        pygame.display.flip()

pygame.quit()
