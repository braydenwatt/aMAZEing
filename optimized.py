import pygame
import numpy as np
import random
from typing import List, Tuple, Optional, Set


class MazeGenerator:
    def __init__(self, width: int, height: int, cell_size: int = 20):
        """
        Initialize Maze Generator

        Args:
            width (int): Number of cells wide
            height (int): Number of cells high
            cell_size (int): Size of each cell in pixels
        """
        self.width = width
        self.height = height
        self.cell_size = cell_size

        # Calculate maze grid dimensions
        self.grid_width = 2 * width + 1
        self.grid_height = 2 * height + 1

        # Possible movement directions
        self.directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        # Initialize maze grid
        self.maze = np.ones((self.grid_height, self.grid_width), dtype=np.uint8)

        # Entrance and exit coordinates
        self.entrance = None
        self.exit = None

    def _is_valid_cell(self, x: int, y: int) -> bool:
        """Check if cell is within maze bounds"""
        return (0 < x < self.grid_width - 1 and
                0 < y < self.grid_height - 1)

    def generate_wilson(self, visualize=False) -> np.ndarray:
        """
        Generate maze using Wilson's algorithm (Loop-Erased Random Walk)

        Returns:
            numpy.ndarray: Generated maze grid
        """
        # All possible cells in the maze
        all_cells = [(x * 2 + 1, y * 2 + 1)
                     for y in range(self.height)
                     for x in range(self.width)]

        # Track visited and unvisited cells
        unvisited = set(all_cells)
        visited = set()

        # Keep track of finalized paths
        finalized_paths = set()
        finalized_walls = set()

        # Choose random start cell
        start_cell = random.choice(all_cells)
        unvisited.remove(start_cell)
        visited.add(start_cell)

        while unvisited:
            # Start random walk from unvisited cell
            current = random.choice(list(unvisited))
            path = [current]
            path_set = set(path)
            path_walls = []

            # Continue walk until hitting a visited cell
            while current in unvisited:
                # Randomize directions
                directions = random.sample(self.directions, len(self.directions))

                for dx, dy in directions:
                    next_x = current[0] + 2 * dx
                    next_y = current[1] + 2 * dy

                    if self._is_valid_cell(next_x, next_y):
                        next_cell = (next_x, next_y)

                        wall_x = (current[0] + next_cell[0]) // 2
                        wall_y = (current[1] + next_cell[1]) // 2
                        wall = (wall_x, wall_y)

                        # Handle loop erasure
                        if next_cell in path_set:
                            loop_index = path.index(next_cell)
                            path = path[:loop_index + 1]
                            path_walls = path_walls[:loop_index]
                            path_set = set(path)
                        else:
                            path.append(next_cell)
                            path_set.add(next_cell)
                            path_walls.append(wall)

                        current = next_cell
                        break

            # Carve path
            if len(path) > 1:
                for i in range(len(path) - 1):
                    current, next_cell = path[i], path[i + 1]

                    # Calculate wall position
                    wall_x = (current[0] + next_cell[0]) // 2
                    wall_y = (current[1] + next_cell[1]) // 2

                    # Create passage
                    self.maze[current[1], current[0]] = 0
                    self.maze[next_cell[1], next_cell[0]] = 0
                    self.maze[wall_y, wall_x] = 0

                    # Update visited status
                    visited.add(current)
                    visited.add(next_cell)
                    if current in unvisited:
                        unvisited.remove(current)
                    if next_cell in unvisited:
                        unvisited.remove(next_cell)

        return self.maze

    def add_entrance_exit(self) -> None:
        """Add entrance and exit to maze borders"""
        # Find valid entrance and exit positions
        left_candidates = [
            (y, 0) for y in range(1, self.grid_height - 1)
            if self.maze[y, 1] == 0 and self.maze[y, 0] == 1
        ]
        right_candidates = [
            (y, self.grid_width - 1) for y in range(1, self.grid_height - 1)
            if self.maze[y, -2] == 0 and self.maze[y, -1] == 1
        ]

        if not left_candidates or not right_candidates:
            raise ValueError("No valid entrance/exit positions")

        # Randomly select entrance and exit
        self.entrance = random.choice(left_candidates)
        self.exit = random.choice(right_candidates)

        # Mark entrance and exit
        self.maze[self.entrance[0], self.entrance[1]] = 2
        self.maze[self.exit[0], self.exit[1]] = 3


