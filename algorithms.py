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


def get_catmull_rom_point(
    p0: Tuple[float, float],
    p1: Tuple[float, float],
    p2: Tuple[float, float],
    p3: Tuple[float, float],
    t: float,
) -> Tuple[float, float]:
    """
    Calculates the (x, y) position for a point 't' between p1 and p2.
    """
    t2 = t * t
    t3 = t2 * t

    # Catmull-Rom basis functions
    f1 = -0.5 * t3 + t2 - 0.5 * t
    f2 = 1.5 * t3 - 2.5 * t2 + 1.0
    f3 = -1.5 * t3 + 2.0 * t2 + 0.5 * t
    f4 = 0.5 * t3 - 0.5 * t2

    x = p0[0] * f1 + p1[0] * f2 + p2[0] * f3 + p3[0] * f4
    y = p0[1] * f1 + p1[1] * f2 + p2[1] * f3 + p3[1] * f4

    return (x, y)


def get_catmull_rom_point(
    p0: Tuple[float, float],
    p1: Tuple[float, float],
    p2: Tuple[float, float],
    p3: Tuple[float, float],
    t: float,
) -> Tuple[float, float]:
    """
    Calculates the (x, y) position for a point 't' between p1 and p2.
    """
    t2 = t * t
    t3 = t2 * t

    f1 = -0.5 * t3 + t2 - 0.5 * t
    f2 = 1.5 * t3 - 2.5 * t2 + 1.0
    f3 = -1.5 * t3 + 2.0 * t2 + 0.5 * t
    f4 = 0.5 * t3 - 0.5 * t2

    x = p0[0] * f1 + p1[0] * f2 + p2[0] * f3 + p3[0] * f4
    y = p0[1] * f1 + p1[1] * f2 + p2[1] * f3 + p3[1] * f4

    return (x, y)


def generate_smooth_path(
    path: List[Node], points_per_segment: int = 20
) -> List[Node]:
    if len(path) < 2:
        return path

    coords = [(float(n.position.x), float(n.position.y)) for n in path]
    f_values = [n.f for n in path]

    coords.insert(0, coords[0])
    coords.append(coords[-1])

    smooth_nodes: List[Node] = []
    
    # Generate interpolated nodes
    for i in range(1, len(coords) - 2):
        p0, p1, p2, p3 = coords[i - 1], coords[i], coords[i + 1], coords[i + 2]
        
        g_start, h_start = path[i-1].g, path[i-1].h
        g_end, h_end = path[i].g, path[i].h

        for j in range(points_per_segment):
            t = j / points_per_segment
            x, y = get_catmull_rom_point(p0, p1, p2, p3, t)
            
            new_node = Node(position=Position(x=x, y=y))
            new_node.g = int(g_start + (g_end - g_start) * t)
            new_node.h = int(h_start + (h_end - h_start) * t)
            
            smooth_nodes.append(new_node)

    final_node = path[-1]
    smooth_nodes.append(Node(
        position=Position(x=final_node.position.x, y=final_node.position.y),
        g=final_node.g,
        h=final_node.h
    ))

    return smooth_nodes
