import os
from zipfile import ZipFile

import numpy as np

from src.convert.common import SegmentationId, get_segmentation_annotations
from src.io.cif.read.mesh import parse_mesh_bcif
from src.models.cvsx.cvsx_annotations import DescriptionData
from src.models.cvsx.cvsx_file import CVSXFile
from src.models.mvsx.mvsx_entry import MVSXSegmentation
from src.models.read.mesh import MeshCif
from src.utils import get_hex_color, rgba_to_opacity


def get_segmentation_descriptions(
    cvsx_file: CVSXFile,
) -> dict[SegmentationId, list[DescriptionData]]:
    descriptions_map: dict[SegmentationId, list[DescriptionData]] = {}

    for description_data in cvsx_file.annotations.descriptions.values():
        if description_data.target_kind != "mesh":
            continue
        if not description_data.target_id:
            continue

        segmentation_id = description_data.target_id.segmentation_id
        segment_id = description_data.target_id.segment_id

        key = (segmentation_id, segment_id)
        if key not in descriptions_map:
            descriptions_map[key] = []
        descriptions_map[key].append(description_data)

    return descriptions_map


def get_info_from_mesh_filepath(filepath: str) -> tuple[str, str, str]:
    filename = os.path.basename(filepath)
    name, ext = os.path.splitext(filename)

    if ext.lower() != ".bcif":
        raise ValueError(f"Expected .bcif extension, got {ext}")

    parts = name.split("_")
    if len(parts) != 4:
        raise ValueError(
            f"Expected 4 parts in mesh segmentation filename, got {len(parts)}: {parts}"
        )

    file_type, segment_id, segmentation_id, timeframe_id = parts

    if file_type != "mesh":
        raise ValueError(f"Expected mesh in filepath, got {file_type}")

    segment_id = int(segment_id)
    timeframe_id = int(timeframe_id)

    return segment_id, segmentation_id, timeframe_id


def get_mesh_data(
    cvsx_path: str,
    inner_path: str,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    with ZipFile(cvsx_path, "r") as z:
        with z.open(inner_path) as f:
            bcif_data = f.read()
            mesh_cif: MeshCif = parse_mesh_bcif(bcif_data)

    x = np.array(mesh_cif.mesh_block.mesh_vertex.x, dtype=np.float64)
    y = np.array(mesh_cif.mesh_block.mesh_vertex.y, dtype=np.float64)
    z = np.array(mesh_cif.mesh_block.mesh_vertex.z, dtype=np.float64)

    indices = mesh_cif.mesh_block.mesh_triangle.vertex_id
    triangle_groups = mesh_cif.mesh_block.mesh_triangle.mesh_id

    spacegroup_cell_size_0 = (
        mesh_cif.mesh_block.volume_data_3d_info.spacegroup_cell_size_0
    )
    spacegroup_cell_size_1 = (
        mesh_cif.mesh_block.volume_data_3d_info.spacegroup_cell_size_1
    )
    spacegroup_cell_size_2 = (
        mesh_cif.mesh_block.volume_data_3d_info.spacegroup_cell_size_2
    )

    sample_count_0 = mesh_cif.mesh_block.volume_data_3d_info.sample_count_0
    sample_count_1 = mesh_cif.mesh_block.volume_data_3d_info.sample_count_1
    sample_count_2 = mesh_cif.mesh_block.volume_data_3d_info.sample_count_2

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
    indices = indices.reshape(-1, 3)[:, [0, 2, 1]]

    return vertices, indices, triangle_groups


def get_list_of_all_mesh_segmentations(
    cvsx_file: CVSXFile,
) -> list[MVSXSegmentation]:
    if not cvsx_file.index.meshSegmentations:
        return []

    mvsx_segmentations = []
    segmentation_annotations = get_segmentation_annotations(cvsx_file)
    segmentation_descriptions = get_segmentation_descriptions(cvsx_file)

    for mesh_segmentation in cvsx_file.index.meshSegmentations:
        for source_filepath in mesh_segmentation.segmentsFilenames:
            parts = get_info_from_mesh_filepath(source_filepath)
            segment_id, segmentation_id, timeframe_id = parts
            destination_filepath = f"segmentations/{source_filepath}"
            annotation = segmentation_annotations.get((segmentation_id, segment_id))
            descriptions = segmentation_descriptions.get((segmentation_id, segment_id))

            if annotation:
                color = get_hex_color(annotation.color)
                opacity = rgba_to_opacity(annotation.color)
            else:
                color = "#ffffff"
                opacity = 1

            # sanity check
            if annotation:
                assert annotation.segment_kind == "mesh"
                assert annotation.segment_id == segment_id
                assert annotation.segmentation_id == segmentation_id
                assert annotation.time == timeframe_id

            vertices, indices, triangle_groups = get_mesh_data(
                cvsx_file.filepath,
                source_filepath,
            )

            mvsx_segmentation = MVSXSegmentation(
                type="mesh",
                source_filepath=source_filepath,
                destination_filepath=destination_filepath,
                timeframe_id=timeframe_id,
                segmentation_id=segmentation_id,
                segment_id=segment_id,
                vertices=vertices,
                indices=indices,
                triangle_groups=triangle_groups,
                color=color,
                opacity=opacity,
                descriptions=descriptions,
            )

            mvsx_segmentations.append(mvsx_segmentation)

    return mvsx_segmentations
