using UnityEngine;

public class CustomCameraController : MonoBehaviour
{
    [Header("Camera Settings")]
    public float initialHeight = 10f;  // Initial height above origin
    public float initialAngle = 45f;   // Initial diagonal angle
    public float zoomSpeed = 5f;       // Speed of zooming
    public float minZoomDistance = 2f; // Minimum zoom distance from origin
    public float horizontalRotationSpeed = 5f;   // Speed of horizontal camera rotation
    public float verticalRotationSpeed = 5f;     // Speed of vertical camera rotation

    [Header("Rotation Constraints")]
    public float minVerticalAngle = 15f;   // Minimum vertical angle from horizontal plane
    public float maxVerticalAngle = 80f;   // Maximum vertical angle from horizontal plane

    private float currentDistance;
    private float currentHorizontalAngle = 0f;
    private float currentVerticalAngle;
    private Vector3 pivotPoint = Vector3.zero;
    private bool isDragging = false;
    private Vector3 lastMousePosition;

    void Start()
    {
        // Set initial camera position
        currentDistance = initialHeight / Mathf.Tan(initialAngle * Mathf.Deg2Rad);
        currentVerticalAngle = initialAngle;
        PositionCamera();
    }

    void Update()
    {
        // Zoom handling
        float scrollWheel = Input.GetAxis("Mouse ScrollWheel");
        if (scrollWheel != 0)
        {
            // Adjust zoom distance
            currentDistance -= scrollWheel * zoomSpeed;
            
            // Enforce minimum zoom limit
            currentDistance = Mathf.Max(currentDistance, minZoomDistance);
            
            PositionCamera();
        }

        // Rotation handling
        HandleCameraRotation();
    }

    void HandleCameraRotation()
    {
        // Left mouse button rotation
        if (Input.GetMouseButtonDown(0))
        {
            isDragging = true;
            lastMousePosition = Input.mousePosition;
        }
        else if (Input.GetMouseButtonUp(0))
        {
            isDragging = false;
        }

        if (isDragging)
        {
            // Calculate mouse drag delta
            Vector3 delta = Input.mousePosition - lastMousePosition;
            
            // Horizontal rotation (left/right)
            currentHorizontalAngle -= delta.x * horizontalRotationSpeed;
            
            // Vertical rotation (up/down)
            currentVerticalAngle -= delta.y * verticalRotationSpeed;
            
            // Clamp vertical angle to prevent going below min or above max
            currentVerticalAngle = Mathf.Clamp(currentVerticalAngle, minVerticalAngle, maxVerticalAngle);
            
            // Update last mouse position
            lastMousePosition = Input.mousePosition;
            
            // Reposition camera
            PositionCamera();
        }
    }

    void PositionCamera()
    {
        // Convert angles to radians
        float radHorizontalAngle = currentHorizontalAngle * Mathf.Deg2Rad;
        float radVerticalAngle = currentVerticalAngle * Mathf.Deg2Rad;

        // Calculate new camera position based on distance, horizontal and vertical angles
        float x = pivotPoint.x + currentDistance * Mathf.Sin(radHorizontalAngle) * Mathf.Cos(radVerticalAngle);
        float y = pivotPoint.y + currentDistance * Mathf.Sin(radVerticalAngle);
        float z = pivotPoint.z + currentDistance * Mathf.Cos(radHorizontalAngle) * Mathf.Cos(radVerticalAngle);

        transform.position = new Vector3(x, y, z);
        transform.LookAt(pivotPoint);
    }
}