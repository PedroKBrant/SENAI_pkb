from dataclasses import dataclass
from math import sqrt
from typing import List, Tuple
import argparse
import heapq
import pygame
import random
import sys

# Colors
GRAY = (30, 30, 30)
MID_GRAY = (50, 50, 50)
LIGHT_GRAY = (100, 100, 100)
LIGHT_BLUE = (90, 185, 209)
RED = (200, 50, 50)
LIGHT_GREEN = (157, 216, 123)
GREEN = (107, 166, 83)
ORANGE = (255, 155, 0)


@dataclass
class Position:
    x: int = 0
    y: int = 0
    theta: float = 0.0


@dataclass
class Node:
    position: Position
    g: int = 1_000_000_000
    h: int = 0
    parent: "Node" = None

    @property
    def f(self) -> int:
        return self.g + self.h

    # heap
    def __lt__(self, other):
        if self.f == other.f:
            return self.h < other.h  # Tie-breaker: pick the one closer to goal
        return self.f < other.f

    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        return int(self.position.x) == int(other.position.x) and int(
            self.position.y
        ) == int(other.position.y)

    def __repr__(self):
        return f"Node(pos={self.position.x, self.position.y, self.position.theta}, f={self.f:}, g={self.g:}, h={self.h:})"


def calculate_heuristic(curr: Position, goal: Position, method: str = "octile") -> int:
    # https://theory.stanford.edu/~amitp/GameProgramming/Heuristics.html
    dx = abs(curr.x - goal.x)
    dy = abs(curr.y - goal.y)
    if method == "octile":
        # Integer Octile: (Straight=1000, Diagonal=1414)
        return 1000 * (dx + dy) + (1414 - 2000) * min(dx, dy)
    else:
        # Integer Euclidean:
        return int(sqrt(dx**2 + dy**2) * 1000)


def get_valid_neighbors(current_pos: Node, blocked_tiles: set) -> List[Node]:
    neighbors = []
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    for dx, dy in directions:
        nx, ny = current_pos.position.x + dx, current_pos.position.y + dy

        if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
            if (nx, ny) not in blocked_tiles:
                neighbors.append(Node(Position(nx, ny)))

    return neighbors


def reconstruct_path(goal: Node) -> List[Node]:
    path = []
    current = goal

    while current is not None:
        path.append(current)
        current = current.parent

    return path[::-1]  # Reverse to get path from start to goal


def a_star(
    initial_position: Position,
    blocked_tiles: set,
    goal_position: Position,
    heuristic_method: str = "octile",
) -> Tuple[List[Node], List[tuple]]:
    initial_node = Node(initial_position)
    initial_node.g = 0
    initial_node.h = calculate_heuristic(initial_node.position, goal_position)

    goal_node = Node(goal_position)

    open_list = [initial_node]  # heap
    visited = {}

    while open_list:
        current_node = heapq.heappop(open_list)
        print("pop heap")
        print(current_node)
        if current_node == goal_node:  # reach the end
            return reconstruct_path(current_node), list(visited.keys())

        for neighbor in get_valid_neighbors(current_node, blocked_tiles):
            dist = calculate_heuristic(current_node.position, neighbor.position)
            tentative_g = current_node.g + dist

            neighbor_position = (neighbor.position.x, neighbor.position.y)
            if (
                neighbor_position not in visited
                or tentative_g < visited[neighbor_position]
            ):
                visited[neighbor_position] = tentative_g
                neighbor.g = tentative_g
                neighbor.h = calculate_heuristic(neighbor.position, goal_position)
                neighbor.parent = current_node
                heapq.heappush(open_list, neighbor)

    return [], list(visited.keys())  # No path found


class Obstacle:
    def __init__(self, x: int, y: int, radius: float):
        self.center = (x, y)
        self.radius = radius
        self.occupied_tiles = self._calculate_coverage()

    def _calculate_coverage(self):
        tiles = set()
        cx, cy = self.center
        for i in range(cx - int(self.radius), cx + int(self.radius) + 1):
            for j in range(cy - int(self.radius), cy + int(self.radius) + 1):
                tiles.add((i, j))
        return tiles


