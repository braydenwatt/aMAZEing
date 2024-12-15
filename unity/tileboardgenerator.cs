using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using System;

public class BoardGenerator : MonoBehaviour
{
    public GameObject tileQuadPrefab; // Assign your TileQuad prefab in the Inspector
    public GameObject tileRingPrefab; // Assign your TileRing prefab in the Inspector
    public GameObject solverBlockPrefab;
    public int boardSize = 9; // Default board size (n x n)
    public float spawnInterval = 0.05f; // Delay between each tile's spawn
    public float flyInDuration = 0.5f; // Duration of the fly-in animation
    public float flyInHeight = -5f; // Initial height from which tiles fly in
    public float ringFlyInDuration = 0.5f; // Duration of the ring fly-in animation
    public Material wallMaterial; // Material for walls
    public Material pathMaterial; // Material for paths
    
    

    private GameObject[,] tiles; // Store tile GameObjects
    private GameObject[,] tileRings; // Store ring GameObjects
    private int[,] maze; // Store the maze grid
    private bool tileFlyInComplete = false; // Flag to track tile fly-in completion
    private Vector2 entrance; // Store entrance position
    private Vector2 exit; // Store exit position

    void Start()
    {
        //StartCoroutine(GenerateBoardAndMaze());
    }

    public IEnumerator GenerateBoardAndMaze()
    {
        DeleteAllObjects();
        yield return StartCoroutine(GenerateBoardSequentially());
        maze = GenerateMaze(boardSize, boardSize);
        yield return StartCoroutine(PlaceTileRings()); // Place and animate tile rings
        yield return StartCoroutine(CarveMazeKruskal());
        AddMazeEntranceAndExit(); // Add entrance and exit to the maze
        VisualizeMaze();
        yield return StartCoroutine(RemoveWalls());
    }
    // Add this method to the BoardGenerator class
    void DeleteAllObjects()
    {
        // Delete tiles
        if (tiles != null)
        {
            foreach (GameObject tile in tiles)
            {
                if (tile != null)
                {
                    Destroy(tile);
                }
            }
            tiles = null;
        }

        // Delete tile rings
        if (tileRings != null)
        {
            foreach (GameObject ring in tileRings)
            {
                if (ring != null)
                {
                    Destroy(ring);
                }
            }
            tileRings = null;
        }

        // Reset maze
        maze = null;

        // Reset entrance and exit
        entrance = Vector2.zero;
        exit = Vector2.zero;

        // Reset tile fly-in complete flag
        tileFlyInComplete = false;

        Debug.Log("All board objects have been deleted.");
    }

    IEnumerator GenerateBoardSequentially()
    {
        if (tileQuadPrefab == null)
        {
            Debug.LogError("TileQuad prefab not assigned!");
            yield break;
        }

        Vector3 quadSize = tileQuadPrefab.transform.localScale;
        Vector3 boardOffset = new Vector3((2 * boardSize + 1) * quadSize.x * 0.5f, 0, (2 * boardSize + 1) * quadSize.z * 0.5f);
        tiles = new GameObject[2 * boardSize + 1, 2 * boardSize + 1];
        List<Coroutine> tileAnimations = new List<Coroutine>();

        for (int y = 0; y < 2 * boardSize + 1; y++)
        {
            for (int x = 0; x < 2 * boardSize + 1; x++)
            {
                Vector3 position = new Vector3(x * quadSize.x, 0, y * quadSize.z) - boardOffset;
                GameObject tile = Instantiate(tileQuadPrefab, position + Vector3.up * flyInHeight, Quaternion.Euler(90f, 0, 0));
                tile.transform.parent = transform;
                tiles[y, x] = tile;
                tileAnimations.Add(StartCoroutine(FlyInTile(tile, position)));
                yield return new WaitForSeconds(spawnInterval);
            }
        }

        // Wait for all tile animations to complete
        foreach (var animation in tileAnimations)
        {
            yield return animation;
        }

        tileFlyInComplete = true;
    }

    IEnumerator FlyInTile(GameObject tile, Vector3 finalPosition)
    {
        float elapsed = 0f;
        Vector3 startPosition = tile.transform.position;

        while (elapsed < flyInDuration)
        {
            tile.transform.position = Vector3.Lerp(startPosition, finalPosition, elapsed / flyInDuration);
            elapsed += Time.deltaTime;
            yield return null;
        }

        tile.transform.position = finalPosition;
    }

