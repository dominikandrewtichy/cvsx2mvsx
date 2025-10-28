from pydantic import BaseModel

from lib.models.cvsx.cvsx_entry import CVSXEntry


class InterFileInfo(BaseModel):
    filepath: str
    timeframe_index: int


class InterVolumeFileInfo(InterFileInfo):
    channel_id: str


class InterSegmentationFileInfo(InterFileInfo):
    segmentation_id: str


class InterSegmentations(BaseModel):
    mesh: list[InterSegmentationFileInfo] = []
    lattice: list[InterSegmentationFileInfo] = []
    geometric: list[InterSegmentationFileInfo] = []


class InterTimeframeInfo(BaseModel):
    timeframe_index: int
    volumes: list[InterVolumeFileInfo] = []
    segmentations: InterSegmentations = InterSegmentations()


class InterEntryInfo(BaseModel):
    cvsx_entry: CVSXEntry
    timeframes: list[InterTimeframeInfo]
