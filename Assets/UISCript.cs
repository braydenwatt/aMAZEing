using UnityEngine;
using UnityEngine.UIElements;

public class UIManager : MonoBehaviour
{
    public BoardGenerator bG; // Reference to the BoardGenerator script

    private void OnEnable()
    {
        var rootVisualElement = GetComponent<UIDocument>().rootVisualElement;

        // Query for IntegerField, Buttons, and other UI elements
        var boardSizeInput = rootVisualElement.Q<IntegerField>("boardSizeInput");  // IntegerField for board size
        var generateMazeButton = rootVisualElement.Q<Button>("generateMazeButton");  // Button for generating the maze
        var hideViewButton = rootVisualElement.Q<Button>("hideView");  // Button for hiding/showing UI elements
        var solveMazeButton = rootVisualElement.Q<Button>("solveMazeButton");

        var genDrop = rootVisualElement.Q<DropdownField>("GenAlgo");  // Dropdown for selecting maze type
        var solveDrop = rootVisualElement.Q<DropdownField>("SolveAlgo"); 
        if (boardSizeInput == null || generateMazeButton == null || hideViewButton == null)
        {
            Debug.LogError("UI elements not found! Make sure the names match the ones in UI Builder.");
            return;
        }

        // Ensure BoardGenerator (bG) is assigned
        if (bG == null)
        {
            Debug.LogError("BoardGenerator is not assigned!");
            return;
        }

        // Add a click listener to the generateMazeButton
        generateMazeButton.clicked += () =>
        {
            Debug.Log("Generate Maze button clicked.");
            ToggleUIVisibility(rootVisualElement);  // Toggle the visibility of the UI elements
            OnGenerateMazeClicked(boardSizeInput.value, genDrop.value);
        };

        // Add a click listener to the hideViewButton
        hideViewButton.clicked += () =>
        {
            Debug.Log("hide ui  button clicked.");
            ToggleUIVisibility(rootVisualElement);  // Toggle the visibility of the UI elements
        };

        solveMazeButton.clicked += () =>
        {
            Debug.Log("Solve Maze button clicked.");
            ToggleUIVisibility(rootVisualElement);  // Toggle the visibility of the UI elements
            OnSolveMazeClicked(solveDrop.value);
        };


    }
    
    private void OnGenerateMazeClicked(int inputSize, string genDrop)
    {
        // Hide the UI elements when maze generation starts
        if (genDrop=="Kruskal")
        {
            bG.boardSize = inputSize;
            bG.StartCoroutine(bG.GenerateBoardAndMaze());
        }
    }

    private void OnSolveMazeClicked(string solveDrop)
    {
        if (solveDrop=="DFS")
        {
            bG.StartCoroutine(bG.SolveMazeDFS());
        }
    }

    private void ToggleUIVisibility(VisualElement rootVisualElement)
    {
        // Get the container for the rest of the UI elements that you want to show/hide
        var uiContainer = rootVisualElement.Q("uiContainer");  // Assuming the container has the class 'uiContainer'

        if (uiContainer == null)
        {
            Debug.LogError("UI container not found!");
            return;
        }

        // Toggle visibility of the container
        if (uiContainer.style.display == DisplayStyle.Flex)
        {
            // Hide the UI container
            uiContainer.style.display = DisplayStyle.None;
        }
        else
        {
            // Show the UI container
            uiContainer.style.display = DisplayStyle.Flex;
        }
    }
}