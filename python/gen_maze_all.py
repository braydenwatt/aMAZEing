import time

import pygame
import numpy as np
import random
import os
from datetime import datetime

# Constants
CELL_SIZE = 20
FPS = 60

# Initialize Pygame
pygame.init()
pygame.mixer.init()

def save_maze_to_png(screen):
    """
    Save the current maze screen as a PNG file.

    Args:
        screen (pygame.Surface): The Pygame screen surface to save
    """
    try:
        # Create a 'maze_screenshots' directory if it doesn't exist
        os.makedirs('maze_screenshots', exist_ok=True)

        # Generate a filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join('maze_screenshots', f'maze_{timestamp}.png')

        # Save the screen to PNG
        pygame.image.save(screen, filename)

        # Optional: print confirmation (you could replace this with on-screen text)
        print(f"Maze screenshot saved: {filename}")

    except Exception as e:
        print(f"Error saving screenshot: {e}")

def generate_sound(frequency=440, duration=0.1, volume=0.5, waveform='sine', attack=0.02, decay=0.02):
    """Generate a sound wave with basic waveforms and volume envelope."""
    sample_rate = 44100  # Standard sample rate
    samples = np.arange(int(sample_rate * duration)) / sample_rate

    if waveform == 'sine':
        wave = np.sin(2 * np.pi * frequency * samples)
    elif waveform == 'square':
        wave = np.sign(np.sin(2 * np.pi * frequency * samples))
    elif waveform == 'triangle':
        wave = 2 * np.abs(2 * (samples * frequency - np.floor(samples * frequency + 0.5))) - 1
    else:
        raise ValueError("Unsupported waveform type")

    # Apply an envelope (fade in, fade out)
    envelope = np.ones_like(wave)
    attack_samples = int(sample_rate * attack)
    decay_samples = int(sample_rate * decay)
    envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
    envelope[-decay_samples:] = np.linspace(1, 0, decay_samples)

    # Apply the envelope to the wave
    wave = wave * envelope

    # Normalize and scale to int16
    wave = (wave * 32767 / np.max(np.abs(wave))).astype(np.int16)

    # Create stereo sound array
    stereo_wave = np.column_stack((wave, wave))

    # Convert to a pygame sound object
    return pygame.sndarray.make_sound(stereo_wave)


# Generate placeholder sounds with improved qualities
wall_carve_sound = generate_sound(frequency=440, duration=0.15, volume=0.3, waveform='sine', attack=0.05, decay=0.05)
path_create_sound = generate_sound(frequency=520, duration=0.15, volume=0.3, waveform='triangle', attack=0.05,
                                   decay=0.05)
explore_sound = generate_sound(frequency=600, duration=0.1, volume=0.2, waveform='sine', attack=0.03, decay=0.03)
backtrack_sound = generate_sound(frequency=380, duration=0.1, volume=0.2, waveform='sine', attack=0.03, decay=0.03)
path_complete_sound = generate_sound(frequency=800, duration=0.3, volume=0.5, waveform='triangle', attack=0.1,
                                     decay=0.1)

# Adjust the volume of each sound
wall_carve_sound.set_volume(0.3)
path_create_sound.set_volume(0.3)
explore_sound.set_volume(0.2)
backtrack_sound.set_volume(0.2)
path_complete_sound.set_volume(0.5)

def generate_maze(width, height):
    maze = np.ones((2 * height + 1, 2 * width + 1), dtype=int)

    # Carve out passageways
    for y in range(height):
        for x in range(width):
            maze[2 * y + 1, 2 * x + 1] = 0  # Make every odd cell a passage

    return maze


