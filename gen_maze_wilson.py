import matplotlib.pyplot as plt
import numpy as np
import random


def generate_maze(width, height):
    """Initialize the maze grid with walls everywhere."""
    maze = np.ones((2 * height + 1, 2 * width + 1), dtype=int)

    # Create initial cell grid
    for y in range(height):
        for x in range(width):
            maze[y * 2 + 1, x * 2 + 1] = 0

    return maze


def visualize_maze(maze, current_path=None, unvisited=None, title="Wilson's Maze Generation"):
    """Visualize the maze generation process with improved color scheme."""
    # Create a black background
    color_maze = np.zeros((*maze.shape, 3))

    # Render the maze state
    for y in range(maze.shape[0]):
        for x in range(maze.shape[1]):
            if maze[y, x] == 0:
                color_maze[y, x] = [1, 1, 1]  # White for passages

    # Unvisited cells in dark blue
    if unvisited:
        for cell in unvisited:
            color_maze[cell[1], cell[0]] = [0, 0, 0]  # Dark blue for unvisited cells

    # Current path in bright blue (including walls)
    if current_path:
        for i in range(len(current_path) - 1):
            # Color the cell
            color_maze[current_path[i][1], current_path[i][0]] = [0, 0.7, 1]

            # Color the wall between cells
            wall_x = (current_path[i][0] + current_path[i + 1][0]) // 2
            wall_y = (current_path[i][1] + current_path[i + 1][1]) // 2
            color_maze[wall_y, wall_x] = [0, 0.7, 1]

        # Color the last cell in the path
        color_maze[current_path[-1][1], current_path[-1][0]] = [0, 0.7, 1]

    # Highlight start and end
    color_maze[1, 1] = [0, 1, 0]  # Start (green)
    color_maze[-2, -2] = [1, 0, 0]  # End (red)

    plt.clf()
    plt.imshow(color_maze, interpolation='nearest')
    plt.axis('off')
    plt.title(title)
    plt.draw()
    plt.pause(0.05)  # Reduced pause for faster visualization


def wilsons_algorithm(width, height, visualize=True):
    """Generate a maze using Wilson's algorithm with optional visualization."""
    # Initialize maze
    maze = generate_maze(width, height)

    # Create list of all cells
    all_cells = [(x * 2 + 1, y * 2 + 1)
                 for y in range(height)
                 for x in range(width)]

    # Track visited and unvisited cells
    unvisited = set(all_cells)

    # Choose a random starting cell and mark as visited
    start = random.choice(list(unvisited))
    unvisited.remove(start)

    if visualize:
        plt.figure(figsize=(10, 10))

    # Continue until all cells are visited
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


def main():
    width, height = 10, 10
    random.seed(42)  # For reproducibility
    maze = wilsons_algorithm(width, height)
    print(maze)


if __name__ == "__main__":
    main()