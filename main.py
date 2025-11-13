from zipfile import ZipFile

import numpy as np
from molviewspec import create_builder
from molviewspec.builder import GlobalMetadata, Primitives, Root, Snapshot, States
from molviewspec.mvsx_converter import mvsj_to_mvsx

from src.convert.geometric import get_list_of_all_geometric_segmentations
from src.convert.lattice import get_list_of_all_lattice_segmentations
from src.convert.mesh import get_list_of_all_mesh_segmentations
from src.convert.volume import get_list_of_all_volumes
from src.io.cvsx_loader import load_cvsx_entry
from src.models.cvsx.cvsx_file import CVSXFile
from src.models.mvsx.mvsx_segmentation import (
    MVSXGeometricSegmentation,
    MVSXMeshSegmentation,
    MVSXSegmentation,
)
from src.models.mvsx.mvsx_volume import MVSXVolume
from src.models.read.geometric import (
    BoxShape,
    CylinderShape,
    EllipsoidShape,
    PyramidShape,
    SphereShape,
    Vector3,
)


def axis_angle_to_rotation_matrix(axis: Vector3, angle: float) -> np.ndarray:
    axis = np.array(axis)
    axis = axis / np.linalg.norm(axis)  # Normalize

    cos_angle = np.cos(angle)
    sin_angle = np.sin(angle)
    K = np.array(
        [[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]]
    )
    rotation_matrix = np.eye(3) + sin_angle * K + (1 - cos_angle) * np.dot(K, K)
    return rotation_matrix


def create_transform_matrix(
    rotation_matrix: np.ndarray,
    translation: Vector3,
) -> np.ndarray:
    transform_matrix = np.eye(4)
    transform_matrix[:3, :3] = rotation_matrix
    transform_matrix[:3, 3] = translation
    return transform_matrix


def add_sphere_primitive(
    primitives: Primitives, shape: SphereShape, color: str, tooltip: str
) -> None:
    primitives.sphere(
        color=color,
        tooltip=tooltip,
        center=shape.center,
        radius=shape.radius,
    )


def add_box_primitive(
    builder: Root,
    shape: BoxShape,
    color: str,
    tooltip: str,
    opacity: float,
) -> None:
    # Convert rotation parameters to rotation matrix
    rotation_matrix = axis_angle_to_rotation_matrix(
        shape.rotation.axis, shape.rotation.radians
    )

    # Box extent is half the scaling
    extent = tuple(s / 2 for s in shape.scaling)

    # Create 4x4 transformation matrix for instancing
    transform_matrix = create_transform_matrix(rotation_matrix, shape.translation)

    # Use instances parameter to apply transformation
    primitives_group = builder.primitives(
        snapshot_key="",
        opacity=opacity,
        instances=[transform_matrix.flatten("F").tolist()],  # Column major
    )
    primitives_group.box(
        face_color=color,
        tooltip=tooltip,
        center=(0, 0, 0),  # Center at origin, instance transform handles position
        extent=extent,
        show_faces=True,
    )


def generate_cylinder_mesh(
    start: Vector3,
    end: Vector3,
    radius_bottom: float,
    radius_top: float,
    num_segments: int = 32,
) -> tuple[list[float], list[int]]:
    start = np.array(start)
    end = np.array(end)

    direction = end - start
    height = np.linalg.norm(direction)
    direction = direction / height

    vertices = []
    indices = []

    # Generate circle points for bottom and top
    angles = np.linspace(0, 2 * np.pi, num_segments, endpoint=False)

    # Find perpendicular vectors for circle generation
    if abs(direction[2]) < 0.9:
        perp1 = np.cross(direction, [0, 0, 1])
    else:
        perp1 = np.cross(direction, [1, 0, 0])
    perp1 = perp1 / np.linalg.norm(perp1)
    perp2 = np.cross(direction, perp1)

    # Bottom circle vertices
    for angle in angles:
        x = start + (perp1 * np.cos(angle) + perp2 * np.sin(angle)) * radius_bottom
        vertices.extend(x.tolist())

    # Top circle vertices
    for angle in angles:
        x = end + (perp1 * np.cos(angle) + perp2 * np.sin(angle)) * radius_top
        vertices.extend(x.tolist())

    # Add center points for caps
    bottom_center_idx = len(vertices) // 3
    vertices.extend(start.tolist())
    top_center_idx = len(vertices) // 3
    vertices.extend(end.tolist())

    # Create triangles for sides
    for i in range(num_segments):
        next_i = (i + 1) % num_segments
        # Two triangles per segment
        indices.extend([i, next_i, i + num_segments])
        indices.extend([next_i, next_i + num_segments, i + num_segments])

    # Bottom cap
    for i in range(num_segments):
        next_i = (i + 1) % num_segments
        indices.extend([bottom_center_idx, next_i, i])

    # Top cap
    for i in range(num_segments):
        next_i = (i + 1) % num_segments
        indices.extend([top_center_idx, i + num_segments, next_i + num_segments])

    triangle_groups = [0] * len(vertices)

    return vertices, indices, triangle_groups


