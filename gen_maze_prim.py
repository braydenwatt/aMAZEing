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

    for y in range(height):
        for x in range(width):
            maze[y * 2 + 1, x * 2 + 1] = 0

    return maze

def visualize_maze(screen, maze):
    screen.fill((0, 0, 0))  # Clear the screen
    color_maze = np.zeros((*maze.shape, 3), dtype=int)

    # Walls as black
    color_maze[maze == 1] = [0, 0, 0]
    # Passages as white
    color_maze[maze == 0] = [255, 255, 255]

    # Draw the maze
    for y in range(maze.shape[0]):
        for x in range(maze.shape[1]):
            pygame.draw.rect(screen, color_maze[y, x], (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    pygame.display.flip()

def carve_passages_prim(maze, width, height, start_x=0, start_y=0, screen=None, visualize=True):
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    walls = []

    # Start with a grid full of walls
    maze[:, :] = 1

    # Pick a starting cell and mark it as part of the maze
    start_cell = (start_y * 2 + 1, start_x * 2 + 1)
    maze[start_cell[0], start_cell[1]] = 0

    # Add the walls of the starting cell to the wall list
    for dx, dy in directions:
        wx, wy = start_cell[0] + dy, start_cell[1] + dx
        if 0 < wx < height * 2 and 0 < wy < width * 2:
            walls.append((wx, wy))

    while walls:
        # Pick a random wall from the list
        random.shuffle(walls)
        wx, wy = walls.pop()

        # Check if it can be a passage
        neighbors = []
        for dx, dy in directions:
            nx, ny = wx + dy, wy + dx
            if 0 <= nx < maze.shape[0] and 0 <= ny < maze.shape[1] and maze[nx, ny] == 0:
                neighbors.append((nx, ny))

        if len(neighbors) == 1:  # Only one visited cell
            # Make the wall a passage
            maze[wx, wy] = 0
            nx, ny = neighbors[0]
            new_cell = (2 * wx - nx, 2 * wy - ny)

            # Mark the unvisited cell as part of the maze
            maze[new_cell[0], new_cell[1]] = 0

            # Add the neighboring walls of the new cell to the wall list
            for dx, dy in directions:
                wx2, wy2 = new_cell[0] + dy, new_cell[1] + dx
                if 0 < wx2 < height * 2 and 0 < wy2 < width * 2 and maze[wx2, wy2] == 1:
                    walls.append((wx2, wy2))

            if visualize:
                # Visualize the current state of the maze
                visualize_maze(screen, maze)

                # Draw a green border around the latest added cell
                current_x, current_y = new_cell
                pygame.draw.rect(screen, (0, 255, 0), (current_y * CELL_SIZE, current_x * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)

                pygame.display.flip()
                pygame.time.delay(10)  # Adjust delay for speed
                pygame.event.pump()  # Handle Pygame events (e.g., quit)

    return maze

def main():
    width, height = 20, 20  # Maze dimensions
    maze = generate_maze(width, height)

    # Set up the display
    screen_size = (maze.shape[1] * CELL_SIZE, maze.shape[0] * CELL_SIZE)
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption("Prim's Maze Generation")

    # Run maze generation
    carve_passages_prim(maze, width, height, 0, 0, screen=screen, visualize=True)

    # Display the final maze
    visualize_maze(screen, maze)

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
