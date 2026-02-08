import pygame
import math
from typing import List
from constants import *
from models import Position, Node, Obstacle, MapConfig


class Drone:
    def __init__(self, initial_position: Position):
        self.position = initial_position
        self.path: List[Node] = []
        self.color = LIGHT_BLUE

    def get_rotated_points(self, cell_size: int):
        cx = self.position.x * cell_size + cell_size // 2
        cy = self.position.y * cell_size + cell_size // 2
        size = cell_size // 3
        base_points = [(0, -size), (-size // 1.2, size), (size // 1.2, size)]
        rad = math.radians(self.position.theta + 90)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        return [
            (cx + (p[0] * cos_a - p[1] * sin_a), cy + (p[0] * sin_a + p[1] * cos_a))
            for p in base_points
        ]

    def __repr__(self):
        if not self.path:
            return "Drone - No path"
        nodes = "\n".join([f" Step {i}: {n}" for i, n in enumerate(self.path)])
        return f"Drone Path [{len(self.path)} steps]:\n{nodes}"


def draw_environment(
    screen: pygame.Surface,
    obstacles: List[Obstacle],
    init_pos: Position,
    drone: Drone,
    goal: Position,
    config: MapConfig,
    path: List[Node] = None,
    explored: List[tuple] = None,
) -> None:
    screen.fill(GRAY)
    for x in range(0, 600, config.cell_size):
        pygame.draw.line(screen, LIGHT_GRAY, (x, 0), (x, 600))
    for y in range(0, 600, config.cell_size):
        pygame.draw.line(screen, LIGHT_GRAY, (0, y), (600, y))

    if explored:
        for x, y in explored:
            pygame.draw.rect(
                screen,
                MID_GRAY,
                (
                    x * config.cell_size + 2,
                    y * config.cell_size + 2,
                    config.cell_size - 4,
                    config.cell_size - 4,
                ),
            )
    if path:
        for n in path:
            pygame.draw.rect(
                screen,
                LIGHT_GREEN,
                (
                    n.position.x * config.cell_size + 2,
                    n.position.y * config.cell_size + 2,
                    config.cell_size - 4,
                    config.cell_size - 4,
                ),
            )

    for obs in obstacles:
        pygame.draw.circle(
            screen,
            RED,
            (
                obs.center[0] * config.cell_size + config.cell_size // 2,
                obs.center[1] * config.cell_size + config.cell_size // 2,
            ),
            int(config.cell_size * obs.radius),
        )

    pygame.draw.circle(
        screen,
        ORANGE,
        (
            init_pos.x * config.cell_size + config.cell_size // 2,
            init_pos.y * config.cell_size + config.cell_size // 2,
        ),
        config.cell_size // 3,
    )
    pygame.draw.circle(
        screen,
        GREEN,
        (
            goal.x * config.cell_size + config.cell_size // 2,
            goal.y * config.cell_size + config.cell_size // 2,
        ),
        config.cell_size // 3,
    )
    pygame.draw.polygon(screen, drone.color, drone.get_rotated_points(config.cell_size))
