from typing import Literal

from pydantic import BaseModel, field_validator

from lib.models.cvsx.cvsx_common import EntryId


class SamplingBox(BaseModel):
    grid_dimensions: tuple[int, int, int]
    origin: tuple[float, float, float]
    voxel_size: tuple[float, float, float]


class TimeTransformation(BaseModel):
    downsampling_level: int | Literal["all"]
    factor: float


class DownsamplingLevelInfo(BaseModel):
    level: int
    available: bool


class SamplingInfo(BaseModel):
    spatial_downsampling_levels: list[DownsamplingLevelInfo]
    boxes: dict[int, SamplingBox]
    time_transformations: list[TimeTransformation] | None = None
    source_axes_units: dict[str, str]
    original_axis_order: tuple[int, int, int]


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
    num_normals: int | None = None


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

    @field_validator("channel_ids", mode="before")
    @classmethod
    def convert_channel_ids_to_string(cls, v):
        return [str(x) for x in v]


class EntryMetadata(BaseModel):
    description: str | None = None
    url: str | None = None


class CVSXMetadata(BaseModel):
    entry_id: EntryId
    volumes: VolumesMetadata
    segmentation_lattices: SegmentationLatticesMetadata | None = None
    segmentation_meshes: MeshSegmentationSetsMetadata | None = None
    geometric_segmentation: GeometricSegmentationSetsMetadata | None = None
    entry_metadata: EntryMetadata | None = None
