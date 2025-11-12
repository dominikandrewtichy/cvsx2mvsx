from pydantic import BaseModel

from src.models.cvsx.cvsx_annotations import DescriptionData
from src.models.mvsx.mvsx_segmentation import MVSXSegmentation
from src.models.mvsx.mvsx_volume import MVSXVolume


class MVSXSnapshot(BaseModel):
    key: str
    title: str | None = None
    description: str | None = None


class MVSXIndexSnapshot(MVSXSnapshot):
    timeframe_keys: list[str]


class MVSXTimeframeSnapshot(MVSXSnapshot):
    volumes: list[MVSXVolume]
    segmentations: list[MVSXSegmentation]


class MVSXFile(BaseModel):
    name: str | None
    details: str | None
    descriptions: list[DescriptionData]
    snapshots: list[MVSXTimeframeSnapshot]
