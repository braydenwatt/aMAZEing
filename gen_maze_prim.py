import matplotlib.pyplot as plt
import numpy as np
import random

plt.figure(figsize=(10, 10))

def generate_maze(width, height):
    maze = np.ones((2 * height + 1, 2 * width + 1), dtype=int)

    for y in range(height):
        for x in range(width):
            maze[y * 2 + 1, x * 2 + 1] = 0

    return maze

def visualize_maze(maze):
    # Visualization code for the maze (optional, can be customized)
    plt.imshow(maze, cmap="binary")
    plt.title("Prim's Maze Generation")
    plt.axis('off')
    plt.pause(0.001)

def carve_passages_prim(maze, width, height, start_x=0, start_y=0, update_interval=10, visualize=False):
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

    iteration = 0
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

        iteration += 1
        if iteration % update_interval == 0 and visualize:
            visualize_maze(maze)  # Only visualize every `update_interval` iterations

def display_maze(maze):
    color_maze = np.zeros((*maze.shape, 3))
    color_maze[maze == 1] = [0, 0, 0]
    color_maze[maze == 0] = [1, 1, 1]
    #color_maze[1,1] = [0, 1, 0]
    #color_maze[-2, -2] = [1, 0, 0]

    plt.title("Completed Maze")
    plt.gcf().set_facecolor('white')
    plt.imshow(color_maze, interpolation='nearest')
    plt.axis('off')
    plt.draw()
    plt.show()

def save_maze_image(maze, filename='maze_image.png'):
    color_maze = np.zeros((*maze.shape, 3))
    color_maze[maze == 1] = [0, 0, 0]  # Walls as black
    color_maze[maze == 0] = [1, 1, 1]  # Passages as white
    print(maze.shape[1])

    # Display the maze
    plt.imshow(color_maze, interpolation='nearest')
    plt.axis('off')

    # Save the image with no extra padding
    plt.savefig(filename, bbox_inches='tight', pad_inches=0.0)
    plt.close()

width, height = 20, 20
maze = generate_maze(width, height)
carve_passages_prim(maze, width, height)
save_maze_image(maze, 'generated_prim.png')