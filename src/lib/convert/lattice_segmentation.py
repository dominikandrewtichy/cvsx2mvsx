from typing import Any
from zipfile import ZipFile

import numpy as np
from ciftools.models.data import CIFCategory, CIFDataBlock, CIFFile
from ciftools.serialization import create_binary_writer, loads
from pydantic import BaseModel

from lib.models.cif.common import (
    VolumeData3DInfo,
    VolumeDataTimeAndChannelInfo,
)
from lib.models.cif.lattice_segmentation import (
    LatticeSegmentationCIF,
    SegmentationBlock,
    SegmentationData3D,
    SegmentationDataTable,
)
from lib.models.cif_categories.volume_data_3d import VolumeData3dCategory
from lib.models.cif_categories.volume_data_3d_info import VolumeData3dInfoCategory


def read_bcif_file(zip_path: str, inner_path: str) -> bytes:
    with ZipFile(zip_path, "r") as f:
        return f.read(inner_path)


def pretty_print_lattice_cif(lattice_cif: BaseModel, indent: int = 0):
    """Pretty-print a LatticeSegmentationCIF model hierarchically."""
    indent_str = " " * indent

    if isinstance(lattice_cif, LatticeSegmentationCIF):
        print(f"{indent_str}CIF File:")
        print(f"{indent_str}  BLOCK SERVER")
        print(f"{indent_str}  BLOCK SEGMENTATION_DATA")
        pretty_print_lattice_cif(lattice_cif.segmentation_block, indent + 4)

    elif isinstance(lattice_cif, SegmentationBlock):
        print(f"{indent_str}CATEGORY: volume_data_3d_info")
        pretty_print_lattice_cif(lattice_cif.volume_data_3d_info, indent + 4)
        print(f"{indent_str}CATEGORY: volume_data_time_and_channel_info")
        pretty_print_lattice_cif(
            lattice_cif.volume_data_time_and_channel_info, indent + 4
        )
        print(f"{indent_str}CATEGORY: segmentation_data_table")
        pretty_print_lattice_cif(lattice_cif.segmentation_data_table, indent + 4)
        print(f"{indent_str}CATEGORY: segmentation_data_3d")
        pretty_print_lattice_cif(lattice_cif.segmentation_data_3d, indent + 4)

    elif isinstance(lattice_cif, BaseModel):
        for field_name, value in lattice_cif.model_dump().items():
            if isinstance(value, list) or isinstance(value, np.ndarray):
                max_items = 10
                displayed = value[:max_items]
                more = "..." if len(value) > max_items else ""
                print(f"{indent_str}FIELD: {field_name} {displayed}{more} {len(value)}")
            else:
                print(f"{indent_str}FIELD: {field_name} {value}")

    else:
        print(f"{indent_str}{lattice_cif}")


def find_block(file: CIFFile, name: str) -> CIFDataBlock | None:
    for block in file.data_blocks:
        if block.header == name:
            return block


def find_category(block: CIFDataBlock, name: str) -> CIFCategory:
    for _, category in block.categories.items():
        if category.name == name:
            return category


def to_ndarray(category: CIFCategory, column_name: str) -> np.ndarray:
    return category[column_name].as_ndarray()


def to_item(category: CIFCategory, column_name: str) -> list[Any]:
    return category[column_name].as_ndarray().item()


