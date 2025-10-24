import json
import math
from itertools import chain
from urllib.request import urlopen

import numpy as np
from ciftools.serialization import loads
from molviewspec import create_builder
from molviewspec.builder import Root

from src.utils.utils import rgba_to_hex
from src.utils.volseg_models import AnnotationsMetadata


def simple_example():
    builder = create_builder()
    structure = (
        builder.download(
            url="https://www.ebi.ac.uk/pdbe/entry-files/download/1cbs_updated.cif"
        )
        .parse(format="mmcif")
        .model_structure()
        .component()
        .representation()
        .color(color="blue")
    )

    builder.camera(
        position=[50.36118149218165, 20.9925140189241, 100.9795310025729],
        target=[17.36118149218165, 20.9925140189241, 26.614665478675132],
        up=[0, 1, 0],
    )

    return builder


def emd_19111_volume_with_protein():
    builder: Root = create_builder()

    volume_cif = builder.download(
        url="http://localhost:8000/data/emd-19111/volume_0_0.bcif"
    ).parse(format="bcif")
    volume_data = volume_cif.volume(channel_id="0")
    volume_representation = volume_data.representation(
        type="isosurface",
        relative_isovalue=6.542392525311452,
        show_wireframe=False,
        show_faces=True,
    )
    volume_representation.color(color="white").opacity(opacity=0.4)

    (
        builder.download(url="https://www.ebi.ac.uk/pdbe/entry-files/download/8rex.cif")
        .parse(format="mmcif")
        .model_structure()
        .component()
        .representation()
        .color(color="red")
    )

    return builder


def idr_13457537_volumes():
    builder: Root = create_builder()
    segment_ids = [
        {
            "color": [1.0, 1.0, 1.0, 0.25098039215686274],
            "id": "b868a107-3e65-4949-b9f2-c12cf7d2ec64",
            "segment_id": 2371559,
            "segment_kind": "lattice",
            "segmentation_id": "0",
            "time": [0, 1, 10, 11, 12, 13, 14, 15, 16, 17, 2, 3, 4, 5, 6, 7, 8, 9],
        }
    ]
    for segment_id in segment_ids:
        volume_cif = builder.download(
            url=f"http://localhost:8000/data/idr-13457537/lattice_volumes/{segment_id['segment_id']}.cif"
        ).parse(format="mmcif")
        volume_data = volume_cif.volume(channel_id="0")
        volume_representation = volume_data.representation(
            type="isosurface",
            relative_isovalue=1,
            show_wireframe=False,
            show_faces=True,
        )
        volume_representation.color(color="green").opacity(opacity=1)

    return builder


def idr_13457537_volume() -> Root:
    builder = create_builder()
    volume_cif = builder.download(
        url="http://localhost:8000/data/idr-13457537/volume_Hyb probe_4.bcif"
    ).parse(format="bcif")
    volume_data = volume_cif.volume(channel_id="0")
    volume_representation = volume_data.representation(
        type="isosurface",
        relative_isovalue=1,
        show_wireframe=False,
        show_faces=True,
    )
    volume_representation.color(color="red").opacity(opacity=0.2)

    return builder


def empiar_10070_volume() -> Root:
    builder = create_builder()
    lattice_cif = builder.download(
        url="http://localhost:8000/data/empiar-10070/volume_0_0.bcif"
    ).parse(format="bcif")
    lattice_data = lattice_cif.volume(channel_id="0")
    lattice_representation = lattice_data.representation(
        type="isosurface",
        relative_isovalue=1,
        show_wireframe=False,
        show_faces=True,
    )
    lattice_representation.color(color="gray").opacity(opacity=0.2)

    return builder


def empiar_10070_mesh() -> Root:
    builder = create_builder()
    lattice_cif = builder.download(
        url="http://localhost:8000/data/empiar-10070/mesh_1_0_0.bcif"
    ).parse(format="bcif")
    lattice_data = lattice_cif.volume(channel_id="0")
    lattice_representation = lattice_data.representation(
        type="isosurface",
        relative_isovalue=1,
        show_wireframe=False,
        show_faces=True,
    )
    lattice_representation.color(color="gray").opacity(opacity=0.2)

    return builder