def add_cylinder_primitive(
    primitives: Primitives,
    shape: CylinderShape,
    color: str,
    tooltip: str,
) -> None:
    start = np.array(shape.start)
    end = np.array(shape.end)
    radius_bottom = shape.radius_bottom
    radius_top = shape.radius_top

    if np.isclose(radius_bottom, radius_top):
        # Uniform cylinder - use tube
        primitives.tube(
            color=color,
            tooltip=tooltip,
            start=tuple(start),
            end=tuple(end),
            radius=radius_bottom,
        )
    else:
        # Tapered cylinder (cone/frustum) - create custom mesh
        vertices, indices, triangle_groups = generate_cylinder_mesh(
            shape.start,
            shape.end,
            radius_bottom,
            radius_top,
        )

        primitives.mesh(
            color=color,
            tooltip=tooltip,
            vertices=vertices,
            indices=indices,
            triangle_groups=triangle_groups,
        )


def add_ellipsoid_primitive(
    primitives: Primitives,
    shape: EllipsoidShape,
    color: str,
    tooltip: str,
) -> None:
    """Add an ellipsoid primitive."""
    primitives.ellipsoid(
        color=color,
        tooltip=tooltip,
        center=shape.center,
        major_axis=shape.dir_major,
        minor_axis=shape.dir_minor,
        radius=shape.radius_scale,
    )


def generate_pyramid_mesh(
    translation: Vector3,
    scaling: Vector3,
    rotation_axis: Vector3,
    rotation_angle: float,
) -> tuple[list[float], list[int]]:
    translation = np.array(translation)
    scaling = np.array(scaling)

    # Create rotation matrix
    rotation_matrix = axis_angle_to_rotation_matrix(rotation_axis, rotation_angle)

    # Define pyramid vertices (apex at top, square base at bottom)
    base_verts = np.array(
        [
            [-0.5, -0.5, 0],
            [0.5, -0.5, 0],
            [0.5, 0.5, 0],
            [-0.5, 0.5, 0],
        ]
    )
    apex = np.array([[0, 0, 1]])

    # Apply scaling
    pyramid_verts = np.vstack([base_verts, apex]) * scaling

    # Apply rotation and translation
    pyramid_verts = (rotation_matrix @ pyramid_verts.T).T + translation

    # Create triangular faces with correct winding order (counter-clockwise from outside)
    indices = [
        # Base (2 triangles) - looking from below, counter-clockwise
        0,
        2,
        1,
        0,
        3,
        2,
        # Sides (4 triangles) - looking from outside, counter-clockwise
        0,
        1,
        4,
        1,
        2,
        4,
        2,
        3,
        4,
        3,
        0,
        4,
    ]

    vertices = pyramid_verts.flatten().tolist()
    triangle_groups = [0] * len(vertices)

    return vertices, indices, triangle_groups


def add_pyramid_primitive(
    primitives: Primitives, shape: PyramidShape, color: str, tooltip: str
) -> None:
    vertices, indices, triangle_groups = generate_pyramid_mesh(
        shape.translation,
        shape.scaling,
        shape.rotation.axis,
        shape.rotation.radians,
    )

    primitives.mesh(
        color=color,
        tooltip=tooltip,
        vertices=vertices,
        triangle_groups=triangle_groups,
        indices=indices,
    )


def add_geometric_segmentation(builder: Root, segmentation: MVSXGeometricSegmentation):
    primitives = builder.primitives(
        snapshot_key="",
        opacity=segmentation.opacity,
    )

    tooltip = get_segmentation_tooltip(segmentation)
    color = segmentation.color

    if segmentation.shape.kind == "sphere":
        add_sphere_primitive(
            primitives,
            segmentation.shape,
            color,
            tooltip,
        )
    elif segmentation.shape.kind == "box":
        add_box_primitive(
            builder,
            segmentation.shape,
            color,
            tooltip,
            segmentation.opacity,
        )
    elif segmentation.shape.kind == "cylinder":
        add_cylinder_primitive(
            primitives,
            segmentation.shape,
            color,
            tooltip,
        )
    elif segmentation.shape.kind == "ellipsoid":
        add_ellipsoid_primitive(
            primitives,
            segmentation.shape,
            color,
            tooltip,
        )
    elif segmentation.shape.kind == "pyramid":
        add_pyramid_primitive(
            primitives,
            segmentation.shape,
            color,
            tooltip,
        )
    else:
        raise ValueError(
            f"Unknown geometric primitives shape type: {segmentation.shape.kind}"
        )

    return builder


