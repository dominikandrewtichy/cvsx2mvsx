from typing import Literal

from pydantic import BaseModel, Field


class MVSXVolume(BaseModel):
    source_filepath: str
    destination_filepath: str
    format: Literal["bcif"]
    channel_id: str
    isovalue: float = 1
    color: str | None = Field(default="#ffffff", pattern=r"^#[0-9a-fA-F]{6}$")
    opacity: float = Field(default=1, ge=0, le=1)


class MVSXMeshSegmentation(BaseModel):
    source_filepath: str
    destination_filepath: str
    format: Literal["bcif"]
    segmentation_id: str
    segment_id: int
    isovalue: float = 1.0
    color: str | None = Field(default="#ffffff", pattern=r"^#[0-9a-fA-F]{6}$")
    opacity: float = Field(default=1, ge=0, le=1)
    annotations: str | None = None


class MVSXLatticeSegmentation(BaseModel):
    source_filepath: str
    destination_filepath: str
    format: Literal["bcif"]
    segmentation_id: str
    segment_id: int
    isovalue: float = 1.0
    color: str | None = Field(default="#ffffff", pattern=r"^#[0-9a-fA-F]{6}$")
    opacity: float = Field(default=1, ge=0, le=1)
    annotations: str | None = None


class MVSXGeometricSegmentation(BaseModel):
    source_filepath: str
    destination_filepath: str
    format: Literal["bcif"]
    segmentation_id: str
    segment_id: int
    isovalue: float = 1.0
    color: str | None = Field(default="#ffffff", pattern=r"^#[0-9a-fA-F]{6}$")
    opacity: float = Field(default=1, ge=0, le=1)
    annotations: str | None = None


class MVSXTimeframeSegmentations(BaseModel):
    mesh: list[MVSXMeshSegmentation] = []
    lattice: list[MVSXLatticeSegmentation] = []
    geometric: list[MVSXGeometricSegmentation] = []


class MVSXSnapshot(BaseModel):
    key: str
    title: str | None = None


class MVSXIndexSnapshot(MVSXSnapshot):
    timeframe_keys: list[str] = []


class MVSXTimeframeSnapshot(MVSXSnapshot):
    volumes: list[MVSXVolume] = []
    segmentations: MVSXTimeframeSegmentations = MVSXTimeframeSegmentations()


class MVSXEntry(BaseModel):
    index: MVSXIndexSnapshot
    timeframes: list[MVSXTimeframeSnapshot]