def cube_mesh():
    builder = create_builder()
    builder.primitives().mesh(
        vertices=[
            0,
            0,
            0,
            1,
            0,
            0,
            0,
            1,
            0,
            0,
            0,
            1,
            1,
            1,
            0,
            1,
            0,
            1,
            0,
            1,
            1,
            1,
            1,
            1,
        ],
        indices=[
            0,
            4,
            1,
            0,
            2,
            4,
            3,
            5,
            7,
            3,
            7,
            6,
            0,
            1,
            5,
            0,
            5,
            3,
            2,
            7,
            4,
            2,
            6,
            7,
            0,
            6,
            2,
            0,
            3,
            6,
            1,
            4,
            7,
            1,
            7,
            5,
        ],
        color="aquamarine",
        tooltip="cube",
        triangle_groups=[0] * 12,
    )
    return builder


def tetrahedron_mesh():
    builder = create_builder()
    builder.primitives().mesh(
        vertices=[
            # 4 vertices forming a tetrahedron
            0,
            0,
            0,  # 0 - base corner A
            1,
            0,
            0,  # 1 - base corner B
            0.5,
            0.866,
            0,  # 2 - base corner C (equilateral base)
            0.5,
            0.2887,
            0.816,  # 3 - top vertex D (centered above base)
        ],
        indices=[
            # Base (ABC) - face downwards
            0,
            2,
            1,
            # Side 1 (A-B-D)
            0,
            1,
            3,
            # Side 2 (B-C-D)
            1,
            2,
            3,
            # Side 3 (C-A-D)
            2,
            0,
            3,
        ],
        color="goldenrod",
        tooltip="tetrahedron",
        # 4 triangles total (one per face)
        triangle_groups=[0, 0, 0, 0],
    )
    return builder


def empiar_10070_all_mesh() -> Root:
    builder = create_builder()

    data = urlopen("http://localhost:8000/data/empiar-10070/annotations.json").read()
    annotations: AnnotationsMetadata = json.loads(data)

    for segment_annotation in annotations["segment_annotations"]:
        rgba_color = segment_annotation["color"]
        color = rgba_to_hex(*rgba_color)
        segment_id = segment_annotation["segment_id"]
        segment_kind = segment_annotation["segment_kind"]
        segmentation_id = segment_annotation["segmentation_id"]
        time = segment_annotation["time"]
        opacity = 1 if segment_id not in [13, 15] else 0.2
        filename = f"{segment_kind}_{segment_id}_{segmentation_id}_{time}.bcif"
        uri = f"http://localhost:8000/data/empiar-10070/{filename}"
        add_mesh_from_bcif(builder, uri, color, opacity)

    return builder


def get_cif_contents(uri: str):
    data = urlopen(uri).read()
    cif_file = loads(data, lazy=False)
    result = dict()
    for block_idx, block in enumerate(cif_file.data_blocks):
        for cat_idx, (cat_name, category) in enumerate(block.categories.items()):
            for col_idx, col_name in enumerate(category.field_names):
                col = category[col_name]
                values = col.as_ndarray()
                result[f"{cat_name}_{col_name}"] = values.tolist()

    return result


def add_mesh_from_bcif(builder: Root, uri: str, color: str, opacity: float):
    data = get_cif_contents(uri=uri)

    x = data["mesh_vertex_x"]
    y = data["mesh_vertex_y"]
    z = data["mesh_vertex_z"]
    indices = data["mesh_triangle_vertex_id"]
    triangle_groups = data["mesh_triangle_mesh_id"]
    zipped = zip(x, y, z)
    vertices = list(chain.from_iterable(zipped))
    flipped_indices = []
    for i in range(0, len(indices), 3):
        v0, v1, v2 = indices[i : i + 3]
        flipped_indices.extend([v0, v2, v1])  # flip v1 and v2

    # smoothed_vertices, smoothed_indices = smooth_mesh_taubin(
    #     vertices=vertices, indices=indices, iterations=5
    # )
    builder.primitives(opacity=opacity).mesh(
        vertices=vertices,
        indices=flipped_indices,
        triangle_groups=triangle_groups,
        color=color,
    )
    return builder


def ball_mesh():
    builder = create_builder()
    # identity matrix
    I = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
    # translated by (x=10, y=20, z=30)
    T = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 50, 20, 30, 1]
    S = [2, 0, 0, 0, 0, 2, 0, 0, 0, 0, 2, 0, 10, 20, 30, 1]
    transforms = [I, T, S]
    vertices, indices = generate_ball_mesh(
        radius=10,
        lat_segments=16,
        lon_segments=2 * 16,
    )
    builder.primitives(
        opacity=1,
        instances=transforms,
    ).mesh(
        vertices=vertices,
        indices=indices,
        triangle_groups=[0] * len(indices),
        tooltip="Ball",
        color="blue",
        show_triangles=True,
        show_wireframe=False,
    )
    return builder