def visualize_maze(screen, maze, current_cell=None, backtracked=None, finalized=None):
    screen.fill((0, 0, 0))  # Black background

    overlap = 0

    for y in range(maze.shape[0]):
        for x in range(maze.shape[1]):
            if maze[y, x] == 0:  # White cell
                pygame.draw.rect(screen, (255, 255, 255),
                                 (x * (CELL_SIZE - overlap), y * (CELL_SIZE - overlap),
                                  CELL_SIZE, CELL_SIZE))
            elif maze[y, x] == 2:  # Entrance
                pygame.draw.rect(screen, (255, 255, 255),  # Green
                                 (x * (CELL_SIZE - overlap), y * (CELL_SIZE - overlap),
                                  CELL_SIZE, CELL_SIZE))
            elif maze[y, x] == 3:  # Exit
                pygame.draw.rect(screen, (255, 255, 255),  # Red
                                 (x * (CELL_SIZE - overlap), y * (CELL_SIZE - overlap),
                                  CELL_SIZE, CELL_SIZE))
            elif maze[y, x] == 4:  # Solver in progress
                pygame.draw.rect(screen, (0, 0, 255),  # Blue
                             (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            elif maze[y, x] == 5:  # Solution path
                pygame.draw.rect(screen, (255, 255, 0),  # Yellow
                                 (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

            if backtracked:
                if (x,y) in backtracked:
                    pygame.draw.rect(screen, (0, 0, 255),  # Red
                                     (x * (CELL_SIZE - overlap), y * (CELL_SIZE - overlap),
                                      CELL_SIZE, CELL_SIZE))

    # Highlight current cell
    if current_cell:
        current_x, current_y = current_cell
        pygame.draw.rect(screen, (0, 255, 0),
                         (current_x * (CELL_SIZE - overlap), current_y * (CELL_SIZE - overlap),
                          CELL_SIZE, CELL_SIZE), 3)


def carve_passages_wilson(maze, width, height, screen=None, visualize=True):
    """
    Generate a maze using Wilson's algorithm (Loop-Erased Random Walk).

    Args:
        maze (numpy.ndarray): The initial maze grid
        width (int): Width of the maze in cells
        height (int): Height of the maze in cells
        screen (pygame.Surface): Pygame screen for visualization
        visualize (bool): Whether to visualize the generation process

    Returns:
        numpy.ndarray: The generated maze
    """
    # Directions for movement: Right, Down, Left, Up
    directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]

    # All possible cells in the maze
    all_cells = [(x * 2 + 1, y * 2 + 1) for y in range(height) for x in range(width)]

    # Initialize unvisited cells (all cells start as unvisited)
    unvisited = set(all_cells)

    # Keep track of finalized paths
    finalized_paths = set()
    finalized_walls = set()

    # Choose a random starting cell and mark it as visited
    start_cell = random.choice(all_cells)
    unvisited.remove(start_cell)
    finalized_paths.add(start_cell)

    # Auxiliary function to check if a cell is within maze bounds
    def is_valid_cell(x, y):
        return 0 < x < maze.shape[1] - 1 and 0 < y < maze.shape[0] - 1

    while unvisited:
        # Choose an unvisited cell as the random walk start
        current_cell = random.choice(list(unvisited))
        path = [current_cell]
        path_set = set(path)
        path_walls = []  # Track walls between cells in the current path

        # Perform random walk until we hit a visited cell
        while current_cell in unvisited:
            # Choose a random direction
            random.shuffle(directions)
            for dx, dy in directions:
                next_x, next_y = current_cell[0] + 2 * dx, current_cell[1] + 2 * dy

                if is_valid_cell(next_x, next_y):
                    next_cell = (next_x, next_y)

                    # Calculate wall coordinates
                    wall_x = (current_cell[0] + next_cell[0]) // 2
                    wall_y = (current_cell[1] + next_cell[1]) // 2
                    wall = (wall_x, wall_y)

                    # If next cell is already in the path, erase the loop
                    if next_cell in path_set:
                        loop_index = path.index(next_cell)

                        # Remove walls and path segments after the loop point
                        path = path[:loop_index + 1]
                        path_walls = path_walls[:loop_index]

                        path_set = set(path)
                    else:
                        path.append(next_cell)
                        path_set.add(next_cell)
                        path_walls.append(wall)

                    current_cell = next_cell
                    break

            # Visualization of the random walk
            if visualize and screen:
                # Reset screen to black
                screen.fill((0, 0, 0))

                # Draw finalized paths in white
                for px, py in finalized_paths:
                    pygame.draw.rect(screen, (255, 255, 255),
                                     (px * CELL_SIZE, py * CELL_SIZE,
                                      CELL_SIZE, CELL_SIZE))

                # Draw finalized walls in white
                for wx, wy in finalized_walls:
                    pygame.draw.rect(screen, (255, 255, 255),
                                     (wx * CELL_SIZE, wy * CELL_SIZE,
                                      CELL_SIZE, CELL_SIZE))

                # Draw current path in blue
                for px, py in path:
                    pygame.draw.rect(screen, (0, 0, 255),
                                     (px * CELL_SIZE, py * CELL_SIZE,
                                      CELL_SIZE, CELL_SIZE))

                # Draw current path walls in blue
                for wx, wy in path_walls:
                    pygame.draw.rect(screen, (0, 0, 255),
                                     (wx * CELL_SIZE, wy * CELL_SIZE,
                                      CELL_SIZE, CELL_SIZE))

                pygame.display.flip()
                pygame.time.delay(20)
                pygame.event.pump()

        # Connect the path to the maze
        if len(path) > 1:
            for i in range(len(path) - 1):
                current = path[i]
                next_cell = path[i + 1]

                # Calculate wall coordinates
                wall_x = (current[0] + next_cell[0]) // 2
                wall_y = (current[1] + next_cell[1]) // 2

                # Carve passage
                maze[current[1], current[0]] = 0
                maze[next_cell[1], next_cell[0]] = 0
                maze[wall_y, wall_x] = 0

                # Add to finalized sets
                finalized_paths.add(current)
                finalized_paths.add(next_cell)
                finalized_walls.add((wall_x, wall_y))

                # Remove from unvisited set
                if current in unvisited:
                    unvisited.remove(current)
                if next_cell in unvisited:
                    unvisited.remove(next_cell)

        # Visualization of the maze progress
        if visualize and screen:
            # Reset screen to black
            screen.fill((0, 0, 0))

            # Draw finalized paths in white
            for px, py in finalized_paths:
                pygame.draw.rect(screen, (255, 255, 255),
                                 (px * CELL_SIZE, py * CELL_SIZE,
                                  CELL_SIZE, CELL_SIZE))

            # Draw finalized walls in white
            for wx, wy in finalized_walls:
                pygame.draw.rect(screen, (255, 255, 255),
                                 (wx * CELL_SIZE, wy * CELL_SIZE,
                                  CELL_SIZE, CELL_SIZE))

            pygame.display.flip()
            pygame.time.delay(50)
            pygame.event.pump()

    return maze

def carve_passages_prim(maze, width, height, screen=None, visualize=True):
    start_x, start_y = 0, 0
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    walls = []
    visited = set()

    # Pick a starting cell and mark it as visited
    start_cell = (start_y * 2 + 1, start_x * 2 + 1)
    visited.add(start_cell)

    # Add the walls of the starting cell to the wall list
    for dx, dy in directions:
        wx, wy = start_cell[0] + dy, start_cell[1] + dx
        if 0 < wx < height * 2 and 0 < wy < width * 2:
            walls.append((wx, wy))

    while walls:
        # Pick a random wall from the list
        wx, wy = random.choice(walls)
        walls.remove((wx, wy))

        # Check if it can be a passage
        neighbors = []
        for dx, dy in directions:
            nx, ny = wx + dx, wy + dy
            if 0 <= nx < maze.shape[0] and 0 <= ny < maze.shape[1]:
                if maze[nx, ny] == 0 and (nx, ny) in visited:
                    neighbors.append((nx, ny))

        if len(neighbors) == 1:
            # Make the wall a passage
            maze[wx, wy] = 0
            nx, ny = neighbors[0]
            new_cell = (2 * wx - nx, 2 * wy - ny)

            # Mark the unvisited cell as part of the maze and visited
            maze[new_cell[0], new_cell[1]] = 0
            visited.add(new_cell)

            # Add the neighboring walls of the new cell to the wall list
            for dx, dy in directions:
                wx2, wy2 = new_cell[0] + dy, new_cell[1] + dx
                if 0 < wx2 < height * 2 and 0 < wy2 < width * 2 and maze[wx2, wy2] == 1:
                    walls.append((wx2, wy2))

            if visualize:
                # Visualize the current state of the maze
                visualize_maze(screen, maze, (new_cell[1], new_cell[0]))

                pygame.display.flip()
                pygame.time.delay(50)  # Adjust delay for speed
                pygame.event.pump()  # Handle Pygame events (e.g., quit)
    return maze

def carve_passages_aldous(maze, width, height, screen=None, visualize=True):
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
                    visualize_maze(screen, maze, current)
                    pygame.display.flip()
                    pygame.time.delay(10)  # Adjust delay for speed
                    pygame.event.pump()  # Handle Pygame events (e.g., quit)

                break

    return maze

def carve_passages_dfs(maze, width, height, screen=None, visualize=True):
    start_x, start_y = 0, 0
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    stack = [(start_x * 2 + 1, start_y * 2 + 1)]
    visited = set(stack)
    backtracked_cells = set()
    finalized_cells = set()

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
                finalized_cells.add((nx, ny))
                finalized_cells.add((wall_x, wall_y))

                if visualize:
                    visualize_maze(screen, maze, (nx, ny), backtracked_cells, finalized_cells)
                    pygame.display.flip()
                    pygame.time.delay(200)  # Adjust delay for speed

                break
        else:
            # Handle backtracking
            backtracked_cell = stack.pop()
            backtracked_cells.add(backtracked_cell)


            # Add the wall associated with the backtracked cell
            if stack:
                prev_x, prev_y = stack[-1]
                wall_x, wall_y = (backtracked_cell[0] + prev_x) // 2, (backtracked_cell[1] + prev_y) // 2
                backtracked_cells.add((wall_x, wall_y))

            if visualize:
                visualize_maze(screen, maze, (wall_x,wall_y), backtracked_cells, finalized_cells)
                pygame.display.flip()
                pygame.time.delay(200)


def add_maze_entrance_and_exit(maze):
    """
    Add an entrance (2) and exit (3) to the maze's left or right border walls.

    Args:
        maze (numpy.ndarray): The maze grid where 0 represents paths and 1 represents walls.

    Returns:
        numpy.ndarray: The maze grid with entrance (2) and exit (3) added to left or right walls.
    """
    # Candidate positions for entrance and exit
    left_wall_candidates = [
        (y, 0) for y in range(1, maze.shape[0] - 1) if maze[y, 1] == 0 and maze[y, 0] == 1
    ]
    right_wall_candidates = [
        (y, maze.shape[1] - 1) for y in range(1, maze.shape[0] - 1) if maze[y, -2] == 0 and maze[y, -1] == 1
    ]

    # If there are no valid candidates on one side, fallback to the other side
    if not left_wall_candidates and not right_wall_candidates:
        raise ValueError("No valid positions found for entrance and exit.")

    # Randomly choose walls for entrance and exit
    if random.choice([True, False]) and left_wall_candidates and right_wall_candidates:
        entrance = random.choice(left_wall_candidates)
        exit = random.choice(right_wall_candidates)
    elif left_wall_candidates:
        entrance = random.choice(left_wall_candidates)
        exit = random.choice(left_wall_candidates)  # Place both on the left if no right candidates
    else:
        entrance = random.choice(right_wall_candidates)
        exit = random.choice(right_wall_candidates)  # Place both on the right if no left candidates

    # Mark entrance and exit

    # This is all fake code lol

    maze[0,1] = 2
    maze[-1,-2] = 3

    return maze

def solve_maze_dfs(maze, screen, visualize=True):
    """
    Solve the maze using Depth-First Search (DFS) and visualize the process.

    Args:
        maze (numpy.ndarray): The maze grid where 0 = path, 1 = wall, 2 = entrance, 3 = exit.
        screen (pygame.Surface): Pygame screen for visualization.
        visualize (bool): Whether to visualize the process.
    """
    # Find entrance and exit
    entrance = None
    exit = None
    for y in range(maze.shape[0]):
        for x in range(maze.shape[1]):
            if maze[y, x] == 2:
                entrance = (x, y)
            elif maze[y, x] == 3:
                exit = (x, y)

    if not entrance or not exit:
        print("Maze must have an entrance (2) and exit (3).")
        return

    # Directions for movement: Right, Left, Down, Up
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    visited = set()
    path = []

    maze[entrance[1], entrance[0]] = 4

    def dfs(current):
        x, y = current

        # Mark the current cell as visited
        visited.add(current)
        path.append(current)

        # Mark as part of the exploration path
        maze[y, x] = 4  # Mark as visited

        explore_sound.play()

        # Visualization
        if visualize:
            visualize_maze(screen, maze)
            pygame.display.flip()
            pygame.time.delay(20)
            pygame.event.pump()

        # Explore neighbors
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            neighbor = (nx, ny)

            if (0 <= nx < maze.shape[1] and 0 <= ny < maze.shape[0] and
                    neighbor not in visited and maze[ny, nx] in [0, 3]):
                if neighbor == exit:
                    path.append(neighbor)  # Include the exit in the path
                    return True
                if dfs(neighbor):
                    return True

        # Backtrack
        if current not in [entrance, exit]:
            maze[y, x] = 0  # Mark as backtracked
            backtrack_sound.play()

        # Visualization for backtracking
        if visualize:
            visualize_maze(screen, maze)
            pygame.display.flip()
            pygame.time.delay(20)

        path.pop()  # Remove current from path if no valid neighbors
        return False

    # Start DFS from entrance
    dfs(entrance)
    maze[exit[1], exit[0]] = 4

    # Mark the solution path
    for px, py in path:
        maze[py, px] = 5  # Mark as part of the solution path
        path_create_sound.play()
        # Visualization for solution path
        if visualize:
            visualize_maze(screen, maze)
            pygame.display.flip()
            pygame.time.delay(50)

    # Ensure the entrance and exit are properly marked
    maze[entrance[1], entrance[0]] = 5
    maze[exit[1], exit[0]] = 5

    path_complete_sound.play()


def solve_maze_flood_fill(maze, screen, visualize=True):
    """
    Solve the maze using flood-fill algorithm and visualize the process.

    Args:
        maze (numpy.ndarray): The maze grid where 0 = path, 1 = wall, 2 = entrance, 3 = exit.
        screen (pygame.Surface): Pygame screen for visualization.
        visualize (bool): Whether to visualize the process.
    """
    # Find entrance and exit
    entrance = None
    exit = None
    for y in range(maze.shape[0]):
        for x in range(maze.shape[1]):
            if maze[y, x] == 2:
                entrance = (x, y)
            elif maze[y, x] == 3:
                exit = (x, y)

    if not entrance or not exit:
        print("Maze must have an entrance (2) and exit (3).")
        return

    # Flood-fill algorithm
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # Right, Left, Down, Up
    queue = [entrance]
    visited = set()
    parents = {}  # To reconstruct the path

    maze[entrance[1], entrance[0]] = 4

    while queue:
        current = queue.pop(0)
        x, y = current

        # Mark as visited
        if current != entrance:
            maze[y, x] = 4  # Mark as part of the flood-fill path

        visited.add(current)

        # Check if we've reached the exit
        if current == exit:
            break

        # Explore neighbors
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            neighbor = (nx, ny)

            if (0 <= nx < maze.shape[1] and 0 <= ny < maze.shape[0] and
                    neighbor not in visited and maze[ny, nx] in [0, 3]):
                queue.append(neighbor)
                parents[neighbor] = current
                visited.add(neighbor)

        # Visualization
        if visualize:
            visualize_maze(screen, maze)
            pygame.display.flip()
            pygame.time.delay(20)  # Adjust delay for speed
            pygame.event.pump()  # Handle Pygame events (e.g., quit)

    # Reconstruct the path
    if exit in parents:
        path = []
        current = exit
        while current != entrance:
            path.append(current)
            current = parents[current]
        path.append(entrance)
        path.reverse()

        # Mark the solution path
        for px, py in path:
            if maze[py, px] not in [2, 3]:  # Skip entrance and exit
                maze[py, px] = 5  # Mark as part of the solution path

            # Visualization
            if visualize:
                visualize_maze(screen, maze)
                pygame.display.flip()
                pygame.time.delay(50)

    # Final visualization
    visualize_maze(screen, maze)
    pygame.display.flip()


def carve_passages_kruskal(maze, width, height, screen=None, visualize=True):
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # Right, Left, Down, Up

    # Helper function to find the index of a cell
    def cell_index(x, y):
        return y * width + x

    # Initialize disjoint sets for each cell
    parent = list(range(width * height))
    rank = [0] * (width * height)

    def find(x):
        """Find the root of the set containing x."""
        if parent[x] != x:
            parent[x] = find(parent[x])  # Path compression
        return parent[x]

    def union(x, y):
        """Union the sets containing x and y."""
        root_x = find(x)
        root_y = find(y)
        if root_x != root_y:
            # Union by rank
            if rank[root_x] > rank[root_y]:
                parent[root_y] = root_x
            elif rank[root_x] < rank[root_y]:
                parent[root_x] = root_y
            else:
                parent[root_y] = root_x
                rank[root_x] += 1

    # List of all walls (edges) between cells
    walls = []
    for y in range(height):
        for x in range(width):
            if x < width - 1:  # Horizontal wall
                walls.append(((x, y), (x + 1, y)))
            if y < height - 1:  # Vertical wall
                walls.append(((x, y), (x, y + 1)))

    # Shuffle walls to randomize
    random.shuffle(walls)

    # Process walls
    for wall in walls:
        (x1, y1), (x2, y2) = wall

        # Check if the cells belong to different sets
        idx1 = cell_index(x1, y1)
        idx2 = cell_index(x2, y2)
        if find(idx1) != find(idx2):
            # Remove the wall
            wall_x, wall_y = (x1 + x2 + 1), (y1 + y2 + 1)  # Wall is in between cells
            maze[wall_y, wall_x] = 0
            maze[2 * y1 + 1, 2 * x1 + 1] = 0
            maze[2 * y2 + 1, 2 * x2 + 1] = 0

            # Union the sets
            union(idx1, idx2)

            wall_carve_sound.play()

            # Visualize if enabled
            if visualize and screen:
                visualize_maze(screen, maze)
                pygame.display.flip()
                pygame.time.delay(20)  # Adjust delay for speed
                pygame.event.pump()  # Handle Pygame events (e.g., quit)

    return maze


def main():
    width, height = 10, 20  # Maze dimensions

    maze = generate_maze(width, height)

    screen_size = (
        maze.shape[1] * CELL_SIZE,
        maze.shape[0] * CELL_SIZE
    )
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption("Maze Generation")

    # Run maze generation
    carve_passages_kruskal(maze, width, height, screen=screen, visualize=False)
    add_maze_entrance_and_exit(maze)
    visualize_maze(screen, maze)
    save_maze_to_png(screen)

    solve_maze_flood_fill(maze,screen,True)

    # Wait until the user closes the window
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    save_maze_to_png(screen)

        pygame.display.update()  # Update the display
        pygame.time.Clock().tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
