import numpy as np
from pydantic import BaseModel, ConfigDict

from lib.models.cif.common import VolumeData3DInfo, VolumeDataTimeAndChannelInfo


class VolumeData3D(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    values: np.ndarray[float]


class VolumeBlock(BaseModel):
    volume_data_3d_info: VolumeData3DInfo
    volume_data_time_and_channel_info: VolumeDataTimeAndChannelInfo
    volume_data_3d: VolumeData3D


class VolumeCIF(BaseModel):
    filename: str | None = None
    volume_block: VolumeBlock
