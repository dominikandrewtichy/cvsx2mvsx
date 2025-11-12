import numpy as np

from src.models.cvsx.cvsx_file import CVSXFile
from src.models.read.geometric import EllipsoidShape


def get_ellipsoid_shape_mesh(cvsx_file: CVSXFile, shape: EllipsoidShape):
    """
    Generate an ellipsoid mesh from an Ellipsoid shape primitive.
    An ellipsoid is a sphere scaled differently along three axes and oriented in space.

    Returns:
        vertices: numpy array of vertex positions
        indices: numpy array of triangle indices
        triangle_groups: numpy array of group IDs for each triangle
    """
    # Ellipsoid tessellation parameters
    # Using UV sphere with latitude/longitude divisions
    u_segments = 32  # longitude divisions
    v_segments = 16  # latitude divisions

    # Build orthonormal basis from dir_major and dir_minor
    dir_major = np.array(shape.dir_major, dtype=np.float32)
    dir_minor = np.array(shape.dir_minor, dtype=np.float32)

    # Normalize the direction vectors
    dir_major = dir_major / np.linalg.norm(dir_major)
    dir_minor = dir_minor / np.linalg.norm(dir_minor)

    # Compute the third axis (cross product)
    dir_third = np.cross(dir_major, dir_minor)
    dir_third = dir_third / np.linalg.norm(dir_third)

    # Create transformation matrix from local to world space
    # The columns are the basis vectors
    basis_matrix = np.column_stack([dir_major, dir_minor, dir_third])

    # Get radius scaling
    radius_scale = np.array(shape.radius_scale, dtype=np.float32)

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
            y = sin_theta * sin_phi
            z = cos_theta

            # Create local position vector
            local_pos = np.array([x, y, z], dtype=np.float32)

            # Apply radius scaling
            scaled_pos = local_pos * radius_scale

            # Transform to world space using basis matrix
            world_pos = np.dot(basis_matrix, scaled_pos)

            # Translate to center
            vertex = world_pos + np.array(shape.center, dtype=np.float32)

            vertices.append(vertex)

    vertices = np.array(vertices, dtype=np.float32)

    # Generate triangle indices (same as sphere)
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