    int[,] GenerateMaze(int width, int height)
    {
        int mazeWidth = 2 * width + 1;
        int mazeHeight = 2 * height + 1;
        maze = new int[mazeHeight, mazeWidth];

        for (int y = 0; y < mazeHeight; y++)
            for (int x = 0; x < mazeWidth; x++)
                maze[y, x] = (y % 2 == 0 || x % 2 == 0) ? 1 : 0;

        return maze;
    }

    IEnumerator CarveMazeKruskal()
    {
        int cells = boardSize * boardSize;
        int[] parent = new int[cells];
        int[] rank = new int[cells];
        List<Tuple<int, int, int, int>> walls = new List<Tuple<int, int, int, int>>(); // (x1, y1, x2, y2)

        for (int y = 0; y < boardSize; y++)
        {
            for (int x = 0; x < boardSize; x++)
            {
                int idx = y * boardSize + x;
                parent[idx] = idx;

                if (x < boardSize - 1) walls.Add(Tuple.Create(x, y, x + 1, y));
                if (y < boardSize - 1) walls.Add(Tuple.Create(x, y, x, y + 1));
            }
        }

        walls.Sort((a, b) => UnityEngine.Random.Range(-1, 2));

        int Find(int x)
        {
            if (parent[x] != x) parent[x] = Find(parent[x]);
            return parent[x];
        }

        void Union(int x, int y)
        {
            int rootX = Find(x);
            int rootY = Find(y);

            if (rootX != rootY)
            {
                if (rank[rootX] > rank[rootY]) parent[rootY] = rootX;
                else if (rank[rootX] < rank[rootY]) parent[rootX] = rootY;
                else
                {
                    parent[rootY] = rootX;
                    rank[rootX]++;
                }
            }
        }

        foreach (var wall in walls)
        {
            int x1 = wall.Item1, y1 = wall.Item2, x2 = wall.Item3, y2 = wall.Item4;
            int cell1 = y1 * boardSize + x1;
            int cell2 = y2 * boardSize + x2;

            if (Find(cell1) != Find(cell2))
            {
                Union(cell1, cell2);
                maze[2 * y1 + 1 + (y2 - y1), 2 * x1 + 1 + (x2 - x1)] = 0; // Remove wall
                VisualizeMaze();
                yield return new WaitForSeconds(0.05f);
            }
        }
    }

    IEnumerator RemoveWalls()
    {
        // Iterate through the maze grid to find the walls (denoted by 0)
        for (int y = 0; y < maze.GetLength(0); y++)
        {
            for (int x = 0; x < maze.GetLength(1); x++)
            {
                // Check if it's a wall (denoted by 0 in the maze grid)
                if (maze[y, x] == 1)
                {
                    GameObject tile = tiles[y, x];
                    GameObject tileRing = tileRings[y, x]; // Get the corresponding ring

                    // Destroy the corresponding ring
                    Destroy(tileRing);

                    // Start the animation of the tile falling after the ring is destroyed
                    StartCoroutine(AnimateTileFalling(tile));

                    // Optionally, wait a bit before processing the next wall
                    yield return new WaitForSeconds(0.1f); // Adjust as needed for animation timing
                }
            }
        }
    }

    // Coroutine to animate the tile falling and then destroy it
    IEnumerator AnimateTileFalling(GameObject tile)
    {
        float fallSpeed = 2f; // Adjust the speed of falling
        float fallDistance = 5f; // How far the tile will fall
        Vector3 startPosition = tile.transform.position;
        Vector3 targetPosition = startPosition + Vector3.down * fallDistance;

        float elapsedTime = 0f;

        // Animate the tile falling down
        while (elapsedTime < fallSpeed)
        {
            tile.transform.position = Vector3.Lerp(startPosition, targetPosition, elapsedTime / fallSpeed);
            elapsedTime += Time.deltaTime;
            yield return null;
        }

        // Ensure the final position is exactly at the target
        tile.transform.position = targetPosition;

        // After the animation, destroy the tile
        Destroy(tile);
    }

