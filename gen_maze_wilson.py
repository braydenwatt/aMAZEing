import matplotlib.pyplot as plt
import numpy as np
import random


def generate_maze(width, height):
    maze = np.ones((2 * height + 1, 2 * width + 1), dtype=int)
    for y in range(height):
        for x in range(width):
            maze[y * 2 + 1, x * 2 + 1] = 0
    return maze


def visualize_maze(maze, current_path=None, finalized_cells=None):
    color_maze = np.zeros((*maze.shape, 3))
    color_maze[maze == 1] = [0, 0, 0]  # Walls (black)
    color_maze[maze == 0] = [0, 0, 0]  # Passages (black)

    if current_path:
        for i in range(len(current_path) - 1):
            # Color the walls between current path cells
            wall_x = (current_path[i][0] + current_path[i + 1][0]) // 2
            wall_y = (current_path[i][1] + current_path[i + 1][1]) // 2

            # Blue walls for current path
            color_maze[wall_y, wall_x] = [0, 0, 1]  # Blue for walls in current path

            # Blue for cells in current path
            color_maze[current_path[i][1], current_path[i][0]] = [0, 0, 1]  # Light blue
            color_maze[current_path[i + 1][1], current_path[i + 1][0]] = [0, 0, 1]  # Light blue

    if finalized_cells:
        for i in range(len(finalized_cells) - 1):
            # Color the walls between current path cells
            wall_x = (finalized_cells[i][0] + finalized_cells[i + 1][0]) // 2
            wall_y = (finalized_cells[i][1] + finalized_cells[i + 1][1]) // 2

            color_maze[wall_y, wall_x] = [0.8, 0.8, 0.8]

            color_maze[finalized_cells[i][1], finalized_cells[i][0]] = [0.8, 0.8, 0.8]
            color_maze[finalized_cells[i+1][1], finalized_cells[i+1][0]] = [0.8, 0.8, 0.8]

    color_maze[1, 1] = [0, 1, 0]  # Start (green)
    color_maze[-2, -2] = [1, 0, 0]  # End (red)

    plt.clf()
    plt.imshow(color_maze, interpolation='nearest')
    plt.axis('off')
    plt.title("Wilson's Maze Generation")
    plt.draw()
    plt.pause(0.01)  # Reduced pause time


def make_passages(maze, width, height, update_freq=10000):
    unvisited = set((x * 2 + 1, y * 2 + 1)
                    for y in range(height)
                    for x in range(width))

    start = random.choice(list(unvisited))
    unvisited.remove(start)

    finalized_cells = set([start])
    iteration = 0

    while unvisited:
        current = random.choice(list(unvisited))
        path = [current]

        while current in unvisited:
            directions = [(0, 2), (0, -2), (2, 0), (-2, 0)]
            random.shuffle(directions)

            for dx, dy in directions:
                next_cell = (current[0] + dx, current[1] + dy)

                if (0 < next_cell[0] < maze.shape[1] - 1 and
                        0 < next_cell[1] < maze.shape[0] - 1):

                    if next_cell in path:
                        # Highlight loop erasing
                        idx = path.index(next_cell)
                        path = path[:idx + 1]
                        #visualize_maze(maze, current_path=path, finalized_cells=finalized_cells)

                    path.append(next_cell)
                    current = next_cell
                    break

        # Only update visualization periodically
        #if iteration % update_freq == 0:
            #visualize_maze(maze, current_path=path, finalized_cells=finalized_cells)

        # Carve passages
        for i in range(len(path) - 1):
            wall_x = (path[i][0] + path[i + 1][0]) // 2
            wall_y = (path[i][1] + path[i + 1][1]) // 2

            maze[wall_y, wall_x] = 0
            maze[path[i][1], path[i][0]] = 0
            maze[path[i + 1][1], path[i + 1][0]] = 0

            if path[i] in unvisited:
                unvisited.remove(path[i])
            if path[i + 1] in unvisited:
                unvisited.remove(path[i + 1])

            finalized_cells.update(path[:i + 2])

        iteration += 1

    return maze


def main():
    width, height = 10, 10
    maze = generate_maze(width, height)
    make_passages(maze, width, height)
    plt.show()


if __name__ == "__main__":
    main()