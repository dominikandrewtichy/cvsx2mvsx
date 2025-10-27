from pydantic import BaseModel

from src.models.mvsx.mvsx_volume import MVSXVolume


class MVSXLatticeSegmentation(BaseModel):
    pass


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
