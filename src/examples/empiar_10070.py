import json
from itertools import chain

from ciftools.serialization import loads
from molviewspec import create_builder
from molviewspec.builder import Root

from src.convert.convert_all import rgba_to_hex_color


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


def add_mesh_from_bcif(uri: str, filename: str, color: str, opacity: float):
    builder = create_builder()

    data = get_cif_contents(uri=uri)

    x = data["mesh_vertex_x"]
    y = data["mesh_vertex_y"]
    z = data["mesh_vertex_z"]
    indices = data["mesh_triangle_vertex_id"]
    triangle_groups = data["mesh_triangle_mesh_id"]

    # Load scaling info from volume_data_3d_info (if available)
    try:
        voxel_size_x = (
            data["volume_data_3d_info_spacegroup_cell_size[0]"][0]
            / data["volume_data_3d_info_sample_count[0]"][0]
        )
        voxel_size_y = (
            data["volume_data_3d_info_spacegroup_cell_size[1]"][0]
            / data["volume_data_3d_info_sample_count[1]"][0]
        )
        voxel_size_z = (
            data["volume_data_3d_info_spacegroup_cell_size[2]"][0]
            / data["volume_data_3d_info_sample_count[2]"][0]
        )
    except KeyError:
        # Fallback constant scaling if volume info not in mesh file
        voxel_size_x = voxel_size_y = voxel_size_z = 150.0

    # Scale coordinates
    x = [xi * voxel_size_x for xi in x]
    y = [yi * voxel_size_y for yi in y]
    z = [zi * voxel_size_z for zi in z]

    zipped = zip(x, y, z)
    vertices = list(chain.from_iterable(zipped))

    flipped_indices = []
    for i in range(0, len(indices), 3):
        v0, v1, v2 = indices[i : i + 3]
        flipped_indices.extend([v0, v2, v1])  # flip winding

    builder.primitives(
        ref=f"{filename}",
        snapshot_key=f"{filename}",
        opacity=opacity,
    ).mesh(
        vertices=vertices,
        indices=flipped_indices,
        triangle_groups=triangle_groups,
        color=color,
        tooltip=f"{filename}",
    )

    state = builder.get_state()
    primitives_node = state.root.children[0]

    with open(f"data/mvsx/unzipped/empiar-10070/{filename}.mvsj", "w") as f:
        f.write(
            primitives_node.model_dump_json(
                indent=2,
                exclude_none=True,
            )
        )


def empiar_10070():
    builder = create_builder()
    empiar_10070_volume(builder)
    empiar_10070_create_mesh_primitives(builder)
    return builder
