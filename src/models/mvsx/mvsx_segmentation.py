from typing import Literal
from uuid import UUID, uuid4

import numpy as np
from pydantic import BaseModel, ConfigDict, Field

from src.models.cvsx.cvsx_annotations import DescriptionData
from src.models.read.geometric import ShapePrimitive

SegmentationType = Literal["mesh", "lattice", "primitive"]


class MVSXBaseSegmentation(BaseModel):
    id: UUID = Field(default_factory=uuid4)

    source_filepath: str
    destination_filepath: str

    timeframe_id: int

    segmentation_id: str
    segment_id: int

    color: str | None = Field(default=None, pattern=r"^#[0-9a-fA-F]{6}$")
    opacity: float | None = Field(default=None, ge=0, le=1)

    descriptions: list[DescriptionData]


class MVSXLatticeSegmentation(MVSXBaseSegmentation):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    kind: Literal["lattice"] = "lattice"

    vertices: np.ndarray[float]
    indices: np.ndarray[int]
    triangle_groups: np.ndarray[int]


class MVSXMeshSegmentation(MVSXBaseSegmentation):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    kind: Literal["mesh"] = "mesh"

    vertices: np.ndarray[float]
    indices: np.ndarray[int]
    triangle_groups: np.ndarray[int]


class MVSXGeometricSegmentation(MVSXBaseSegmentation):
    kind: Literal["primitive"] = "primitive"

    shape: ShapePrimitive


MVSXSegmentation = MVSXMeshSegmentation | MVSXGeometricSegmentation
