import math
import heapq
from typing import List, Tuple
from models import Position, Node, MapConfig


def calculate_heuristic(curr: Position, goal: Position, method: str = "octile") -> int:
    dx, dy = abs(curr.x - goal.x), abs(curr.y - goal.y)
    if method == "octile":
        return 1000 * (dx + dy) + (1414 - 2000) * min(dx, dy)
    return int(math.sqrt(dx**2 + dy**2) * 1000)


def get_valid_neighbors(
    current_node: Node, blocked_tiles: set, config: MapConfig
) -> List[Node]:
    neighbors = []
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    for dx, dy in directions:
        nx, ny = current_node.position.x + dx, current_node.position.y + dy
        if 0 <= nx < config.grid_size and 0 <= ny < config.grid_size:
            if (nx, ny) not in blocked_tiles:
                neighbors.append(Node(Position(nx, ny)))
    return neighbors


def a_star(
    initial_pos: Position,
    blocked: set,
    goal_pos: Position,
    config: MapConfig,
    method: str,
) -> Tuple[List[Node], List[tuple]]:
    start_node = Node(initial_pos)
    start_node.g = 0
    start_node.h = calculate_heuristic(initial_pos, goal_pos, method)

    open_list = [start_node]
    visited = {}

    while open_list:
        curr = heapq.heappop(open_list)
        if curr.position.x == goal_pos.x and curr.position.y == goal_pos.y:
            path = []
            while curr:
                path.append(curr)
                curr = curr.parent
            return path[::-1], list(visited.keys())

        for neighbor in get_valid_neighbors(curr, blocked, config):
            cost = calculate_heuristic(curr.position, neighbor.position, method)
            tentative_g = curr.g + cost
            pos = (neighbor.position.x, neighbor.position.y)
            if pos not in visited or tentative_g < visited[pos]:
                visited[pos] = tentative_g
                neighbor.g, neighbor.parent = tentative_g, curr
                neighbor.h = calculate_heuristic(neighbor.position, goal_pos, method)
                heapq.heappush(open_list, neighbor)
    return [], list(visited.keys())


def calculate_theta(path: List[Node]) -> List[Node]:
    if len(path) < 2:
        return path
    for i in range(len(path)):
        if i < len(path) - 1:
            dx = path[i + 1].position.x - path[i].position.x
            dy = path[i + 1].position.y - path[i].position.y
            path[i].position.theta = math.degrees(math.atan2(dy, dx))
        else:
            path[i].position.theta = path[i - 1].position.theta
    return path
