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


def visualize_maze(screen, maze, current_cell=None):
    screen.fill((0, 0, 0))  # Clear the screen

    # Draw walls (cells with value 1)
    for y in range(maze.shape[0]):
        for x in range(maze.shape[1]):
            if maze[y, x] == 1:
                pygame.draw.rect(screen, (0, 0, 0), (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            if maze[y, x] == 0:
                # Draw empty cell (20x20 pixels)
                color = (255, 255, 255)
                pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, (CELL_SIZE), (CELL_SIZE)))

    # Highlight the current cell with a green border
    if current_cell:
        current_x, current_y = current_cell
        pygame.draw.rect(screen, (0, 255, 0), (current_x * CELL_SIZE, current_y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)

    pygame.display.flip()


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

                visualize_maze(screen, maze, (nx, ny))
                pygame.display.flip()
                pygame.time.delay(10)  # Adjust delay for speed

                break
        else:
            stack.pop()

def main():
    width, height = 20, 20  # Maze dimensions
    maze = generate_maze(width, height)

    # Set up the display
    screen_size = (maze.shape[1] * CELL_SIZE, maze.shape[0] * CELL_SIZE)
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption("Maze Generation")

    # Run maze generation
    carve_passages_prim(maze, width, height, screen=screen, visualize=True)

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
