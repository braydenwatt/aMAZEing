import pygame
import numpy as np
import random
import time

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

def carve_passages(maze, width, height, start_x=0, start_y=0, screen=None):
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

                visualize_maze_pygame(screen, maze)
                pygame.display.flip()
                pygame.time.delay(10)  # Adjust delay for speed

                break
        else:
            stack.pop()

# Visualize the maze using pygame
def visualize_maze_pygame(screen, maze, current_cell):
    screen.fill((0, 0, 0))  # Clear the screen
    for y in range(maze.shape[0]):
        for x in range(maze.shape[1]):
            if maze[y, x] == 0:
                # Draw empty cell (20x20 pixels)
                color = (255, 255, 255)
                pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, (CELL_SIZE), (CELL_SIZE)))

    current_x, current_y = current_cell
    pygame.draw.rect(screen, (0, 255, 0), (current_x * CELL_SIZE, current_y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)

    pygame.display.flip()

# Main function
def main():
    pygame.init()
    width, height = 20, 20
    maze = generate_maze(width, height)
    screen_size = (maze.shape[1] * CELL_SIZE, maze.shape[0] * CELL_SIZE)
    screen = pygame.display.set_mode(screen_size)
    visualize_maze_pygame(screen, maze)
    pygame.display.set_caption("Maze Generation")
    clock = pygame.time.Clock()

    carve_passages(maze, width, height, start_x=0, start_y=0, screen=screen)

    # Display the completed maze until the user quits
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
