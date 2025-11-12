from zipfile import ZipFile

import numpy as np
from skimage.measure import marching_cubes

from src.convert.common import SegmentationId, get_segmentation_annotations
from src.io.cif.read.lattice import parse_lattice_bcif
from src.models.cvsx.cvsx_annotations import DescriptionData
from src.models.cvsx.cvsx_file import CVSXFile
from src.models.mvsx.mvsx_entry import MVSXSegmentation
from src.models.mvsx.mvsx_segmentation import MVSXMeshSegmentation
from src.models.read.lattice import LatticeCif
from src.utils import get_hex_color, rgba_to_opacity, smooth_3d_volume


def get_lattice_segmentation_descriptions(
    cvsx_file: CVSXFile,
) -> dict[SegmentationId, list[DescriptionData]]:
    descriptions_map: dict[SegmentationId, list[DescriptionData]] = {}

    for description_data in cvsx_file.annotations.descriptions.values():
        if description_data.target_kind != "lattice":
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


def get_lattice_cif(cvsx_path: str, inner_path: str) -> LatticeCif:
    with ZipFile(cvsx_path, "r") as z:
        with z.open(inner_path) as f:
            bcif_data = f.read()
            lattice_cif: LatticeCif = parse_lattice_bcif(bcif_data)
            return lattice_cif


def get_mesh_data_for_lattice_segment(
    lattice_cif: LatticeCif,
    segment_id: int,
    smooth_iterations: int = 1,
) -> np.ndarray:
    values = lattice_cif.segmentation_block.segmentation_data_3d.values
    info = lattice_cif.segmentation_block.volume_data_3d_info

    # original sample counts (before padding)
    nx, ny, nz = (
        int(info.sample_count_0),
        int(info.sample_count_1),
        int(info.sample_count_2),
    )

    # Read flat list into 3D array using the same order as earlier code:
    # values are stored z-major (slowest), so reshape -> transpose to (x,y,z)
    data = np.array(values, dtype=np.float32).reshape((nz, ny, nx))
    data = np.transpose(data, (2, 1, 0))  # -> shape (nx, ny, nz)

    # Binary mask for the requested segment
    data_3d_values = np.where(data == segment_id, 1.0, 0.0)

    # Pad with one voxel border (background = 0)
    padded = np.pad(
        data_3d_values,
        ((1, 1), (1, 1), (1, 1)),
        mode="constant",
        constant_values=0.0,
    )

    # Optional smoothing
    if smooth_iterations and smooth_iterations > 0:
        padded = smooth_3d_volume(padded, iterations=smooth_iterations)

    sample_count_0 = nx + 2
    sample_count_1 = ny + 2
    sample_count_2 = nz + 2

    # Flatten back into CIF order (reverse of the reshape/transposition above)
    values = np.transpose(padded, (2, 1, 0))

    nx, ny, nz = (
        sample_count_0,
        sample_count_1,
        sample_count_2,
    )

    data = values.reshape((nz, ny, nx)).transpose((2, 1, 0))

    # data_3d_values = np.where(data == segment_id, 1.0, 0.0)

    # padded = np.pad(
    #     data_3d_values,
    #     ((1, 1), (1, 1), (1, 1)),
    #     mode="constant",
    #     constant_values=0.0,
    # )

    verts, faces, normals, values = marching_cubes(data, level=0.5)

    # inverted
    faces = faces[:, ::-1]

    # Scale vertices to match volume dimensions

    # Calculate voxel sizes from spacegroup cell sizes
    voxel_size_x = info.spacegroup_cell_size_0 / info.sample_count_0
    voxel_size_y = info.spacegroup_cell_size_1 / info.sample_count_1
    voxel_size_z = info.spacegroup_cell_size_2 / info.sample_count_2

    # Scale vertices (subtract 1 to account for padding offset)
    verts[:, 0] = (verts[:, 0] - 1) * voxel_size_x
    verts[:, 1] = (verts[:, 1] - 1) * voxel_size_y
    verts[:, 2] = (verts[:, 2] - 1) * voxel_size_z

    # # Get value from metadata
    # center = 182.399995
    # verts -= center

    print(info.origin_0)

    vertices = verts
    indices = faces
    triangle_groups = np.zeros(len(faces))

    return vertices, indices, triangle_groups


def get_list_of_all_lattice_segmentations(
    cvsx_file: CVSXFile,
) -> list[MVSXSegmentation]:
    if not cvsx_file.index.latticeSegmentations:
        return []

    mvsx_segmentations = []
    segmentation_annotations = get_segmentation_annotations(cvsx_file)
    segmentation_descriptions = get_lattice_segmentation_descriptions(cvsx_file)

    for (
        source_filepath,
        segmentation_info,
    ) in cvsx_file.index.latticeSegmentations.items():
        segmentation_id = segmentation_info.segmentationId
        timeframe_id = segmentation_info.timeframeIndex

        lattice_cif = get_lattice_cif(cvsx_file.filepath, source_filepath)

        segment_ids = lattice_cif.segmentation_block.segmentation_data_table.segment_id
        # remove background
        segment_ids = set(segment_ids) - {0}

        for segment_id in segment_ids:
            filepath = f"lattice_{segment_id}_{segmentation_id}_{timeframe_id}.mvsj"
            destination_filepath = f"segmentations/{filepath}"
            annotation = segmentation_annotations.get((segmentation_id, segment_id))
            descriptions = segmentation_descriptions.get((segmentation_id, segment_id))

            color = get_hex_color(annotation)
            opacity = rgba_to_opacity(annotation)

            # sanity check
            if annotation:
                assert annotation.segment_kind == "lattice"
                assert annotation.segment_id == segment_id
                assert annotation.segmentation_id == segmentation_id
                assert annotation.time == timeframe_id

            vertices, indices, triangle_groups = get_mesh_data_for_lattice_segment(
                lattice_cif,
                segment_id,
            )

            mvsx_segmentation = MVSXMeshSegmentation(
                type="lattice",
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
