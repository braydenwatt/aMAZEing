import matplotlib.pyplot as plt
import numpy as np
import random

def generate_maze(width, height):
    maze = np.ones((2 * height + 1, 2 * width + 1), dtype=int)

    for y in range(height):
        for x in range(width):
            maze[y * 2 + 1, x * 2 + 1] = 0

    return maze

def visualize_maze(maze, current_path=None, unvisited=None, title="Wilson's Maze Generation"):
    color_maze = np.zeros((*maze.shape, 3))

    for y in range(maze.shape[0]):
        for x in range(maze.shape[1]):
            if maze[y, x] == 0:
                color_maze[y, x] = [1, 1, 1]

    if unvisited:
        for cell in unvisited:
            color_maze[cell[1], cell[0]] = [0, 0, 0]

    if current_path:
        for i in range(len(current_path) - 1):
            # Color the cell
            color_maze[current_path[i][1], current_path[i][0]] = [0.2, 0.2, 1]

            # Color the wall between cells
            wall_x = (current_path[i][0] + current_path[i + 1][0]) // 2
            wall_y = (current_path[i][1] + current_path[i + 1][1]) // 2
            color_maze[wall_y, wall_x] = [0.2, 0.2, 1]

        # Color the last cell in the path
        color_maze[current_path[-1][1], current_path[-1][0]] = [0.2, 0.2, 1]

    plt.clf()
    plt.imshow(color_maze, interpolation='nearest')
    plt.axis('off')
    plt.title(title)
    plt.draw()
    plt.pause(0.05)  # Reduced pause for faster visualization


def wilsons_algorithm(width, height, visualize=True):
    maze = generate_maze(width, height)

    all_cells = [(x * 2 + 1, y * 2 + 1)
                 for y in range(height)
                 for x in range(width)]

    unvisited = set(all_cells)

    start = random.choice(list(unvisited))
    unvisited.remove(start)

    if visualize:
        plt.figure(figsize=(10, 10))

    while unvisited:
        # Choose an unvisited cell to start a random walk
        current = random.choice(list(unvisited))
        path = [current]

        # Random walk until we hit a visited cell
        while current in unvisited:
            # Possible move directions
            directions = [(0, 2), (0, -2), (2, 0), (-2, 0)]

            # Choose a random direction
            dx, dy = random.choice(directions)
            next_cell = (current[0] + dx, current[1] + dy)

            # Check if next cell is valid
            if (0 < next_cell[0] < maze.shape[1] - 1 and
                    0 < next_cell[1] < maze.shape[0] - 1):

                # Check for loops and remove them
                if next_cell in path:
                    # Erase loop
                    loop_index = path.index(next_cell)
                    path = path[:loop_index + 1]

                # Add next cell to path
                path.append(next_cell)
                current = next_cell

                # Visualize occasionally
                if visualize and len(path) % 10 == 0:
                    visualize_maze(maze, current_path=path, unvisited=unvisited)

        # If we've reached a visited cell, carve the path
        if current not in unvisited:
            # Carve the path
            for i in range(len(path) - 1):
                # Calculate wall position
                wall_x = (path[i][0] + path[i + 1][0]) // 2
                wall_y = (path[i][1] + path[i + 1][1]) // 2

                # Remove walls and cells (carve passages)
                maze[wall_y, wall_x] = 0
                maze[path[i][1], path[i][0]] = 0
                maze[path[i + 1][1], path[i + 1][0]] = 0

                # Remove from unvisited
                if path[i] in unvisited:
                    unvisited.remove(path[i])
                if path[i + 1] in unvisited:
                    unvisited.remove(path[i + 1])

            # Visualize final path
            if visualize:
                visualize_maze(maze, current_path=path, unvisited=unvisited)

    # Final visualization to show completed maze
    if visualize:
        visualize_maze(maze, title="Completed Maze")
        plt.show()

    return maze

def save_maze_image(maze, filename='maze_image.png'):
    color_maze = np.zeros((*maze.shape, 3))
    color_maze[maze == 1] = [0, 0, 0]
    color_maze[maze == 0] = [1, 1, 1]

    plt.imshow(color_maze, interpolation='nearest')
    plt.axis('off')
    plt.savefig(filename, bbox_inches='tight', pad_inches=0.0)
    plt.close()

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

def main():
    width, height = 20, 20
    random.seed(42)
    maze = wilsons_algorithm(width, height, False)
    print(len(maze))
    save_maze_image(maze,'generated_wilson.png')

if __name__ == "__main__":
    main()