    void VisualizeMaze()
    {
        for (int y = 0; y < maze.GetLength(0); y++)
        {
            for (int x = 0; x < maze.GetLength(1); x++)
            {
                Renderer renderer = tiles[y, x].GetComponent<Renderer>();
                if (renderer != null)
                {
                    if (maze[y, x] == 1) // Wall
                    {
                        renderer.material = wallMaterial;
                    }
                    else if (maze[y, x] == 0) // Path
                    {
                        renderer.material = pathMaterial;
                    }
                    else if (maze[y, x] == 2) // Start (entrance)
                    {
                        renderer.material.color = Color.green; // Set to green for the start tile
                    }
                    else if (maze[y, x] == 3) // End (exit)
                    {
                        renderer.material.color = Color.red; // Set to red for the end tile
                    }
                }
            }
        }
    }

    // Place rings above tiles and animate them flying up
    IEnumerator PlaceTileRings()
    {
        // Wait until all tiles have finished flying in
        while (!tileFlyInComplete)
        {
            yield return null;
        }

        tileRings = new GameObject[2 * boardSize + 1, 2 * boardSize + 1];

        // Place a ring slightly below the final position (at Y = -1) and animate upwards
        for (int y = 0; y < 2 * boardSize + 1; y++)
        {
            for (int x = 0; x < 2 * boardSize + 1; x++)
            {
                Vector3 tilePosition = tiles[y, x].transform.position;

                // Set the initial position of the tile ring just below the final position (e.g., Y = -1)
                GameObject tileRing = Instantiate(tileRingPrefab, new Vector3(tilePosition.x, -0.1f, tilePosition.z), Quaternion.Euler(90f, 0, 0));
                tileRing.transform.parent = transform;

                tileRings[y, x] = tileRing;
            }
        }

        // Animate all tile rings flying up to their final position
        yield return StartCoroutine(FlyRingsUp());
    }

    // Animate all rings flying up to their final position at the same time
    IEnumerator FlyRingsUp()
    {
        float elapsedTime = 0f;
        float flyInHeight = 0.04f; // Final Y position for the rings

        // Move all rings from their starting position to the target position
        while (elapsedTime < ringFlyInDuration)
        {
            float yPosition = Mathf.Lerp(-.11f, flyInHeight, elapsedTime / ringFlyInDuration);
            foreach (GameObject ring in tileRings)
            {
                ring.transform.position = new Vector3(ring.transform.position.x, yPosition, ring.transform.position.z);
            }
            elapsedTime += Time.deltaTime;
            yield return null;
        }

        // Ensure all rings are at the final position
        foreach (GameObject ring in tileRings)
        {
            ring.transform.position = new Vector3(ring.transform.position.x, flyInHeight, ring.transform.position.z);
        }
    }

    void AddMazeEntranceAndExit()
    {
        // Randomly choose a wall side for the entrance and exit
        List<Vector2> leftWallCandidates = new List<Vector2>();
        List<Vector2> rightWallCandidates = new List<Vector2>();

        for (int y = 1; y < maze.GetLength(0) - 1; y++)
        {
            if (maze[y, 1] == 0 && maze[y, 0] == 1)
                leftWallCandidates.Add(new Vector2(y, 0)); // Left wall candidate

            if (maze[y, maze.GetLength(1) - 2] == 0 && maze[y, maze.GetLength(1) - 1] == 1)
                rightWallCandidates.Add(new Vector2(y, maze.GetLength(1) - 1)); // Right wall candidate
        }

        if (leftWallCandidates.Count > 0 && rightWallCandidates.Count > 0)
        {
            entrance = leftWallCandidates[UnityEngine.Random.Range(0, leftWallCandidates.Count)];
            exit = rightWallCandidates[UnityEngine.Random.Range(0, rightWallCandidates.Count)];
        }
        else if (leftWallCandidates.Count > 0)
        {
            entrance = leftWallCandidates[UnityEngine.Random.Range(0, leftWallCandidates.Count)];
            exit = leftWallCandidates[UnityEngine.Random.Range(0, leftWallCandidates.Count)];
        }
        else if (rightWallCandidates.Count > 0)
        {
            entrance = rightWallCandidates[UnityEngine.Random.Range(0, rightWallCandidates.Count)];
            exit = rightWallCandidates[UnityEngine.Random.Range(0, rightWallCandidates.Count)];
        }

        // Mark entrance and exit positions
        maze[(int)entrance.x, (int)entrance.y] = 2; // Entrance
        maze[(int)exit.x, (int)exit.y] = 3; // Exit
    }

