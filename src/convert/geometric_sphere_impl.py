import numpy as np

from src.models.cvsx.cvsx_file import CVSXFile
from src.models.read.geometric import SphereShape


def get_sphere_shape_mesh(cvsx_file: CVSXFile, shape: SphereShape):
    """
    Generate a sphere mesh from a Sphere shape primitive.

    Returns:
        vertices: numpy array of vertex positions
        indices: numpy array of triangle indices
        triangle_groups: numpy array of group IDs for each triangle
    """
    # Sphere tessellation parameters
    # Using UV sphere with latitude/longitude divisions
    u_segments = 32  # longitude divisions
    v_segments = 16  # latitude divisions

    vertices = []

    # Generate vertices
    for i in range(v_segments + 1):
        theta = i * np.pi / v_segments  # latitude angle from 0 to pi
        sin_theta = np.sin(theta)
        cos_theta = np.cos(theta)

        for j in range(u_segments + 1):
            phi = j * 2 * np.pi / u_segments  # longitude angle from 0 to 2pi
            sin_phi = np.sin(phi)
            cos_phi = np.cos(phi)

            # Unit sphere position
            x = sin_theta * cos_phi
            y = cos_theta
            z = sin_theta * sin_phi

            # Scale by radius and translate to center
            vertex = np.array(
                [
                    shape.center[0] + shape.radius * x,
                    shape.center[1] + shape.radius * y,
                    shape.center[2] + shape.radius * z,
                ],
                dtype=np.float32,
            )

            vertices.append(vertex)

    vertices = np.array(vertices, dtype=np.float32)

    # Generate triangle indices
    indices = []
    for i in range(v_segments):
        for j in range(u_segments):
            # Current vertex index
            first = i * (u_segments + 1) + j
            second = first + u_segments + 1

            # First triangle of quad
            indices.append([first, second, first + 1])
            # Second triangle of quad
            indices.append([second, second + 1, first + 1])

    indices = np.array(indices, dtype=np.int32)

    # Create triangle groups (all triangles belong to group 0)
    triangle_groups = np.zeros(len(indices), dtype=np.float32)

    return vertices, indices, triangle_groups