def bcif_to_lattice_segmentation_cif(
    bcif_data: bytes,
    segmentation_id: str,
) -> LatticeSegmentationCIF:
    cif_file = loads(bcif_data, lazy=True)

    seg_block = find_block(cif_file, "SEGMENTATION_DATA")
    if seg_block is None:
        raise ValueError("SEGMENTATION_DATA block not found in CIF file")

    vol3d = find_category(seg_block, "volume_data_3d_info")
    time_ch = find_category(seg_block, "volume_data_time_and_channel_info")
    seg_table = find_category(seg_block, "segmentation_data_table")
    seg3d = find_category(seg_block, "segmentation_data_3d")

    volume_data_3d_info = VolumeData3DInfo(
        name=to_item(vol3d, "name"),
        axis_order_0=to_item(vol3d, "axis_order[0]"),
        axis_order_1=to_item(vol3d, "axis_order[1]"),
        axis_order_2=to_item(vol3d, "axis_order[2]"),
        origin_0=to_item(vol3d, "origin[0]"),
        origin_1=to_item(vol3d, "origin[1]"),
        origin_2=to_item(vol3d, "origin[2]"),
        dimensions_0=to_item(vol3d, "dimensions[0]"),
        dimensions_1=to_item(vol3d, "dimensions[1]"),
        dimensions_2=to_item(vol3d, "dimensions[2]"),
        sample_rate=to_item(vol3d, "sample_rate"),
        sample_count_0=to_item(vol3d, "sample_count[0]"),
        sample_count_1=to_item(vol3d, "sample_count[1]"),
        sample_count_2=to_item(vol3d, "sample_count[2]"),
        spacegroup_number=to_item(vol3d, "spacegroup_number"),
        spacegroup_cell_size_0=to_item(vol3d, "spacegroup_cell_size[0]"),
        spacegroup_cell_size_1=to_item(vol3d, "spacegroup_cell_size[1]"),
        spacegroup_cell_size_2=to_item(vol3d, "spacegroup_cell_size[2]"),
        spacegroup_cell_angles_0=to_item(vol3d, "spacegroup_cell_angles[0]"),
        spacegroup_cell_angles_1=to_item(vol3d, "spacegroup_cell_angles[1]"),
        spacegroup_cell_angles_2=to_item(vol3d, "spacegroup_cell_angles[2]"),
        mean_source=to_item(vol3d, "mean_source"),
        mean_sampled=to_item(vol3d, "mean_sampled"),
        sigma_source=to_item(vol3d, "sigma_source"),
        sigma_sampled=to_item(vol3d, "sigma_sampled"),
        min_source=to_item(vol3d, "min_source"),
        min_sampled=to_item(vol3d, "min_sampled"),
        max_source=to_item(vol3d, "max_source"),
        max_sampled=to_item(vol3d, "max_sampled"),
    )

    volume_data_time_and_channel_info = VolumeDataTimeAndChannelInfo(
        time_id=to_item(time_ch, "time_id"),
        channel_id=to_item(time_ch, "channel_id"),
    )

    segmentation_data_table = SegmentationDataTable(
        set_id=to_ndarray(seg_table, "set_id"),
        segment_id=to_ndarray(seg_table, "segment_id"),
    )

    segmentation_data_3d = SegmentationData3D(
        values=to_ndarray(seg3d, "values"),
    )

    segmentation_block = SegmentationBlock(
        volume_data_3d_info=volume_data_3d_info,
        volume_data_time_and_channel_info=volume_data_time_and_channel_info,
        segmentation_data_table=segmentation_data_table,
        segmentation_data_3d=segmentation_data_3d,
    )

    return LatticeSegmentationCIF(
        segmentation_block=segmentation_block,
        segmentation_id=segmentation_id,
    )


def get_lattice_segment(
    lattice_cif: LatticeSegmentationCIF,
    segment_id: int,
    name: str,
) -> LatticeSegmentationCIF | None:
    values = lattice_cif.segmentation_block.segmentation_data_3d.values
    info = lattice_cif.segmentation_block.volume_data_3d_info

    nx, ny, nz = (
        info.sample_count_0,
        info.sample_count_1,
        info.sample_count_2,
    )

    # 1️⃣ Reshape properly from flat list
    # CIF’s flat list stores values in z-major (slowest) order, but NumPy’s default reshape assumes x-major.
    data = np.array(values, dtype=np.float32).reshape((nz, ny, nx))
    data = np.transpose(data, (2, 1, 0))  # -> (x, y, z)

    # 2️⃣ Convert segment IDs to binary mask
    data_3d_values = np.where(data == segment_id, 1.0, 0.0)

    # 3️⃣ Pad with one voxel border (background = 0)
    padded = np.pad(
        data_3d_values, ((1, 1), (1, 1), (1, 1)), mode="constant", constant_values=0.0
    )

    # 4️⃣ Update metadata
    info.sample_count_0 = nx + 2
    info.sample_count_1 = ny + 2
    info.sample_count_2 = nz + 2
    info.origin_0 -= info.dimensions_0
    info.origin_1 -= info.dimensions_1
    info.origin_2 -= info.dimensions_2

    info.min_sampled = 0.0
    info.max_sampled = 1.0
    info.mean_sampled = float(np.mean(padded))
    info.sigma_sampled = float(np.std(padded))

    # 5️⃣ Flatten back into CIF order (reverse of reshape)
    padded_for_cif = np.transpose(padded, (2, 1, 0)).ravel().tolist()

    lattice_cif.segmentation_block.segmentation_data_3d.values = padded_for_cif
    lattice_cif.filename = name

    return lattice_cif


def lattice_model_to_bcif(lattice_model: LatticeSegmentationCIF) -> bytes:
    writer = create_binary_writer(encoder="VolumeServer")

    # this has to be here otherwise the volumeFromDensityServerData in molstar won't work
    # because it expects the data to be in the second block ¯\_(ツ)_/¯
    writer.start_data_block("SERVER")

    writer.start_data_block("VOLUME_DATA")
    writer.write_category(
        VolumeData3dInfoCategory,
        [lattice_model.segmentation_block.volume_data_3d_info],
    )
    values = lattice_model.segmentation_block.segmentation_data_3d.values
    writer.write_category(
        VolumeData3dCategory,
        [np.ravel(values, order="F")],
    )

    return writer.encode()