    // Add this method to the BoardGenerator class
    public IEnumerator SolveMazeDFS()
    {
        // Ensure maze is generated
        if (maze == null)
        {
            Debug.LogError("Maze not generated yet!");
            yield break;
        }

        // Find start position (where value is 2)
        Vector2Int startPos = FindPositionInMaze(2);
        Vector3 startTilePos = tiles[startPos.x, startPos.y].transform.position;
        Vector3 vector3Pos = new Vector3(startTilePos.x, 0.45f, startTilePos.z);
        GameObject solverBlock = Instantiate(solverBlockPrefab, vector3Pos, Quaternion.identity);

        // Sanity check for start position
        if (startPos.x == -1 || startPos.y == -1)
        {
            Debug.LogError("Start position not found!");
            yield break;
        }

        // Create a stack for DFS, a set to track visited nodes, and a previous array for backtracking
        Stack<Vector2Int> stack = new Stack<Vector2Int>();
        HashSet<Vector2Int> visited = new HashSet<Vector2Int>();
        Vector2Int[,] previous = new Vector2Int[maze.GetLength(0), maze.GetLength(1)];

        // Push the starting node onto the stack and mark it as visited
        stack.Push(startPos);
        visited.Add(startPos);

        bool pathFound = false;
        Vector2Int endPos = new Vector2Int(-1, -1);

        // Directions: up, right, down, left
        Vector2Int[] directions = new Vector2Int[]
        {
            new Vector2Int(-1, 0),   // Up
            new Vector2Int(0, 1),    // Right
            new Vector2Int(1, 0),    // Down
            new Vector2Int(0, -1)    // Left
        };

        // Start DFS loop
        while (stack.Count > 0 && !pathFound) // Continue only if not found yet
        {
            Vector2Int current = stack.Peek(); // Get the current cell, but do not pop yet

            // Check if current cell is the exit (value 3)
            if (maze[current.x, current.y] == 3)
            {
                pathFound = true; // Path is found
                endPos = current;
                break; // Exit the loop as we've found the endpoint
            }

            bool moved = false; // To track if we are moving to a new cell or backtracking

            // Explore neighbors
            foreach (Vector2Int next in directions)
            {
                Vector2Int neighborPos = new Vector2Int(current.x + next.x, current.y + next.y);

                // Check if neighbor is within bounds, is a path (0 or 3), and hasn't been visited
                if (neighborPos.x >= 0 && neighborPos.x < maze.GetLength(0) &&
                    neighborPos.y >= 0 && neighborPos.y < maze.GetLength(1) &&
                    (maze[neighborPos.x, neighborPos.y] == 0 || maze[neighborPos.x, neighborPos.y] == 3) &&
                    !visited.Contains(neighborPos))
                {
                    // Move to the next cell
                    stack.Push(neighborPos);
                    visited.Add(neighborPos); // Mark as visited
                    previous[neighborPos.x, neighborPos.y] = current;
                    VisualizeExplorationStep(neighborPos, solverBlock); // Visualize forward movement
                    yield return new WaitForSeconds(1f); // Optional delay for visualization

                    moved = true; // We moved forward, so no need to backtrack yet
                    break; // Stop checking other neighbors
                }
            }

            // If we didn't move (i.e., we're backtracking), pop the stack, visualize it, and go to the previous node
            if (!moved)
            {
                // Pop the stack (backtrack)
                Vector2Int backtrackPos = stack.Pop();
                VisualizeExplorationStep(backtrackPos, solverBlock); // Visualize backtracking
                yield return new WaitForSeconds(1f);
                Vector2Int peek = stack.Peek(); // Get the current cell, but do not pop yet

                // Explore neighbors
                foreach (Vector2Int next in directions)
                {
                    Vector2Int neighborPos = new Vector2Int(peek.x + next.x, peek.y + next.y);

                    // Check if neighbor is within bounds, is a path (0 or 3), and hasn't been visited
                    if (neighborPos.x >= 0 && neighborPos.x < maze.GetLength(0) &&
                        neighborPos.y >= 0 && neighborPos.y < maze.GetLength(1) &&
                        (maze[neighborPos.x, neighborPos.y] == 0 || maze[neighborPos.x, neighborPos.y] == 3) &&
                        !visited.Contains(neighborPos))
                    {

                        VisualizeExplorationStep(peek, solverBlock); // Visualize forward movement
                        yield return new WaitForSeconds(1f); // Optional delay for visualization
                    }
                }
            }
        }

        // If path found, reconstruct and visualize the path from end to start
        if (pathFound)
        {
            // Visualize the solution path from end to start
            yield return StartCoroutine(VisualizePath(startPos, endPos, previous));
        }
        else
        {
            Debug.Log("No path found!");
        }
    }
    // Helper method to find a specific value in the maze
    private Vector2Int FindPositionInMaze(int value)
    {
        for (int x = 0; x < maze.GetLength(0); x++)
        {
            for (int y = 0; y < maze.GetLength(1); y++)
            {
                if (maze[x, y] == value)
                {
                    return new Vector2Int(x, y);
                }
            }
        }
        return new Vector2Int(-1, -1);
    }