def ball_mesh_with_label():
    builder = create_builder()
    vertices, indices = generate_ball_mesh(
        radius=10,
        lat_segments=16,
        lon_segments=2 * 16,
    )

    mesh_prim = builder.primitives(opacity=1).mesh(
        vertices=vertices,
        indices=indices,
        triangle_groups=[0] * len(indices),
        tooltip="Ball",
        color="red",
        show_wireframe=False,
        show_triangles=True,
    )

    line = builder.primitives().lines(
        vertices=[0, 0, 0, 10, 10, 10],
        indices=[0, 1],
        color="green",
        ref="line",
    )

    # Add label primitive
    builder.primitives().label(
        position=[0, 0, 14],  # above the ball along Z
        text="Ball",
        label_color="white",
        label_size=5,
        label_offset=0,
    )

    return builder


def dynamic_controls_large_ball():
    builder = create_builder()

    vertices, indices = generate_ball_mesh(
        radius=10,
        lat_segments=128,
        lon_segments=2 * 128,
    )
    builder.primitives(
        instances=[[1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 20, 30, 1]]
    ).mesh(
        ref="large_ball",
        vertices=vertices,
        indices=indices,
        triangle_groups=[0] * len(indices),
        tooltip="Ball",
        color="blue",
        show_triangles=True,
        show_wireframe=False,
    )

    vertices, indices = generate_ball_mesh(
        radius=0.5,
        lat_segments=64,
        lon_segments=2 * 64,
    )

    builder.primitives().mesh(
        vertices=vertices,
        indices=indices,
        triangle_groups=[0] * len(indices),
        color="cyan",
        show_wireframe=False,
        show_triangles=True,
    )

    builder.primitives().lines(
        ref="line",
        vertices=[-10, 0, 0, 10, 0, 0],
        indices=[0, 1],
        color="green",
    )

    return builder


def generate_ball_mesh(radius=1.0, lat_segments=16, lon_segments=32):
    vertices = []
    indices = []

    # Generate vertices
    for i in range(lat_segments + 1):
        theta = math.pi * i / lat_segments
        sin_theta = math.sin(theta)
        cos_theta = math.cos(theta)

        for j in range(lon_segments + 1):
            phi = 2 * math.pi * j / lon_segments
            sin_phi = math.sin(phi)
            cos_phi = math.cos(phi)

            x = radius * sin_theta * cos_phi
            y = radius * cos_theta
            z = radius * sin_theta * sin_phi

            vertices.extend([x, y, z])

    # Generate indices (now using counter-clockwise winding)
    for i in range(lat_segments):
        for j in range(lon_segments):
            first = i * (lon_segments + 1) + j
            second = first + lon_segments + 1

            # First triangle
            indices.extend([first, first + 1, second])
            # Second triangle
            indices.extend([second, first + 1, second + 1])

    return vertices, indices


def add_lattice_from_bcif(builder: Root, segment_id: int, color: str, opacity: float):
    data = get_cif_contents(uri="")

    x = data["mesh_vertex_x"]
    y = data["mesh_vertex_y"]
    z = data["mesh_vertex_z"]
    indices = data["mesh_triangle_vertex_id"]
    triangle_groups = data["mesh_triangle_mesh_id"]
    zipped = zip(x, y, z)
    vertices = list(chain.from_iterable(zipped))
    flipped_indices = []
    for i in range(0, len(indices), 3):
        v0, v1, v2 = indices[i : i + 3]
        flipped_indices.extend([v0, v2, v1])  # flip v1 and v2

    # smoothed_vertices, smoothed_indices = smooth_mesh_taubin(
    #     vertices=vertices, indices=indices, iterations=5
    # )
    builder.primitives(opacity=opacity).mesh(
        vertices=vertices,
        indices=flipped_indices,
        triangle_groups=triangle_groups,
        color=color,
    )
    return builder


