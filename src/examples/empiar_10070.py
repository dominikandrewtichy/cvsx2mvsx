import json

import numpy as np
from ciftools.serialization import loads
from molviewspec import create_builder
from molviewspec.builder import Root

from src.convert.convert_all import rgba_to_hex_color
from src.io.cif.read.mesh import parse_mesh_bcif
from src.models.read.mesh import MeshCif


def empiar_10070_volume(builder: Root) -> Root:
    lattice_cif = builder.download(url="./volume_0_0.bcif").parse(format="bcif")
    lattice_data = lattice_cif.volume(channel_id="0")
    lattice_representation = lattice_data.representation(
        type="isosurface",
        relative_isovalue=1,
        show_wireframe=False,
        show_faces=True,
    )
    lattice_representation.color(color="gray").opacity(opacity=0.2)

    return builder


def empiar_10070_create_mesh_primitives() -> Root:
    with open("data/cvsx/unzipped/empiar-10070/annotations.json") as f:
        json_string = f.read()
        annotations = json.loads(json_string)

    for segment_annotation in annotations["segment_annotations"]:
        rgba_color = segment_annotation["color"]
        color = rgba_to_hex_color(rgba_color)
        segment_id = segment_annotation["segment_id"]
        segment_kind = segment_annotation["segment_kind"]
        segmentation_id = segment_annotation["segmentation_id"]
        time = segment_annotation["time"]
        opacity = 1
        filename = f"{segment_kind}_{segment_id}_{segmentation_id}_{time}"
        uri = f"data/cvsx/unzipped/empiar-10070/{filename}.bcif"
        add_mesh_from_bcif(uri, filename, color, opacity)


def get_cif_contents(uri: str):
    with open(uri, "rb") as f:
        data = f.read()
    cif_file = loads(data, lazy=False)
    result = dict()
    for block_idx, block in enumerate(cif_file.data_blocks):
        for cat_idx, (cat_name, category) in enumerate(block.categories.items()):
            for col_idx, col_name in enumerate(category.field_names):
                col = category[col_name]
                values = col.as_ndarray()
                result[f"{cat_name}_{col_name}"] = values.tolist()

    return result


def add_mesh_from_bcif(
    uri: str,
    segment_name: str,
    color: str,
    opacity: float,
):
    with open(uri, "rb") as f:
        data: MeshCif = parse_mesh_bcif(f.read())

    x = np.array(data.mesh_block.mesh_vertex.x, dtype=np.float64)
    y = np.array(data.mesh_block.mesh_vertex.y, dtype=np.float64)
    z = np.array(data.mesh_block.mesh_vertex.z, dtype=np.float64)

    indices = data.mesh_block.mesh_triangle.vertex_id
    triangle_groups = data.mesh_block.mesh_triangle.mesh_id

    spacegroup_cell_size_0 = data.mesh_block.volume_data_3d_info.spacegroup_cell_size_0
    spacegroup_cell_size_1 = data.mesh_block.volume_data_3d_info.spacegroup_cell_size_1
    spacegroup_cell_size_2 = data.mesh_block.volume_data_3d_info.spacegroup_cell_size_2

    sample_count_0 = data.mesh_block.volume_data_3d_info.sample_count_0
    sample_count_1 = data.mesh_block.volume_data_3d_info.sample_count_1
    sample_count_2 = data.mesh_block.volume_data_3d_info.sample_count_2

    voxel_size_x = spacegroup_cell_size_0 / sample_count_0
    voxel_size_y = spacegroup_cell_size_1 / sample_count_1
    voxel_size_z = spacegroup_cell_size_2 / sample_count_2

    x *= voxel_size_x
    y *= voxel_size_y
    z *= voxel_size_z

    x = np.round(x, 2)
    y = np.round(y, 2)
    z = np.round(z, 2)

    vertices = np.column_stack((x, y, z))

    indices_reshaped = indices.reshape(-1, 3)
    flipped_indices = indices_reshaped[:, [0, 2, 1]]

    builder = create_builder()
    builder.primitives(
        ref=f"{segment_name}",
        snapshot_key=f"{segment_name}",
        opacity=opacity,
    ).mesh(
        vertices=vertices.ravel().tolist(),
        indices=flipped_indices.ravel().tolist(),
        triangle_groups=triangle_groups.ravel().tolist(),
        color=color,
        tooltip=f"{segment_name}",
    )

    state = builder.get_state()
    primitives_node = state.root.children[0]

    with open(f"data/mvsx/unzipped/empiar-10070/{segment_name}.mvsj", "w") as f:
        f.write(
            json.dumps(
                obj=primitives_node.model_dump(exclude_none=True),
                separators=(",", ":"),
            )
        )
    # with open(f"data/mvsx/unzipped/empiar-10070/{segment_name}.msgpack", "wb") as f:
    #     packed = msgpack.packb(
    #         primitives_node.model_dump(exclude_none=True),
    #         use_bin_type=True,
    #     )
    #     f.write(packed)


def empiar_10070():
    builder = create_builder()
    empiar_10070_volume(builder)
    empiar_10070_create_mesh_primitives(builder)
    return builder
