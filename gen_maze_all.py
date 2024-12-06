import pygame
import numpy as np
import random

# Constants
CELL_SIZE = 20
FPS = 60

# Initialize Pygame
pygame.init()

def generate_maze(width, height):
    maze = np.ones((2 * height + 1, 2 * width + 1), dtype=int)

    # Carve out passageways
    for y in range(height):
        for x in range(width):
            maze[2 * y + 1, 2 * x + 1] = 0  # Make every odd cell a passage

    return maze


def visualize_maze(screen, maze, current_cell=None, backtracked=None, finalized=None):
    screen.fill((0, 0, 0))  # Black background

    overlap = 0

    for y in range(maze.shape[0]):
        for x in range(maze.shape[1]):
            if maze[y, x] == 0:  # White cell
                pygame.draw.rect(screen, (255, 255, 255),
                                 (x * (CELL_SIZE - overlap), y * (CELL_SIZE - overlap),
                                  CELL_SIZE, CELL_SIZE))
            elif maze[y, x] == 2:  # Entrance
                pygame.draw.rect(screen, (0, 255, 0),  # Green
                                 (x * (CELL_SIZE - overlap), y * (CELL_SIZE - overlap),
                                  CELL_SIZE, CELL_SIZE))
            elif maze[y, x] == 3:  # Exit
                pygame.draw.rect(screen, (255, 0, 0),  # Red
                                 (x * (CELL_SIZE - overlap), y * (CELL_SIZE - overlap),
                                  CELL_SIZE, CELL_SIZE))
            elif maze[y, x] == 4:  # Solver in progress
                pygame.draw.rect(screen, (0, 0, 255),  # Blue
                             (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            elif maze[y, x] == 5:  # Solution path
                pygame.draw.rect(screen, (255, 255, 0),  # Yellow
                                 (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

            if backtracked:
                if (x,y) in backtracked:
                    pygame.draw.rect(screen, (0, 0, 255),  # Red
                                     (x * (CELL_SIZE - overlap), y * (CELL_SIZE - overlap),
                                      CELL_SIZE, CELL_SIZE))

    # Highlight current cell
    if current_cell:
        current_x, current_y = current_cell
        pygame.draw.rect(screen, (0, 255, 0),
                         (current_x * (CELL_SIZE - overlap), current_y * (CELL_SIZE - overlap),
                          CELL_SIZE, CELL_SIZE), 3)

def carve_passages_prim(maze, width, height, screen=None, visualize=True):
    start_x, start_y = 0, 0
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    walls = []
    visited = set()

    # Pick a starting cell and mark it as visited
    start_cell = (start_y * 2 + 1, start_x * 2 + 1)
    visited.add(start_cell)

    # Add the walls of the starting cell to the wall list
    for dx, dy in directions:
        wx, wy = start_cell[0] + dy, start_cell[1] + dx
        if 0 < wx < height * 2 and 0 < wy < width * 2:
            walls.append((wx, wy))

    while walls:
        # Pick a random wall from the list
        wx, wy = random.choice(walls)
        walls.remove((wx, wy))

        # Check if it can be a passage
        neighbors = []
        for dx, dy in directions:
            nx, ny = wx + dx, wy + dy
            if 0 <= nx < maze.shape[0] and 0 <= ny < maze.shape[1]:
                if maze[nx, ny] == 0 and (nx, ny) in visited:
                    neighbors.append((nx, ny))

        if len(neighbors) == 1:
            # Make the wall a passage
            maze[wx, wy] = 0
            nx, ny = neighbors[0]
            new_cell = (2 * wx - nx, 2 * wy - ny)

            # Mark the unvisited cell as part of the maze and visited
            maze[new_cell[0], new_cell[1]] = 0
            visited.add(new_cell)

            # Add the neighboring walls of the new cell to the wall list
            for dx, dy in directions:
                wx2, wy2 = new_cell[0] + dy, new_cell[1] + dx
                if 0 < wx2 < height * 2 and 0 < wy2 < width * 2 and maze[wx2, wy2] == 1:
                    walls.append((wx2, wy2))

            if visualize:
                # Visualize the current state of the maze
                visualize_maze(screen, maze, (new_cell[1], new_cell[0]))

                pygame.display.flip()
                pygame.time.delay(10)  # Adjust delay for speed
                pygame.event.pump()  # Handle Pygame events (e.g., quit)
    return maze

def carve_passages_aldous(maze, width, height, screen=None, visualize=True):
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    visited = set()

    all_cells = [(x * 2 + 1, y * 2 + 1) for y in range(height) for x in range(width)]

    unvisited = set(all_cells)
    current = random.choice(all_cells)
    visited.add(current)
    unvisited.remove(current)

    while unvisited:
        random.shuffle(directions)
        x, y = current
        for dx, dy in directions:
            nx, ny = x + 2 * dx, y + 2 * dy

            if 0 < nx < maze.shape[1] - 1 and 0 < ny < maze.shape[0] - 1:
                next_cell = (nx, ny)

                if next_cell not in visited:
                    wall_x, wall_y = x + dx, y + dy
                    maze[wall_y, wall_x] = 0
                    maze[ny, nx] = 0
                    visited.add(next_cell)
                    visited.add((wall_x, wall_y))
                    unvisited.remove(next_cell)

                current = next_cell

                if visualize:
                    visualize_maze(screen, maze, current)
                    pygame.display.flip()
                    pygame.time.delay(10)  # Adjust delay for speed
                    pygame.event.pump()  # Handle Pygame events (e.g., quit)

                break

    return maze

def carve_passages(maze, width, height, screen=None, visualize=True):
    start_x, start_y = 0, 0
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    stack = [(start_x * 2 + 1, start_y * 2 + 1)]
    visited = set(stack)
    backtracked_cells = set()
    finalized_cells = set()

    while stack and screen:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        x, y = stack[-1]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = x + 2 * dx, y + 2 * dy
            if 0 < nx < maze.shape[1] - 1 and 0 < ny < maze.shape[0] - 1 and (nx, ny) not in visited:
                wall_x, wall_y = x + dx, y + dy
                maze[wall_y, wall_x] = 0  # Remove the wall
                maze[ny, nx] = 0          # Create the passage
                stack.append((nx, ny))
                visited.add((nx, ny))
                finalized_cells.add((nx, ny))
                finalized_cells.add((wall_x, wall_y))

                if visualize:
                    visualize_maze(screen, maze, (nx, ny), backtracked_cells, finalized_cells)
                    pygame.display.flip()
                    pygame.time.delay(10)  # Adjust delay for speed

                break
        else:
            # Handle backtracking
            backtracked_cell = stack.pop()
            backtracked_cells.add(backtracked_cell)

            # Add the wall associated with the backtracked cell
            if stack:
                prev_x, prev_y = stack[-1]
                wall_x, wall_y = (backtracked_cell[0] + prev_x) // 2, (backtracked_cell[1] + prev_y) // 2
                backtracked_cells.add((wall_x, wall_y))

            if visualize:
                visualize_maze(screen, maze, None, backtracked_cells, finalized_cells)
                pygame.display.flip()
                pygame.time.delay(10)


def add_maze_entrance_and_exit(maze):
    """
    Add an entrance (2) and exit (3) to the maze's left or right border walls.

    Args:
        maze (numpy.ndarray): The maze grid where 0 represents paths and 1 represents walls.

    Returns:
        numpy.ndarray: The maze grid with entrance (2) and exit (3) added to left or right walls.
    """
    # Candidate positions for entrance and exit
    left_wall_candidates = [
        (y, 0) for y in range(1, maze.shape[0] - 1) if maze[y, 1] == 0 and maze[y, 0] == 1
    ]
    right_wall_candidates = [
        (y, maze.shape[1] - 1) for y in range(1, maze.shape[0] - 1) if maze[y, -2] == 0 and maze[y, -1] == 1
    ]

    # If there are no valid candidates on one side, fallback to the other side
    if not left_wall_candidates and not right_wall_candidates:
        raise ValueError("No valid positions found for entrance and exit.")

    # Randomly choose walls for entrance and exit
    if random.choice([True, False]) and left_wall_candidates and right_wall_candidates:
        entrance = random.choice(left_wall_candidates)
        exit = random.choice(right_wall_candidates)
    elif left_wall_candidates:
        entrance = random.choice(left_wall_candidates)
        exit = random.choice(left_wall_candidates)  # Place both on the left if no right candidates
    else:
        entrance = random.choice(right_wall_candidates)
        exit = random.choice(right_wall_candidates)  # Place both on the right if no left candidates

    # Mark entrance and exit
    maze[entrance[0], entrance[1]] = 2  # Entrance
    maze[exit[0], exit[1]] = 3  # Exit

    return maze

def solve_maze_dfs(maze, screen, visualize=True):
    """
    Solve the maze using Depth-First Search (DFS) and visualize the process.

    Args:
        maze (numpy.ndarray): The maze grid where 0 = path, 1 = wall, 2 = entrance, 3 = exit.
        screen (pygame.Surface): Pygame screen for visualization.
        visualize (bool): Whether to visualize the process.
    """
    # Find entrance and exit
    entrance = None
    exit = None
    for y in range(maze.shape[0]):
        for x in range(maze.shape[1]):
            if maze[y, x] == 2:
                entrance = (x, y)
            elif maze[y, x] == 3:
                exit = (x, y)

    if not entrance or not exit:
        print("Maze must have an entrance (2) and exit (3).")
        return

    # Directions for movement: Right, Left, Down, Up
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    visited = set()
    path = []

    def dfs(current):
        x, y = current

        # Base case: If we reached the exit, stop
        if current == exit:
            return True

        # Mark the current cell as visited
        visited.add(current)
        path.append(current)

        # Mark as part of the exploration path
        if current != entrance and current != exit:
            maze[y, x] = 4  # Mark as visited

        # Visualization
        if visualize:
            visualize_maze(screen, maze)
            pygame.display.flip()
            pygame.time.delay(20)
            pygame.event.pump()

        # Explore neighbors
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            neighbor = (nx, ny)

            if (0 <= nx < maze.shape[1] and 0 <= ny < maze.shape[0] and
                    neighbor not in visited and maze[ny, nx] in [0, 3]):
                if neighbor == exit:
                    return True
                if dfs(neighbor):
                    return True

        # Backtrack
        if current != entrance and current != exit:
            maze[y, x] = 0  # Mark as backtracked

        # Visualization for backtracking
        if visualize:
            visualize_maze(screen, maze)
            pygame.display.flip()
            pygame.time.delay(20)

        path.pop()  # Remove current from path if no valid neighbors
        return False

    # Start DFS from the entrance
    dfs(entrance)

    # Mark the solution path
    for px, py in path:
        if maze[py, px] not in [2, 3]:  # Skip entrance and exit
            maze[py, px] = 5  # Mark as part of the solution path

        # Final visualization
        if visualize:
            visualize_maze(screen, maze)
            pygame.display.flip()
            pygame.time.delay(50)

def solve_maze_flood_fill(maze, screen, visualize=True):
    """
    Solve the maze using flood-fill algorithm and visualize the process.

    Args:
        maze (numpy.ndarray): The maze grid where 0 = path, 1 = wall, 2 = entrance, 3 = exit.
        screen (pygame.Surface): Pygame screen for visualization.
        visualize (bool): Whether to visualize the process.
    """
    # Find entrance and exit
    entrance = None
    exit = None
    for y in range(maze.shape[0]):
        for x in range(maze.shape[1]):
            if maze[y, x] == 2:
                entrance = (x, y)
            elif maze[y, x] == 3:
                exit = (x, y)

    if not entrance or not exit:
        print("Maze must have an entrance (2) and exit (3).")
        return

    # Flood-fill algorithm
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # Right, Left, Down, Up
    queue = [entrance]
    visited = set()
    parents = {}  # To reconstruct the path

    while queue:
        current = queue.pop(0)
        x, y = current

        # Mark as visited
        if current != entrance:
            maze[y, x] = 4  # Mark as part of the flood-fill path

        visited.add(current)

        # Check if we've reached the exit
        if current == exit:
            break

        # Explore neighbors
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            neighbor = (nx, ny)

            if (0 <= nx < maze.shape[1] and 0 <= ny < maze.shape[0] and
                    neighbor not in visited and maze[ny, nx] in [0, 3]):
                queue.append(neighbor)
                parents[neighbor] = current
                visited.add(neighbor)

        # Visualization
        if visualize:
            visualize_maze(screen, maze)
            pygame.display.flip()
            pygame.time.delay(20)  # Adjust delay for speed
            pygame.event.pump()  # Handle Pygame events (e.g., quit)

    # Reconstruct the path
    if exit in parents:
        path = []
        current = exit
        while current != entrance:
            path.append(current)
            current = parents[current]
        path.append(entrance)
        path.reverse()

        # Mark the solution path
        for px, py in path:
            if maze[py, px] not in [2, 3]:  # Skip entrance and exit
                maze[py, px] = 5  # Mark as part of the solution path

            # Visualization
            if visualize:
                visualize_maze(screen, maze)
                pygame.display.flip()
                pygame.time.delay(50)

    # Final visualization
    visualize_maze(screen, maze)
    pygame.display.flip()

def main():
    width, height = 20, 20  # Maze dimensions
    maze = generate_maze(width, height)

    screen_size = (
        maze.shape[1] * CELL_SIZE,
        maze.shape[0] * CELL_SIZE
    )
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption("Maze Generation")

    # Run maze generation
    carve_passages_prim(maze, width, height, screen=screen, visualize=False)
    add_maze_entrance_and_exit(maze)

    visualize_maze(screen, maze)
    solve_maze_dfs(maze, screen=screen, visualize=True)

    # Wait until the user closes the window
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pygame.display.update()  # Update the display
        pygame.time.Clock().tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
