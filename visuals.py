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

    def get_summary_path(self, step_size: int):
        return self.path[::step_size]

    def get_summary_string(self, step_size: int) -> str:
        summary_nodes = self.get_summary_path(step_size)
        detailed_nodes = "\n".join(
            [f"  Waypoint {i}: {node}" for i, node in enumerate(summary_nodes)]
        )
        return f"Drone Path Summary ({len(summary_nodes)} Waypoints):\n{detailed_nodes}"

    def get_path_statistics(smooth_path: List[Node]):
        total_steps = len(smooth_path)
        unique_tiles = list(
            {
                (int(round(n.position.x)), int(round(n.position.y))): None
                for n in smooth_path
            }.keys()
        )
        return total_steps, unique_tiles


def draw_environment(
    screen: pygame.Surface,
    obstacles: List[Obstacle],
    init_pos: Position,
    drone: Drone,
    goal: Position,
    config: MapConfig,
    path: List[Node] = None,
    explored: List[tuple] = None,
    smooth_path=None,
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

    if path and len(path) > 1:
        raw_points = [
            (
                n.position.x * config.cell_size + config.cell_size // 2,
                n.position.y * config.cell_size + config.cell_size // 2,
            )
            for n in path
        ]
        pygame.draw.lines(screen, LIGHT_GRAY, False, raw_points, 5)

        for p in raw_points:
            pygame.draw.circle(screen, LIGHT_GRAY, p, 3)

    if smooth_path and len(smooth_path) > 1:
        smooth_points = [
            (
                node.position.x * config.cell_size + config.cell_size // 2,
                node.position.y * config.cell_size + config.cell_size // 2,
            )
            for node in smooth_path
        ]
        pygame.draw.lines(screen, LIGHT_BLUE, False, smooth_points, 3)

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
