from typing import Literal

from pydantic import BaseModel
from src.utils.volseg_models import EntryId


class SamplingBox(BaseModel):
    origin: tuple[int, int, int]
    voxel_size: tuple[float, float, float]
    grid_dimensions: list[int, int, int]


class TimeTransformation(BaseModel):
    downsampling_level: int | Literal["all"]
    factor: float


class DownsamplingLevelInfo(BaseModel):
    level: int
    available: bool


class SamplingInfo(BaseModel):
    spatial_downsampling_levels: list[DownsamplingLevelInfo]
    boxes: dict[int, SamplingBox]
    time_transformations: list[TimeTransformation] | None
    source_axes_units: dict[str, str]
    original_axis_order: list[int, int, int]


class TimeInfo(BaseModel):
    kind: str
    start: int
    end: int
    units: str


class SegmentationLatticesMetadata(BaseModel):
    segmentation_ids: list[str]
    segmentation_sampling_info: dict[str, SamplingInfo]
    time_info: dict[str, TimeInfo]


class GeometricSegmentationSetsMetadata(BaseModel):
    segmentation_ids: list[str]
    time_info: dict[str, TimeInfo]


class MeshMetadata(BaseModel):
    num_vertices: int
    num_triangles: int
    num_normals: int | None


class MeshListMetadata(BaseModel):
    mesh_ids: dict[int, MeshMetadata]


class DetailLvlsMetadata(BaseModel):
    detail_lvls: dict[int, MeshListMetadata]


class MeshComponentNumbers(BaseModel):
    segment_ids: dict[int, DetailLvlsMetadata]


class MeshesMetadata(BaseModel):
    mesh_timeframes: dict[int, MeshComponentNumbers]
    detail_lvl_to_fraction: dict


class MeshSegmentationSetsMetadata(BaseModel):
    segmentation_ids: list[str]
    segmentation_metadata: dict[str, MeshesMetadata]
    time_info: dict[str, TimeInfo]


class VolumeDescriptiveStatistics(BaseModel):
    mean: float
    min: float
    max: float
    std: float


class VolumeSamplingInfo(SamplingInfo):
    descriptive_statistics: dict[int, dict[int, dict[str, VolumeDescriptiveStatistics]]]


class VolumesMetadata(BaseModel):
    channel_ids: list[str]
    time_info: TimeInfo
    volume_sampling_info: VolumeSamplingInfo


class EntryMetadata(BaseModel):
    description: str | None
    url: str | None


class CVSXMetadata(BaseModel):
    entry_id: EntryId
    volumes: VolumesMetadata
    segmentation_lattices: SegmentationLatticesMetadata | None
    segmentation_meshes: MeshSegmentationSetsMetadata | None
    geometric_segmentation: GeometricSegmentationSetsMetadata | None
    entry_metadata: EntryMetadata | None