    void VisualizeExplorationStep(Vector2Int pos, GameObject solverBlock)
    {
        // Get the next tile position
        Vector3 nextTilePos = tiles[pos.x, pos.y].transform.position;
        Vector3 targetPos = new Vector3(nextTilePos.x, 0.45f, nextTilePos.z);

        // Start the animation coroutine
        StartCoroutine(AnimateBlockMove(solverBlock, targetPos));
    }
    public IEnumerator AnimateBlockMove(GameObject solverBlock, Vector3 targetPos)
    {
        // Get the current position of the solver block
        Vector3 startPos = solverBlock.transform.position;

        // Time duration for the animation
        float duration = 1.0f;
        float elapsedTime = 0f;

        // Determine the direction of movement (difference between start and target positions)
        Vector3 moveDirection = targetPos - startPos;

        // Calculate the midpoint between start and target positions to simulate the arc
        Vector3 midpoint = (startPos + targetPos) / 2;

        // We want to "lift" the block slightly to make it appear as if it's moving in an arc
        midpoint.y += 1.0f; // Adjust the height to simulate the semi-circle path

        // Determine the axis of rotation (this will be the same for both up/down and left/right movement)
        Vector3 rotationAxis = Vector3.Cross(Vector3.up, moveDirection.normalized);

        // Animate the block's movement along the semi-circular path
        while (elapsedTime < duration)
        {
            // Calculate the percentage of the animation progress
            float t = elapsedTime / duration;

            // Interpolate the position using a cubic bezier-like curve (for smooth arc movement)
            Vector3 position = Vector3.Lerp(Vector3.Lerp(startPos, midpoint, t), Vector3.Lerp(midpoint, targetPos, t), t);

            // Move the solver block along the path
            solverBlock.transform.position = position;

            // Interpolate the rotation for smooth flipping effect
            // Rotate around the calculated axis to simulate the "flip" effect as the block moves along the arc
            Quaternion targetRotation = Quaternion.AngleAxis(180f * t, rotationAxis);

            // Apply the rotation gradually (smoothly rotate to the target)
            solverBlock.transform.rotation = Quaternion.Slerp(solverBlock.transform.rotation, targetRotation, t);

            // Increment elapsed time
            elapsedTime += Time.deltaTime;

            // Wait for the next frame
            yield return null;
        }

        // Ensure the final position and rotation are set exactly
        solverBlock.transform.position = targetPos;
        solverBlock.transform.rotation = Quaternion.LookRotation(targetPos - solverBlock.transform.position); // Final rotation to face target
    }
    IEnumerator VisualizePath(Vector2Int start, Vector2Int end, Vector2Int[,] previous)
    {
        // Create a path list by backtracking from end to start
        List<Vector2Int> path = new List<Vector2Int>();
        Vector2Int current = end;

        while (!current.Equals(start))
        {
            path.Add(current);
            current = previous[current.x, current.y];
        }
        path.Add(start);
        path.Reverse();

        // Visualize path with a distinct color
        Material pathMat = new Material(pathMaterial);
        pathMat.color = Color.yellow;

        // Gradually reveal the path
        for (int i = 1; i < path.Count - 1; i++)
        {
            Vector2Int pos = path[i];
            Renderer renderer = tiles[pos.x, pos.y].GetComponent<Renderer>();
            
            if (renderer != null)
            {
                // Only change color if not the start or end tile
                if (maze[pos.x, pos.y] != 2 && maze[pos.x, pos.y] != 3)
                {
                    renderer.material = pathMat;
                }
            }

            yield return new WaitForSeconds(0.1f);
        }
    }
}