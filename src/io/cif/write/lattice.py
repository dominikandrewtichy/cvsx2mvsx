from ciftools.serialization import create_binary_writer
from src.models.cif.read.lattice import LatticeCif
from src.models.cif.write.volume.volume_data_3d import VolumeData3dCategory
from src.models.cif.write.volume.volume_data_3d_info import VolumeData3dInfoCategory
from src.models.cif.write.volume.volume_data_time_and_channel_info import (
    VolumeDataTimeAndChannelInfoCategory,
)


def lattice_to_bcif(lattice_model: LatticeCif) -> bytes:
    writer = create_binary_writer(encoder="VolumeServer")

    # this empty data block is required by mol* despite not being used
    writer.start_data_block("SERVER")
    writer.start_data_block("VOLUME_DATA")

    writer.write_category(
        VolumeData3dInfoCategory,
        [
            lattice_model.segmentation_block.volume_data_3d_info,
        ],
    )
    writer.write_category(
        VolumeDataTimeAndChannelInfoCategory,
        [
            lattice_model.segmentation_block.volume_data_time_and_channel_info,
        ],
    )
    writer.write_category(
        VolumeData3dCategory,
        [
            lattice_model.segmentation_block.segmentation_data_3d.values,
        ],
    )

    return writer.encode()
