from typing import Literal

from pydantic import BaseModel, Field

from src.models.mvsx.mvsx_volume import MVSXVolume


class MVSXLatticeSegmentation(BaseModel):
    source_filepath: str
    destination_filepath: str
    format: Literal["bcif"]
    segmentation_id: str
    segment_id: int
    isovalue: float = 1.0
    color: str | None = Field(default="#ffffff", pattern=r"^#[0-9a-fA-F]{6}$")
    opacity: float = Field(default=1, ge=0, le=1)


class MVSXMeshSegmentation(BaseModel):
    pass


class MVSXGeometricSegmentation(BaseModel):
    pass


class MVSXTimeframeSegmentations(BaseModel):
    mesh: list[MVSXMeshSegmentation] = []
    lattice: list[MVSXLatticeSegmentation] = []
    geometric: list[MVSXGeometricSegmentation] = []


class MVSXSnapshot(BaseModel):
    title: str | None = None
    description: str | None = None
    volumes: list[MVSXVolume] = []
    segmentations: MVSXTimeframeSegmentations = MVSXTimeframeSegmentations()


class MVSXEntry(BaseModel):
    snapshots: list[MVSXSnapshot]
