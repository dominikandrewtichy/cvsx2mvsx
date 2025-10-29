import numpy as np
from pydantic import BaseModel, ConfigDict

from lib.models.cif.volume import VolumeData3DInfo, VolumeDataTimeAndChannelInfo


class SegmentationDataTable(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    set_id: np.ndarray[int]
    segment_id: np.ndarray[int]


class SegmentationData3D(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    values: np.ndarray[float]


class SegmentationBlock(BaseModel):
    volume_data_3d_info: VolumeData3DInfo
    volume_data_time_and_channel_info: VolumeDataTimeAndChannelInfo
    segmentation_data_table: SegmentationDataTable
    segmentation_data_3d: SegmentationData3D


class LatticeSegmentationCIF(BaseModel):
    filename: str | None = None
    segmentation_id: str
    segmentation_block: SegmentationBlock