class Drone:
    def __init__(self, initial_position: Position):
        self.position = initial_position
        self.path = [initial_position]
        self.done = False
        self.color = LIGHT_BLUE

    def draw_drone(self):
        center_x = self.position.x * CELL_SIZE + CELL_SIZE // 2
        center_y = self.position.y * CELL_SIZE + CELL_SIZE // 2
        size = CELL_SIZE // 3

        points = [
            (center_x, center_y - size),
            (center_x - size, center_y + size),
            (center_x + size, center_y + size),
        ]
        return points

    def __repr__(self) -> str:
        if not self.path:
            return (
                f"Drone at ({self.position.x}, {self.position.y}) - No path assigned."
            )

        detailed_nodes = "\n".join(
            [f"  Step {i}: {node}" for i, node in enumerate(self.path)]
        )
        summary = f"Drone Path [{len(self.path)} steps]:"
        return f"{summary}\n{detailed_nodes}"


def draw_environment(
    screen: pygame.Surface,
    obstacles: List[Obstacle],
    initial_position: Position,
    drone: Drone,
    goal: Position,
    path: List[Node] = None,
    explored: List[tuple] = None,
) -> None:
    screen.fill(GRAY)

    # GRID
    for x in range(0, SCREEN_SIZE, CELL_SIZE):
        pygame.draw.line(screen, LIGHT_GRAY, (x, 0), (x, SCREEN_SIZE))
    for y in range(0, SCREEN_SIZE, CELL_SIZE):
        pygame.draw.line(screen, LIGHT_GRAY, (0, y), (SCREEN_SIZE, y))

    if explored:
        for x, y in explored:
            rect = pygame.Rect(
                x * CELL_SIZE + 2, y * CELL_SIZE + 2, CELL_SIZE - 4, CELL_SIZE - 4
            )
            pygame.draw.rect(screen, MID_GRAY, rect)

    if path:
        for node in path:
            rect = pygame.Rect(
                node.position.x * CELL_SIZE + 2,
                node.position.y * CELL_SIZE + 2,
                CELL_SIZE - 4,
                CELL_SIZE - 4,
            )
            pygame.draw.rect(screen, LIGHT_GREEN, rect)

    for obs in obstacles:
        obstacle_pixel_x = obs.center[0] * CELL_SIZE + CELL_SIZE // 2
        obstacle_pixel_y = obs.center[1] * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.circle(
            screen, RED, (obstacle_pixel_x, obstacle_pixel_y), CELL_SIZE * obs.radius
        )

    initial_position_pixel_x = initial_position.x * CELL_SIZE + CELL_SIZE // 2
    initial_position_pixel_y = initial_position.y * CELL_SIZE + CELL_SIZE // 2
    pygame.draw.circle(
        screen,
        ORANGE,
        (initial_position_pixel_x, initial_position_pixel_y),
        CELL_SIZE // 3,
    )

    goal_pixel_x = goal.x * CELL_SIZE + CELL_SIZE // 2
    goal_pixel_y = goal.y * CELL_SIZE + CELL_SIZE // 2
    pygame.draw.circle(screen, GREEN, (goal_pixel_x, goal_pixel_y), CELL_SIZE // 3)

    pygame.draw.polygon(screen, drone.color, drone.draw_drone())


def get_conf_random(grid_size=30, num_obstacles=15):
    obs = []
    for _ in range(num_obstacles):
        x = random.randint(2, grid_size - 3)
        y = random.randint(2, grid_size - 3)
        r = random.uniform(0.5, 2.5)
        obs.append(Obstacle(x, y, r))

    return {
        "grid_size": grid_size,
        "obstacles": obs,
        "initial_position": Position(0, 0, 0),
        "goal": Position(grid_size - 1, grid_size - 1, 0),
    }


def run_animation(
    screen: pygame.Surface,
    clock: pygame.time.Clock,
    drone: Drone,
    obstacles: List[Obstacle],
    initial_position: Position,
    goal: Position,
    best_path: List[Node],
    explored: List[tuple],
    no_anim: bool = False,
) -> None:
    visible_explored = []
    visible_path = []

    if no_anim:
        visible_explored = explored
        visible_path = best_path
        explored_idx, path_idx = len(explored), len(best_path)
    else:
        explored_idx, path_idx = 0, 0

    drone_idx = 0
    anim_timer = pygame.time.get_ticks()
    move_timer = pygame.time.get_ticks()

    ANIM_DELAY = 20 if not no_anim else 0
    DRONE_DELAY = 200

    while True:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if explored_idx < len(explored):
            if current_time - anim_timer > ANIM_DELAY:
                visible_explored.append(explored[explored_idx])
                explored_idx += 1
                anim_timer = current_time

        elif path_idx < len(best_path):
            if current_time - anim_timer > ANIM_DELAY:
                visible_path.append(best_path[path_idx])
                path_idx += 1
                anim_timer = current_time

        elif drone_idx < len(best_path):
            if current_time - move_timer > DRONE_DELAY:
                drone.position = best_path[drone_idx].position
                drone_idx += 1
                move_timer = current_time

        draw_environment(
            screen,
            obstacles,
            initial_position,
            drone,
            goal,
            visible_path,
            visible_explored,
        )
        pygame.display.flip()
        clock.tick(60)


def main(
    grid_size: int,
    obstacles: List[Obstacle],
    initial_position: Position,
    goal: Position,
    no_anim: bool = False,
    heuristic: str = "octile",
) -> None:
    global GRID_SIZE, CELL_SIZE, SCREEN_SIZE
    GRID_SIZE = grid_size
    SCREEN_SIZE = 600
    CELL_SIZE = SCREEN_SIZE // GRID_SIZE

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
    pygame.display.set_caption(f"Drone Pathfinding - {GRID_SIZE}x{GRID_SIZE}")
    clock = pygame.time.Clock()

    drone = Drone(
        Position(initial_position.x, initial_position.y, initial_position.theta)
    )
    blocked_tiles = {tile for obs in obstacles for tile in obs.occupied_tiles}

    best_path, explored = a_star(initial_position, blocked_tiles, goal, heuristic)
    print("Explored Nodes:", explored)
    print("Total Nós visitados", len(explored))

    if best_path:
        drone.path = best_path
        print(drone)
        run_animation(
            screen,
            clock,
            drone,
            obstacles,
            initial_position,
            goal,
            best_path,
            explored,
            no_anim,
        )
    else:
        print("No path found!")
        draw_environment(
            screen, obstacles, initial_position, drone, goal, explored=explored
        )
        pygame.display.flip()
        pygame.time.wait(3000)


conf_easy = {
    "grid_size": 10,
    "obstacles": [Obstacle(3, 3, 1), Obstacle(5, 5, 0.5), Obstacle(7, 3, 1.5)],
    "initial_position": Position(0, 0, 0),
    "goal": Position(9, 9, 0),
}

conf_medium = {
    "grid_size": 20,
    "obstacles": [
        Obstacle(3, 3, 1),
        Obstacle(5, 5, 0.5),
        Obstacle(7, 3, 1.5),
        Obstacle(12, 15, 4),
        Obstacle(3, 14, 3),
        Obstacle(16, 8, 1.5),
    ],
    "initial_position": Position(0, 0, 0),
    "goal": Position(19, 19, 0),
}

conf_hard = {
    "grid_size": 40,
    "obstacles": [
        Obstacle(5, 5, 2),
        Obstacle(15, 5, 3),
        Obstacle(25, 15, 4),
        Obstacle(10, 25, 3),
        Obstacle(30, 30, 5),
        Obstacle(12, 15, 2),
        Obstacle(35, 10, 2),
        Obstacle(5, 35, 2),
    ],
    "initial_position": Position(0, 0, 0),
    "goal": Position(39, 39, 0),
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Drone Pathfinding Simulation")
    parser.add_argument(
        "config",
        nargs="?",
        default="easy",
        choices=["easy", "medium", "hard", "random"],
        help="The configuration difficulty to run (default: easy)",
    )
    parser.add_argument(
        "--no-anim",
        action="store_true",
        help="Skip the step-by-step pathfinding animation",
    )
    parser.add_argument(
        "--heuristic",
        default="octile",
        choices=["octile", "euclidean"],
        help="The heuristic method to use (default: octile)",
    )
    args = parser.parse_args()
    configs = {
        "easy": conf_easy,
        "medium": conf_medium,
        "hard": conf_hard,
        "random": get_conf_random(grid_size=30, num_obstacles=20),
    }
    selected_conf = configs[args.config]
    main(**selected_conf, no_anim=args.no_anim, heuristic=args.heuristic)