def smooth_mesh_taubin(vertices, indices, iterations=10, lambda_filter=0.5, mu=-0.53):
    """
    Smooths a mesh using Taubin smoothing (prevents shrinkage).

    vertices: flat list [x0, y0, z0, x1, y1, z1, ...]
    indices: flat list [i0, i1, i2, ...]
    iterations: number of smoothing iterations
    lambda_filter: smoothing factor
    mu: shrinkage factor

    Returns: smoothed_vertices_flat, smoothed_indices_flat
    """

    from itertools import chain

    import numpy as np
    import open3d as o3d

    if len(vertices) == 0 or len(indices) == 0:
        raise ValueError("Vertices or indices are empty!")

    # Reshape vertices into Nx3
    vertices = np.array(vertices, dtype=np.float64).reshape((-1, 3))

    # Convert indices to Mx3 faces
    if len(indices) % 3 != 0:
        raise ValueError(f"Indices length must be multiple of 3, got {len(indices)}")
    faces = np.array(
        [indices[i : i + 3] for i in range(0, len(indices), 3)], dtype=np.int32
    )

    # Flip triangle winding
    faces = faces[:, [0, 2, 1]]

    # Create Open3D mesh
    o3d_mesh = o3d.geometry.TriangleMesh()
    o3d_mesh.vertices = o3d.utility.Vector3dVector(vertices)
    o3d_mesh.triangles = o3d.utility.Vector3iVector(faces)
    o3d_mesh.compute_vertex_normals()

    # Apply Taubin smoothing
    smoothed_mesh = o3d_mesh.filter_smooth_taubin(
        number_of_iterations=iterations, lambda_filter=lambda_filter, mu=mu
    )
    smoothed_mesh.compute_vertex_normals()

    # Convert back to flat lists
    smoothed_vertices_flat = list(
        chain.from_iterable(np.asarray(smoothed_mesh.vertices).tolist())
    )
    smoothed_indices_flat = list(
        chain.from_iterable(np.asarray(smoothed_mesh.triangles).tolist())
    )

    return smoothed_vertices_flat, smoothed_indices_flat


def smooth_mesh(vertices, indices, iterations=2):
    if len(vertices) == 0 or len(indices) == 0:
        raise ValueError("Vertices or indices are empty!")

    # Reshape vertices into Nx3
    vertices = np.array(vertices, dtype=np.float64).reshape((-1, 3))

    # Group indices into Mx3 faces
    if len(indices) % 3 != 0:
        raise ValueError(f"Indices length must be multiple of 3, got {len(indices)}")
    faces = np.array(
        [indices[i : i + 3] for i in range(0, len(indices), 3)], dtype=np.int32
    )

    # Flip triangle winding to face outward
    faces = faces[:, [0, 2, 1]]

    # Create Open3D mesh
    o3d_mesh = o3d.geometry.TriangleMesh()
    o3d_mesh.vertices = o3d.utility.Vector3dVector(vertices)
    o3d_mesh.triangles = o3d.utility.Vector3iVector(faces)
    o3d_mesh.compute_vertex_normals()

    # Apply Laplacian smoothing
    smoothed_mesh = o3d_mesh.filter_smooth_laplacian(number_of_iterations=iterations)
    smoothed_mesh.compute_vertex_normals()

    # Convert back to flat lists for Mol*
    smoothed_vertices_flat = list(
        chain.from_iterable(np.asarray(smoothed_mesh.vertices).tolist())
    )
    smoothed_indices_flat = list(
        chain.from_iterable(np.asarray(smoothed_mesh.triangles).tolist())
    )

    return smoothed_vertices_flat, smoothed_indices_flat


def smoothen():
    with open("output.json", "r") as file:
        data = json.load(file)

    x = data["mesh_vertex_x"]
    y = data["mesh_vertex_y"]
    z = data["mesh_vertex_z"]
    indices = data["mesh_triangle_vertex_id"]
    zipped = zip(x, y, z)
    zipped_list = [list(t) for t in zipped]
    vertices = list(chain.from_iterable(zipped))
    grouped = [indices[i : i + 3] for i in range(0, len(indices), 3)]

    vertices = np.array(zipped_list)
    faces = np.array(grouped)
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)

    # Convert to Open3D mesh
    o3d_mesh = o3d.geometry.TriangleMesh()
    o3d_mesh.vertices = o3d.utility.Vector3dVector(mesh.vertices)
    o3d_mesh.triangles = o3d.utility.Vector3iVector(mesh.faces)
    o3d_mesh.compute_vertex_normals()

    # Apply Laplacian smoothing
    smoothed_mesh: o3d.geometry.TriangleMesh = o3d_mesh.filter_smooth_laplacian(
        number_of_iterations=10
    )

    triangles = list(chain.from_iterable(np.asarray(smoothed_mesh.triangles).tolist()))[
        :30
    ]
    vertices = list(chain.from_iterable(np.asarray(smoothed_mesh.vertices).tolist()))[
        :30
    ]

    builder = create_builder()
    builder.primitives().mesh(
        vertices=vertices,
        indices=triangles,
        color="goldenrod",
        tooltip="something",
    )
    return builder
