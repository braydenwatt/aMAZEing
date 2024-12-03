import matplotlib.pyplot as plt
import numpy as np

def display_maze(maze):
    color_maze = np.zeros((*maze.shape, 3))
    color_maze[maze == 1] = [0, 0, 0]
    color_maze[maze == 0] = [1, 1, 1]

    plt.title("Completed Maze")
    plt.gcf().set_facecolor('white')
    plt.imshow(color_maze, interpolation='nearest')
    plt.axis('off')
    plt.draw()
    plt.show()
