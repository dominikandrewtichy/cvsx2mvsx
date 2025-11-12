import numpy as np

from src.models.cvsx.cvsx_file import CVSXFile
from src.models.read.geometric import CylinderShape


def get_cylinder_shape_mesh(cvsx_file: CVSXFile, shape: CylinderShape):
    """
    Generate a cylinder mesh from a Cylinder shape primitive.
    Supports both regular cylinders and tapered cylinders (cones).

    Returns:
        vertices: numpy array of vertex positions
        indices: numpy array of triangle indices
        triangle_groups: numpy array of group IDs for each triangle
    """
    # Cylinder tessellation parameters
    radial_segments = 32  # Number of segments around the circumference

    # Calculate cylinder axis and properties
    start = np.array(shape.start, dtype=np.float32)
    end = np.array(shape.end, dtype=np.float32)
    axis = end - start
    height = np.linalg.norm(axis)
    axis_normalized = (
        axis / height if height > 0 else np.array([0, 1, 0], dtype=np.float32)
    )

    # Create a perpendicular vector to the axis for the circular cross-section
    # Choose a vector that's not parallel to the axis
    if abs(axis_normalized[0]) < 0.9:
        perpendicular = np.array([1, 0, 0], dtype=np.float32)
    else:
        perpendicular = np.array([0, 1, 0], dtype=np.float32)

    # Create orthonormal basis for the cylinder
    u = np.cross(axis_normalized, perpendicular)
    u = u / np.linalg.norm(u)
    v = np.cross(axis_normalized, u)
    v = v / np.linalg.norm(v)

    vertices = []
    indices = []

    # Generate vertices for bottom and top circles
    for i in range(radial_segments):
        angle = 2 * np.pi * i / radial_segments
        cos_angle = np.cos(angle)
        sin_angle = np.sin(angle)

        # Bottom circle vertex
        offset_bottom = shape.radius_bottom * (cos_angle * u + sin_angle * v)
        vertex_bottom = start + offset_bottom
        vertices.append(vertex_bottom)

        # Top circle vertex
        offset_top = shape.radius_top * (cos_angle * u + sin_angle * v)
        vertex_top = end + offset_top
        vertices.append(vertex_top)

    # Add center vertices for caps
    center_bottom_idx = len(vertices)
    vertices.append(start)

    center_top_idx = len(vertices)
    vertices.append(end)

    vertices = np.array(vertices, dtype=np.float32)

    # Generate side triangles
    for i in range(radial_segments):
        next_i = (i + 1) % radial_segments

        bottom_current = 2 * i
        top_current = 2 * i + 1
        bottom_next = 2 * next_i
        top_next = 2 * next_i + 1

        # First triangle of quad (side)
        indices.append([bottom_current, bottom_next, top_current])
        # Second triangle of quad (side)
        indices.append([top_current, bottom_next, top_next])

    # Generate bottom cap triangles (only if radius > 0)
    if shape.radius_bottom > 1e-6:
        for i in range(radial_segments):
            next_i = (i + 1) % radial_segments
            bottom_current = 2 * i
            bottom_next = 2 * next_i
            # Triangle facing downward
            indices.append([center_bottom_idx, bottom_next, bottom_current])

    # Generate top cap triangles (only if radius > 0)
    if shape.radius_top > 1e-6:
        for i in range(radial_segments):
            next_i = (i + 1) % radial_segments
            top_current = 2 * i + 1
            top_next = 2 * next_i + 1
            # Triangle facing upward
            indices.append([center_top_idx, top_current, top_next])

    indices = np.array(indices, dtype=np.int32)

    # Create triangle groups (all triangles belong to group 0)
    triangle_groups = np.zeros(len(indices), dtype=np.float32)

    return vertices, indices, triangle_groups
