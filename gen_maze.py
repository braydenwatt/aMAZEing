import matplotlib.pyplot as plt
import numpy as np
import random

def generate_maze(width, height):
    maze = np.ones((2 * height + 1, 2 * width + 1), dtype=int)

    for y in range(height):
        for x in range(width):
            maze[y * 2 + 1, x * 2 + 1] = 0

    return maze

def carve_passages(maze, width, height, start_x=0, start_y=0, update_freq=1, visualize=False):
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    stack = [(start_x * 2 + 1, start_y * 2 + 1)]
    visited = set(stack)
    backtracked_cells = set()
    iteration = 0

    while stack:
        x, y = stack[-1]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = x + 2 * dx, y + 2 * dy
            if 0 < nx < maze.shape[1] - 1 and 0 < ny < maze.shape[0] - 1 and (nx, ny) not in visited:
                # Remove the wall
                wall_x, wall_y = x + dx, y + dy
                maze[wall_y, wall_x] = 0  # Remove the wall
                maze[ny, nx] = 0          # Create the passage
                stack.append((nx, ny))
                visited.add((nx, ny))
                visited.add((wall_x, wall_y))  # Add the removed wall to visited/removed set

                # Visualize the maze generation
                iteration += 1
                if iteration % update_freq == 0 and visualize:
                    visualize_maze(maze, visited, backtracked_cells, (start_x * 2 + 1, start_y * 2 + 1), (nx, ny))
                break
        else:
            # Backtrack
            backtracked_cells.add(stack.pop())
            if stack:
                bx, by = stack[-1]
                backtracked_cells.add(((x + bx) // 2, (y + by) // 2))

                iteration += 1
                if iteration % update_freq == 0 and visualize:
                    visualize_maze(maze, visited, backtracked_cells, (start_x * 2 + 1, start_y * 2 + 1), ((x+bx)//2, (y+by)//2))

def visualize_maze(maze, visited, backtracked_cells, start, end):
    color_maze = np.zeros((*maze.shape, 3))
    color_maze[maze == 1] = [0, 0, 0]
    color_maze[maze == 0] = [0, 0, 0]

    for x, y in visited:
        color_maze[y, x] = [1, 1, 1]
    for x, y in backtracked_cells:
        color_maze[y, x] = [0.2, 0.2, 1]

    color_maze[start[1], start[0]] = [0, 1, 0]
    color_maze[end[1], end[0]] = [1, 0, 0]
    plt.title("DFS Maze Generation")
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

width, height = 20, 20
maze = generate_maze(width, height)
plt.figure(figsize=(10, 10))
carve_passages(maze, width, height)
plt.show()
print(len(maze))
display_maze(maze)
save_maze_image(maze, 'generated_maze.png')
