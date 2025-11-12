import numpy as np

from src.models.cvsx.cvsx_file import CVSXFile
from src.models.read.geometric import BoxShape


def get_box_shape_mesh(cvsx_file: CVSXFile, shape: BoxShape):
    """
    Generate a box mesh from a Box shape primitive.

    Returns:
        vertices: numpy array of shape (8, 3) containing vertex positions
        indices: numpy array of shape (12, 3) containing triangle indices
        triangle_groups: numpy array of shape (12,) containing group IDs for each triangle
    """
    # Create unit cube vertices centered at origin (ranges from -0.5 to 0.5)
    unit_vertices = np.array(
        [
            [-0.5, -0.5, -0.5],  # 0: back-bottom-left
            [0.5, -0.5, -0.5],  # 1: back-bottom-right
            [0.5, 0.5, -0.5],  # 2: back-top-right
            [-0.5, 0.5, -0.5],  # 3: back-top-left
            [-0.5, -0.5, 0.5],  # 4: front-bottom-left
            [0.5, -0.5, 0.5],  # 5: front-bottom-right
            [0.5, 0.5, 0.5],  # 6: front-top-right
            [-0.5, 0.5, 0.5],  # 7: front-top-left
        ],
        dtype=np.float32,
    )

    # Define triangles (12 triangles, 2 per face)
    # Using counter-clockwise winding order
    indices = np.array(
        [
            # Front face (z = 0.5)
            [4, 5, 6],
            [4, 6, 7],
            # Back face (z = -0.5)
            [1, 0, 3],
            [1, 3, 2],
            # Right face (x = 0.5)
            [5, 1, 2],
            [5, 2, 6],
            # Left face (x = -0.5)
            [0, 4, 7],
            [0, 7, 3],
            # Top face (y = 0.5)
            [7, 6, 2],
            [7, 2, 3],
            # Bottom face (y = -0.5)
            [0, 1, 5],
            [0, 5, 4],
        ],
        dtype=np.int32,
    )

    # Apply scaling
    vertices = unit_vertices * np.array(shape.scaling, dtype=np.float32)

    # Apply rotation
    axis = np.array(shape.rotation.axis, dtype=np.float32)
    axis = axis / np.linalg.norm(axis)  # Normalize axis
    angle = shape.rotation.radians

    # Rodrigues' rotation formula
    cos_angle = np.cos(angle)
    sin_angle = np.sin(angle)

    # Create rotation matrix
    K = np.array(
        [[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]],
        dtype=np.float32,
    )

    rotation_matrix = (
        np.eye(3, dtype=np.float32) + sin_angle * K + (1 - cos_angle) * np.dot(K, K)
    )

    # Apply rotation to all vertices
    vertices = np.dot(vertices, rotation_matrix.T)

    # Apply translation
    vertices = vertices + np.array(shape.translation, dtype=np.float32)

    # Create triangle groups (all triangles belong to group 0)
    triangle_groups = np.zeros(len(indices), dtype=np.float32)

    return vertices, indices, triangle_groups
