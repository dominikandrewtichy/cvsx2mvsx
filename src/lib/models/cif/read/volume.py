import numpy as np
from pydantic import BaseModel, ConfigDict

from lib.models.cif.read.common import (
    CifFile,
    VolumeData3dInfo,
    VolumeDataTimeAndChannelInfo,
)


class VolumeData3d(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    values: np.ndarray[float]


class VolumeBlock(BaseModel):
    volume_data_3d_info: VolumeData3dInfo
    volume_data_time_and_channel_info: VolumeDataTimeAndChannelInfo
    volume_data_3d: VolumeData3d


class VolumeCif(CifFile):
    volume_block: VolumeBlock
