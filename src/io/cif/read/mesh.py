from ciftools.serialization import loads
from src.models.cif.read.common import VolumeData3dInfo
from src.models.cif.read.mesh import Mesh, MeshBlock, MeshCif, MeshTriangle, MeshVertex

from src.io.cif.read.common import find_block, find_category, to_item, to_ndarray


def parse_mesh_bcif(bcif_data: bytes) -> MeshCif:
    cif_file = loads(bcif_data, lazy=True)

    segmentation_block = find_block(cif_file, "VOLUME_INFO")
    if segmentation_block is None:
        raise ValueError("VOLUME_INFO data block not found in CIF file")

    volume_data_3d_info_category = find_category(
        segmentation_block, "volume_data_3d_info"
    )
    mesh_category = find_category(segmentation_block, "mesh")
    mesh_vertex_category = find_category(segmentation_block, "mesh_vertex")
    mesh_triangle_category = find_category(segmentation_block, "mesh_triangle")

    if not all(
        [
            volume_data_3d_info_category,
            mesh_category,
            mesh_vertex_category,
            mesh_triangle_category,
        ]
    ):
        raise ValueError("Segmentation data block is missing a category.")

    volume_data_3d_info_data = VolumeData3dInfo(
        name=to_item(volume_data_3d_info_category, "name"),
        axis_order_0=to_item(volume_data_3d_info_category, "axis_order[0]"),
        axis_order_1=to_item(volume_data_3d_info_category, "axis_order[1]"),
        axis_order_2=to_item(volume_data_3d_info_category, "axis_order[2]"),
        origin_0=to_item(volume_data_3d_info_category, "origin[0]"),
        origin_1=to_item(volume_data_3d_info_category, "origin[1]"),
        origin_2=to_item(volume_data_3d_info_category, "origin[2]"),
        dimensions_0=to_item(volume_data_3d_info_category, "dimensions[0]"),
        dimensions_1=to_item(volume_data_3d_info_category, "dimensions[1]"),
        dimensions_2=to_item(volume_data_3d_info_category, "dimensions[2]"),
        sample_rate=to_item(volume_data_3d_info_category, "sample_rate"),
        sample_count_0=to_item(volume_data_3d_info_category, "sample_count[0]"),
        sample_count_1=to_item(volume_data_3d_info_category, "sample_count[1]"),
        sample_count_2=to_item(volume_data_3d_info_category, "sample_count[2]"),
        spacegroup_number=to_item(volume_data_3d_info_category, "spacegroup_number"),
        spacegroup_cell_size_0=to_item(
            volume_data_3d_info_category, "spacegroup_cell_size[0]"
        ),
        spacegroup_cell_size_1=to_item(
            volume_data_3d_info_category, "spacegroup_cell_size[1]"
        ),
        spacegroup_cell_size_2=to_item(
            volume_data_3d_info_category, "spacegroup_cell_size[2]"
        ),
        spacegroup_cell_angles_0=to_item(
            volume_data_3d_info_category, "spacegroup_cell_angles[0]"
        ),
        spacegroup_cell_angles_1=to_item(
            volume_data_3d_info_category, "spacegroup_cell_angles[1]"
        ),
        spacegroup_cell_angles_2=to_item(
            volume_data_3d_info_category, "spacegroup_cell_angles[2]"
        ),
        mean_source=to_item(volume_data_3d_info_category, "mean_source"),
        mean_sampled=to_item(volume_data_3d_info_category, "mean_sampled"),
        sigma_source=to_item(volume_data_3d_info_category, "sigma_source"),
        sigma_sampled=to_item(volume_data_3d_info_category, "sigma_sampled"),
        min_source=to_item(volume_data_3d_info_category, "min_source"),
        min_sampled=to_item(volume_data_3d_info_category, "min_sampled"),
        max_source=to_item(volume_data_3d_info_category, "max_source"),
        max_sampled=to_item(volume_data_3d_info_category, "max_sampled"),
    )

    mesh_data = Mesh(
        id=to_item(mesh_category, "time_id"),
        channel_id=to_item(mesh_category, "channel_id"),
    )

    mesh_vertex_data = MeshVertex(
        mesh_id=to_ndarray("mesh_id"),
        vertex_id=to_ndarray("vertex_id"),
        x=to_ndarray("x"),
        y=to_ndarray("y"),
        z=to_ndarray("z"),
    )

    mesh_triangle_data = MeshTriangle(
        mesh_id=to_ndarray("mesh_id"),
        vertex_id=to_ndarray("vertex_id"),
    )

    mesh_block_data = MeshBlock(
        volume_data_3d_info=volume_data_3d_info_data,
        mesh=mesh_data,
        mesh_vertex=mesh_vertex_data,
        mesh_triangle=mesh_triangle_data,
    )

    return MeshCif(
        mesh_block=mesh_block_data,
    )
