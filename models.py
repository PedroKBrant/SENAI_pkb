from dataclasses import dataclass
from typing import Set, Tuple


@dataclass
class MapConfig:
    grid_size: int
    cell_size: int
    screen_size: int = 600


@dataclass
class Position:
    x: float = 0.0
    y: float = 0.0
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

    def __lt__(self, other):
        if self.f == other.f:
            return self.h < other.h
        return self.f < other.f

    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        return int(self.position.x) == int(other.position.x) and int(
            self.position.y
        ) == int(other.position.y)

    def __repr__(self):
        pos_str = f"({self.position.x:.2f}, {self.position.y:.2f}, {self.position.theta:.1f}°)"
        return f"Node(pos={pos_str}, f={self.f/1000}, g={self.g/1000}, h={self.h/1000})"


class Obstacle:
    def __init__(self, x: int, y: int, radius: float):
        self.center = (x, y)
        self.radius = radius
        self.occupied_tiles = self._calculate_coverage()

    def _calculate_coverage(self) -> Set[Tuple[int, int]]:
        tiles = set()
        cx, cy = self.center
        for i in range(cx - int(self.radius), cx + int(self.radius) + 1):
            for j in range(cy - int(self.radius), cy + int(self.radius) + 1):
                tiles.add((i, j))
        return tiles
