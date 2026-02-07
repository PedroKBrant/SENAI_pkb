from dataclasses import dataclass
import pygame
import sys
from typing import List
import heapq
from math import sqrt
from dataclasses import dataclass

# Configuration
SCREEN_SIZE = 600
GRID_SIZE = 20
CELL_SIZE = SCREEN_SIZE // GRID_SIZE

#Colors 
GRAY = (30, 30, 30)
LIGHT_GRAY = (100, 100, 100)
LIGHT_BLUE = (90,185,209)
RED = (200, 50, 50)
GREEN = (127,186,103)
YELLOW = (255, 255, 0)
    
@dataclass
class Position:
    x: float = 0.0
    y: float = 0.0
    theta: float = 0.0
    
@dataclass
class Node:
    position: Position
    g: float = float('inf')
    h: float = 0.0
    parent = None
    
    @property   
    def f(self) -> float:
        return self.g + self.h
    #heap
    def __lt__(self, other):
        return self.f < other.f
    
    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        return (int(self.position.x) == int(other.position.x) and 
                int(self.position.y) == int(other.position.y))
  
      
def calculate_heuristic(curr: Position, goal: Position) -> float:
  # Euclidean Distance
  return sqrt((curr.x - goal.x)**2 +(curr.y - goal.y)**2)


def get_valid_neighbors(current_pos: Position, blocked_tiles: set) -> List[Position]:
  neighbors = []
  directions = [
          (0, 1), (0, -1), (1, 0), (-1, 0),
          (1, 1), (1, -1), (-1, 1), (-1, -1)
      ]

  for dx, dy in directions:
      nx, ny = current_pos.x + dx, current_pos.y + dy

      if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
          if (nx, ny) not in blocked_tiles:
              neighbors.append(Position(nx, ny))
              
  return neighbors
  
def reconstruct_path(goal: Node) -> List[Position]:
  path = []
  current = goal
  
  while current is not None:
      path.append(current.position)
      current = current.parent
       
  return path[::-1]  # Reverse to get path from start to goal

def a_star(initial_position: Position, blocked_tiles: set, goal_position: Position) -> List[Position]:
    initial_node = Node(initial_position)
    initial_node.g = 0
    initial_node.h = calculate_heuristic(initial_node.position, goal_position)
    
    goal_node = Node(goal_position)
    
    open_list = [initial_node] # heap
    visited = {}
    
    while open_list:
        current_node = heapq.heappop(open_list)
        
        if current_node == goal_node:# reach the end
            return reconstruct_path(current_node)
        
        for neighbor in get_valid_neighbors(current_node.position, blocked_tiles):
            dist = calculate_heuristic(current_node.position, neighbor)
            tentative_g = current_node.g + dist
            print(neighbor)
            
            neighbor_position = (neighbor.x, neighbor.y)
            if neighbor_position not in visited or tentative_g < visited[neighbor_position]:
                visited[neighbor_position] = tentative_g
                neighbor_node = Node(neighbor)
                neighbor_node.g = tentative_g
                neighbor_node.h = calculate_heuristic(neighbor, goal_position)
                neighbor_node.parent = current_node
                heapq.heappush(open_list, neighbor_node)
                
    return [] # No path found
    
class Obstacle:
    def __init__(self, x, y, radius):
        self.center = (x, y)
        self.radius = radius
        self.occupied_tiles = self._calculate_coverage()

    def _calculate_coverage(self):
        tiles = set()
        cx, cy = self.center
        for i in range(cx - int(self.radius), cx + int(self.radius)+1):
            for j in range(cy - int(self.radius), cy + int(self.radius)+1):
                tiles.add((i, j))
        return tiles
          
class Drone():
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
        (center_x + size, center_y + size) 
    ]
    return points
    
  def __repr__(self):
    return f"Drone Path: {self.path}"


def draw_environment(screen, obstacles, initial_position, drone, goal):
  screen.fill(GRAY)

  #GRID
  for x in range(0, SCREEN_SIZE, CELL_SIZE):
      pygame.draw.line(screen, LIGHT_GRAY, (x, 0), (x, SCREEN_SIZE))
  for y in range(0, SCREEN_SIZE, CELL_SIZE):
      pygame.draw.line(screen, LIGHT_GRAY, (0, y), (SCREEN_SIZE, y))
      
  for obs in obstacles:
      obstacle_pixel_x = obs.center[0] * CELL_SIZE + CELL_SIZE // 2
      obstacle_pixel_y = obs.center[1] * CELL_SIZE + CELL_SIZE // 2
      pygame.draw.circle(screen, RED, (obstacle_pixel_x, obstacle_pixel_y), CELL_SIZE * obs.radius)
    
  initial_position_pixel_x = initial_position.x * CELL_SIZE + CELL_SIZE // 2
  initial_position_pixel_y = initial_position.y * CELL_SIZE + CELL_SIZE // 2
  pygame.draw.circle(screen, YELLOW, (initial_position_pixel_x, initial_position_pixel_y), CELL_SIZE // 2)
  
  goal_pixel_x = goal.x * CELL_SIZE + CELL_SIZE // 2
  goal_pixel_y = goal.y * CELL_SIZE + CELL_SIZE // 2
  pygame.draw.circle(screen, GREEN, (goal_pixel_x, goal_pixel_y), CELL_SIZE // 2)
  
  pygame.draw.polygon(screen, drone.color, drone.draw_drone())
      

def main(obstacles = (0,0), 
         initial_position = Position(0,0,0), 
         goal = Position(1,1,0)):
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
    pygame.display.set_caption("Drone Pathfinding Test")
    clock = pygame.time.Clock()
    
    drone = Drone(Position(initial_position.x, initial_position.y, initial_position.theta))

    blocked_tiles = set()
    for obs in obstacles:
        for tile in obs.occupied_tiles:
            blocked_tiles.add(tile)
            
    best_path = a_star(initial_position, blocked_tiles, goal)       
    last_move_time = pygame.time.get_ticks() 
    delay = 400 
    i=0
    while True: 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        current_time = pygame.time.get_ticks()
        if current_time - last_move_time > delay:
          if i < len(best_path):
            drone.position = best_path[i]
            i+=1
          last_move_time = current_time
      
        draw_environment(screen, obstacles, initial_position, drone, goal)
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main(obstacles=[Obstacle(3, 3, 1), Obstacle(5, 5, 0.5), Obstacle(7, 3, 1.5), Obstacle(12, 15, 4), Obstacle(3, 14, 3), Obstacle(16, 8, 1.5)],
         initial_position=Position(0,0,0),
         goal=Position(19,19,0))
