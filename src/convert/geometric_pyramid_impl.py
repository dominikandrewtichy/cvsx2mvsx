import numpy as np

from src.models.cvsx.cvsx_file import CVSXFile
from src.models.read.geometric import PyramidShape


def get_pyramid_shape_mesh(cvsx_file: CVSXFile, shape: PyramidShape):
    """
    Generate a pyramid mesh from a Pyramid shape primitive.
    Creates a square pyramid with base centered at origin and apex at (0, 1, 0).

    Returns:
        vertices: numpy array of vertex positions
        indices: numpy array of triangle indices
        triangle_groups: numpy array of group IDs for each triangle
    """
    # Create unit pyramid vertices
    # Base is a square from -0.5 to 0.5 on x and z, at y = 0
    # Apex is at (0, 1, 0)
    unit_vertices = np.array(
        [
            # Base vertices (y = 0)
            [-0.5, 0.0, -0.5],  # 0: back-left
            [0.5, 0.0, -0.5],  # 1: back-right
            [0.5, 0.0, 0.5],  # 2: front-right
            [-0.5, 0.0, 0.5],  # 3: front-left
            # Apex vertex (y = 1)
            [0.0, 1.0, 0.0],  # 4: apex
        ],
        dtype=np.float32,
    )

    # Define triangles
    indices = np.array(
        [
            # Base (2 triangles forming a square)
            [0, 2, 1],  # Base triangle 1
            [0, 3, 2],  # Base triangle 2
            # Side faces (4 triangular faces)
            [0, 1, 4],  # Back face
            [1, 2, 4],  # Right face
            [2, 3, 4],  # Front face
            [3, 0, 4],  # Left face
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
