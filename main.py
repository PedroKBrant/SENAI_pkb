import pygame, sys, argparse, random
from constants import *
from models import Position, Obstacle, MapConfig, Node
from algorithms import a_star, calculate_theta
from visuals import Drone, draw_environment
from typing import List


def run_animation(
    screen: pygame.Surface,
    clock: pygame.time.Clock,
    drone: Drone,
    obstacles: List[Obstacle],
    init_pos: Position,
    goal: Position,
    config: MapConfig,
    best_path: List[Node],
    explored: List[tuple],
    no_anim: bool = False,
):
    visible_explored, visible_path = (explored, best_path) if no_anim else ([], [])
    explored_idx, path_idx, drone_idx = (
        (len(explored), len(best_path), 0) if no_anim else (0, 0, 0)
    )
    anim_timer = move_timer = pygame.time.get_ticks()

    while True:
        curr_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if explored_idx < len(explored) and curr_time - anim_timer > 10:
            visible_explored.append(explored[explored_idx])
            explored_idx += 1
            anim_timer = curr_time

        elif path_idx < len(best_path) and curr_time - anim_timer > 20:
            visible_path.append(best_path[path_idx])
            path_idx += 1
            anim_timer = curr_time

        elif drone_idx < len(best_path) and curr_time - move_timer > 200:
            drone.position = best_path[drone_idx].position
            drone_idx += 1
            move_timer = curr_time

        draw_environment(
            screen,
            obstacles,
            init_pos,
            drone,
            goal,
            config,
            visible_path,
            visible_explored,
        )
        pygame.display.flip()
        clock.tick(60)


def main(
    grid_size, obstacles, initial_position, goal, no_anim=False, heuristic="octile"
):
    screen_size = 600
    config = MapConfig(
        grid_size=grid_size, cell_size=screen_size // grid_size, screen_size=screen_size
    )

    pygame.init()
    screen = pygame.display.set_mode((config.screen_size, config.screen_size))
    pygame.display.set_caption(f"Drone Pathfinding - {grid_size}x{grid_size}")
    clock = pygame.time.Clock()

    drone = Drone(Position(initial_position.x, initial_position.y))
    blocked = {t for obs in obstacles for t in obs.occupied_tiles}

    path, explored = a_star(initial_position, blocked, goal, config, heuristic)

    if path:
        drone.path = calculate_theta(path)
        print(drone)
        run_animation(
            screen,
            clock,
            drone,
            obstacles,
            initial_position,
            goal,
            config,
            path,
            explored,
            no_anim,
        )
    else:
        print("No path found!")
        draw_environment(
            screen,
            obstacles,
            initial_position,
            drone,
            goal,
            explored=explored,
        )
        pygame.display.flip()
        pygame.time.wait(3000)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Drone Pathfinding Simulation")
    parser.add_argument(
        "config",
        nargs="?",
        default="easy",
        choices=["easy", "medium", "hard", "random"],
    )
    parser.add_argument("--no-anim", action="store_true")
    parser.add_argument(
        "--heuristic", default="octile", choices=["octile", "euclidean"]
    )
    args = parser.parse_args()

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

    configs = {
        "easy": conf_easy,
        "medium": conf_medium,
        "hard": conf_hard,
        "random": get_conf_random(grid_size=30, num_obstacles=20),
    }

    selected_conf = configs[args.config]

    main(**selected_conf, no_anim=args.no_anim, heuristic=args.heuristic)