def create_index_snapshot(
    volumes: list[MVSXVolume],
    mesh_segmentations: list[MVSXMeshSegmentation],
    geometric_segmentations: list[MVSXGeometricSegmentation],
) -> Snapshot:
    builder = create_builder()

    for volume in volumes:
        add_volume(builder, volume)
    for mesh in mesh_segmentations:
        add_mesh_segmentation(builder, mesh)
    for geometric in geometric_segmentations:
        add_geometric_segmentation(builder, geometric)

    snapshot = builder.get_snapshot()

    return snapshot


def create_segmentation_primitives_files(
    mesh_segmentations: list[MVSXMeshSegmentation],
    geometric_segmentations: list[MVSXGeometricSegmentation],
):
    for mesh in mesh_segmentations:
        builder = create_builder()
        add_mesh_segmentation(builder, mesh)
        state = builder.get_state()
        if state.root.children != 1:
            raise ValueError("Expected state to contain exactly one child")
        primitives_node = state.root.children[0]
        if primitives_node.kind != "primitives":
            raise ValueError("Expected primitives node")
        with open(f"temp/{mesh.destination_filepath}", "w") as f:
            f.write(mesh)

    for geometric in geometric_segmentations:
        add_geometric_segmentation(builder, geometric)


def get_segmentation_tooltip(segmentation: MVSXSegmentation) -> str:
    tooltip = ""
    segmentation_id = segmentation.segmentation_id
    segment_id = segmentation.segment_id
    tooltip += f"{segmentation_id} | Segment {segment_id}"
    for description in segmentation.descriptions:
        if description.name is not None:
            tooltip += "\n\n"
            tooltip += f"{description.name}"
        if not description.external_references:
            continue
        for reference in description.external_references:
            tooltip += "\n\n"
            tooltip += f"{reference.label} [{reference.resource}:{reference.accession}]"
    return tooltip


def add_volume(builder: Root, volume: MVSXVolume):
    volume_raw = builder.download(url=volume.destination_filepath)
    volume_cif = volume_raw.parse(format="bcif")
    volume_data = volume_cif.volume(channel_id=volume.channel_id)
    volume_representation = volume_data.representation(
        type="isosurface",
        relative_isovalue=volume.isovalue,
        show_faces=True,
        show_wireframe=False,
    )
    volume_representation.color(color=volume.color)
    volume_representation.opacity(opacity=volume.opacity)
    return builder


def add_mesh_segmentation(builder: Root, segmentation: MVSXMeshSegmentation):
    builder.primitives(
        snapshot_key="",
        opacity=segmentation.opacity,
    ).mesh(
        color=segmentation.color,
        vertices=segmentation.vertices.ravel().tolist(),
        indices=segmentation.indices.ravel().tolist(),
        triangle_groups=segmentation.triangle_groups.ravel().tolist(),
        tooltip=get_segmentation_tooltip(segmentation),
    )
    return builder


def convert_cvsx_to_mvsx(cvsx_path: str):
    cvsx_file: CVSXFile = load_cvsx_entry(cvsx_path)
    volumes: list[MVSXVolume] = get_list_of_all_volumes(cvsx_file)
    mesh_segmentations: list[MVSXMeshSegmentation] = [
        *get_list_of_all_mesh_segmentations(cvsx_file),
        *get_list_of_all_lattice_segmentations(cvsx_file),
    ]
    geometric_segmentations: list[MVSXGeometricSegmentation] = (
        get_list_of_all_geometric_segmentations(cvsx_file)
    )

    # print("volumes")
    # for volume in volumes:
    #     print(volume.get_fields_str())
    #     print()

    # print("mesh segmentations")
    # for segmentation in mesh_segmentations:
    #     print(segmentation.get_fields_str())
    #     print()

    # print("lattice segmentations")
    # for segmentation in lattice_segmentations:
    #     print(segmentation.get_fields_str())
    #     print()

    # print("geometric segmentations")
    # for segmentation in geometric_segmentations:
    #     print(segmentation.get_fields_str())
    #     print()

    # copy over data
    for volume in volumes:
        with ZipFile(cvsx_path, "r") as zip_ref:
            zip_ref.extract(volume.source_filepath, "temp/volumes")

    index_snapshot = create_index_snapshot(
        volumes,
        mesh_segmentations,
        geometric_segmentations,
    )
    states = States(
        metadata=GlobalMetadata(),
        snapshots=[index_snapshot],
    )

    with open("temp/mesh.mvsj", "w") as f:
        f.write(states.model_dump_json(indent=2, exclude_none=True))

    mvsj_to_mvsx(
        input_mvsj_path="temp/mesh.mvsj",
        output_mvsx_path="temp/mesh.mvsx",
    )


if __name__ == "__main__":
    # TODO: add switch for the lattice segmentation conversion
    convert_cvsx_to_mvsx("data/cvsx/zipped/custom-tubhiswt.cvsx")
