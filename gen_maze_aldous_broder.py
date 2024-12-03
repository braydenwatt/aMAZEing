import matplotlib.pyplot as plt
import numpy as np
import random

def generate_maze(width, height):
    maze = np.ones((2 * height + 1, 2 * width + 1), dtype=int)

    for y in range(height):
        for x in range(width):
            maze[y * 2 + 1, x * 2 + 1] = 0

    return maze

def carve_passages(maze, width, height, update_freq=1, visualize=False):
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    iteration = 0

    visited = set()

    all_cells = [(x * 2 + 1, y * 2 + 1) for y in range(height) for x in range(width)]

    unvisited = set(all_cells)
    current = random.choice(all_cells)
    visited.add(current)
    unvisited.remove(current)

    while unvisited:
        print(unvisited)
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

                iteration += 1
                if iteration % update_freq == 0 and visualize:
                    visualize_maze(maze, visited, next_cell)

                break

    return maze

def visualize_maze(maze, visited, last):
    color_maze = np.zeros((*maze.shape, 3))
    color_maze[maze == 1] = [0, 0, 0]
    color_maze[maze == 0] = [0, 0, 0]

    for x, y in visited:
        color_maze[y, x] = [1, 1, 1]
    last_x, last_y = last

    color_maze[last_y, last_x] = [0, 1, 0]
    plt.title("Aldous Broder Maze Generation")
    plt.gcf().set_facecolor('white')
    plt.imshow(color_maze, interpolation='nearest')
    plt.axis('off')
    plt.pause(0.0001)

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
    color_maze[maze == 1] = [0, 0, 0]
    color_maze[maze == 0] = [1, 1, 1]

    plt.imshow(color_maze, interpolation='nearest')
    plt.axis('off')
    plt.savefig(filename, bbox_inches='tight', pad_inches=0.0)
    plt.close()

width, height = 5, 5
maze = generate_maze(width, height)
plt.figure(figsize=(10, 10))
carve_passages(maze, width, height, 1, True)
plt.show()
print(len(maze))
display_maze(maze)
