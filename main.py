import pygame, sys, argparse, random
from constants import *
from models import Position, Obstacle, MapConfig, Node
from algorithms import a_star, calculate_theta, generate_smooth_path
from visuals import Drone, draw_environment
from typing import List, Tuple


def run_animation(
    screen: pygame.Surface,
    clock: pygame.time.Clock,
    drone: Drone,
    obstacles: List[Obstacle],
    init_pos: Position,
    goal: Position,
    config: MapConfig,
    best_path: List[Node],
    smooth_path: List[Tuple[float, float]],
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

        elif drone_idx < len(smooth_path):
            if curr_time - move_timer > 20:
                drone.position = smooth_path[drone_idx].position
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
            smooth_path,
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

    best_path, explored = a_star(initial_position, blocked, goal, config, heuristic)

    if best_path:
        points_per_segment = 15
        smooth_path = generate_smooth_path(best_path, points_per_segment)
        drone.path = calculate_theta(smooth_path)
        total_steps, tiles_visited = Drone.get_path_statistics(best_path)
        print("-" * 30)
        print(f"DRONE MISSION SUMMARY")
        print("-" * 30)
        print(f"Total Tiles Explored: {len(explored)}")
        print(f"Trajectory Steps: {total_steps}")
        print(f"Path Tiles: {tiles_visited}")
        print("-" * 30)
        print(drone.get_summary_string(points_per_segment // 3))

        run_animation(
            screen,
            clock,
            drone,
            obstacles,
            initial_position,
            goal,
            config,
            best_path,
            smooth_path,
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
            config,
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
        "obstacles": [Obstacle(2, 2, 1), Obstacle(5, 5, 0.5), Obstacle(3, 7, 1.5)],
        "initial_position": Position(0, 0, 0),
        "goal": Position(9, 9, 0),
    }

    conf_medium = {
        "grid_size": 20,
        "obstacles": [
            Obstacle(2, 2, 1),
            Obstacle(5, 5, 0.5),
            Obstacle(3, 7, 1.5),
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
            x = random.randint(3, grid_size - 7)
            y = random.randint(3, grid_size - 7)
            allowed_values = [0.5, 1.0, 1.5, 2.0]
            r = random.choice(allowed_values)
            obs.append(Obstacle(x, y, r))

        choice = random.choice(["right", "bottom"])

        if choice == "right":
            goal_x = random.randint(25, grid_size - 1)
            goal_y = random.randint(0, grid_size - 1)
        else:
            goal_x = random.randint(0, grid_size - 1)
            goal_y = random.randint(25, grid_size - 1)

        return {
            "grid_size": grid_size,
            "obstacles": obs,
            "initial_position": Position(0, 0, 0),
            "goal": Position(goal_x, goal_y, 0),
        }

    configs = {
        "easy": conf_easy,
        "medium": conf_medium,
        "hard": conf_hard,
        "random": get_conf_random(grid_size=30, num_obstacles=20),
    }

    selected_conf = configs[args.config]

    main(**selected_conf, no_anim=args.no_anim, heuristic=args.heuristic)