class MazeSolver:
    def __init__(self, maze: np.ndarray):
        """
        Initialize Maze Solver

        Args:
            maze (numpy.ndarray): Maze grid to solve
        """
        self.maze = maze.copy()
        self.directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        self.entrance = None
        self.exit = None

        # Find entrance and exit
        for y in range(maze.shape[0]):
            for x in range(maze.shape[1]):
                if maze[y, x] == 2:
                    self.entrance = (x, y)
                elif maze[y, x] == 3:
                    self.exit = (x, y)

    def solve_flood_fill(self) -> Optional[List[Tuple[int, int]]]:
        """
        Solve maze using flood-fill algorithm

        Returns:
            Optional list of path coordinates, or None if no path found
        """
        if not self.entrance or not self.exit:
            return None

        queue = [self.entrance]
        visited = set([self.entrance])
        parents = {self.entrance: None}

        while queue:
            current = queue.pop(0)

            if current == self.exit:
                break

            for dx, dy in self.directions:
                nx, ny = current[0] + dx, current[1] + dy
                neighbor = (nx, ny)

                if (0 <= nx < self.maze.shape[1] and
                        0 <= ny < self.maze.shape[0] and
                        neighbor not in visited and
                        self.maze[ny, nx] in [0, 3]):
                    queue.append(neighbor)
                    visited.add(neighbor)
                    parents[neighbor] = current

        # Reconstruct path
        if self.exit not in parents:
            return None

        path = []
        current = self.exit
        while current != self.entrance:
            path.append(current)
            current = parents[current]
        path.append(self.entrance)
        path.reverse()

        return path


class MazeVisualization:
    def __init__(self, maze: np.ndarray, cell_size: int = 20):
        """
        Initialize Maze Visualization

        Args:
            maze (numpy.ndarray): Maze grid to visualize
            cell_size (int): Size of each cell in pixels
        """
        pygame.init()

        self.maze = maze
        self.cell_size = cell_size

        # Create screen
        self.screen_size = (
            maze.shape[1] * cell_size,
            maze.shape[0] * cell_size
        )
        self.screen = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption("Maze Generator and Solver")

    def draw(self, path: Optional[List[Tuple[int, int]]] = None) -> None:
        """
        Draw the maze with optional solution path

        Args:
            path (Optional[List[Tuple[int, int]]]): Solution path coordinates
        """
        self.screen.fill((0, 0, 0))  # Black background

        for y in range(self.maze.shape[0]):
            for x in range(self.maze.shape[1]):
                cell_type = self.maze[y, x]
                color = {
                    0: (255, 255, 255),  # Path (white)
                    1: (0, 0, 0),  # Wall (black)
                    2: (0, 255, 0),  # Entrance (green)
                    3: (255, 0, 0)  # Exit (red)
                }.get(cell_type, (128, 128, 128))

                pygame.draw.rect(self.screen, color,
                                 (x * self.cell_size, y * self.cell_size,
                                  self.cell_size, self.cell_size))

        # Draw solution path
        if path:
            for px, py in path:
                pygame.draw.rect(self.screen, (255, 255, 0),  # Yellow
                                 (px * self.cell_size, py * self.cell_size,
                                  self.cell_size, self.cell_size))

        pygame.display.flip()

    def run(self) -> None:
        """Run visualization loop"""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            pygame.time.Clock().tick(60)

        pygame.quit()


def main():
    # Maze parameters
    width, height = 50, 30
    cell_size = 15

    # Generate maze
    generator = MazeGenerator(width, height, cell_size)
    generator.generate_wilson()
    generator.add_entrance_exit()

    # Solve maze
    solver = MazeSolver(generator.maze)
    solution_path = solver.solve_flood_fill()

    # Visualize
    viz = MazeVisualization(generator.maze, cell_size)
    viz.draw(solution_path)
    viz.run()


if __name__ == "__main__":
    main()