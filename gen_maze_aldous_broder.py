import pygame
import numpy as np
import random

# Constants for visualization
CELL_SIZE = 20
FPS = 60

# Generate the maze grid
def generate_maze(width, height):
    maze = np.ones((2 * height + 1, 2 * width + 1), dtype=int)
    for y in range(height):
        for x in range(width):
            maze[y * 2 + 1, x * 2 + 1] = 0
    return maze

def carve_passages(maze, width, height, visualize=False, screen=None):
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
                    visualize_maze_pygame(screen, maze, list(visited), current)
                    pygame.display.flip()
                    pygame.time.delay(10)  # Adjust delay for speed
                    pygame.event.pump()  # Handle Pygame events (e.g., quit)

                break

    return maze

# Visualize the maze using Pygame
def visualize_maze_pygame(screen, maze, visited, current_cell):
    screen.fill((0, 0, 0))  # Clear the screen

    # Draw walls (cells with value 1)
    for y in range(maze.shape[0]):
        for x in range(maze.shape[1]):
            if maze[y, x] == 1:
                pygame.draw.rect(screen, (0, 0, 0), (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # Draw visited cells (cells with value 0)
    for x, y in visited:
        pygame.draw.rect(screen, (255, 255, 255), (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # Highlight the current cell with a green border
    current_x, current_y = current_cell
    pygame.draw.rect(screen, (0, 255, 0), (current_x * CELL_SIZE, current_y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)

    pygame.display.flip()

# Display the completed maze
def display_maze(screen, maze):
    for y in range(maze.shape[0]):
        for x in range(maze.shape[1]):
            if maze[y, x] == 1:
                pygame.draw.rect(screen, (0, 0, 0), (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            else:
                pygame.draw.rect(screen, (255, 255, 255), (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    pygame.display.flip()

# Initialize Pygame
def main():
    pygame.init()

    width, height = 20, 20  # Maze dimensions
    maze = generate_maze(width, height)

    # Set up the display
    screen_size = (maze.shape[1] * CELL_SIZE, maze.shape[0] * CELL_SIZE)
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption("Aldous-Broder Maze Generation")

    # Run maze generation
    carve_passages(maze, width, height, visualize=True, screen=screen)

    # Show the final maze after completion
    display_maze(screen, maze)

    # Wait until the user closes the window
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        pygame.time.Clock().tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
