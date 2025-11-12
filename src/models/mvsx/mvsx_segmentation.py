from typing import Literal

import numpy as np
from pydantic import BaseModel, ConfigDict, Field

from src.models.cvsx.cvsx_annotations import DescriptionData
from src.models.read.geometric import Vector3

SegmentationType = Literal["mesh", "lattice", "primitive"]


class MVSXSegmentation(BaseModel):
    type: SegmentationType

    source_filepath: str
    destination_filepath: str

    timeframe_id: int

    segmentation_id: str
    segment_id: int

    color: str | None = Field(default=None, pattern=r"^#[0-9a-fA-F]{6}$")
    opacity: float | None = Field(default=None, ge=0, le=1)

    descriptions: list[DescriptionData]

    def print_fields(self):
        print("SEGMENTATION")

        print("type                 :", self.type)
        print("source_filepath      :", self.source_filepath)
        print("destination_filepath :", self.destination_filepath)
        print("timeframe_id         :", self.timeframe_id)
        print("segmentation_id      :", self.segmentation_id)
        print("segment_id           :", self.segment_id)

        # Print descriptions
        print("descriptions         :")
        if not self.descriptions:
            print("  <empty>")
        else:
            for i, desc in enumerate(self.descriptions):
                print(f"  Description {i + 1}:")
                print(f"    id                : {desc.id}")
                print(f"    target_kind       : {desc.target_kind}")
                print(f"    target_id         : {desc.target_id}")
                print(f"    name              : {desc.name}")
                print(f"    external_references: {desc.external_references}")
                print(f"    is_hidden         : {desc.is_hidden}")
                print(f"    time              : {desc.time}")
                print(f"    details           : {desc.details}")
                print(f"    metadata          : {desc.metadata}")


class MVSXMeshSegmentation(MVSXSegmentation):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    vertices: np.ndarray[float]
    indices: np.ndarray[int]
    triangle_groups: np.ndarray[int]


class MVSXSphereSegmentation(MVSXSegmentation):
    kind: Literal["sphere"] = "sphere"
    center: Vector3
    radius: float


MVSXGeometricSegmentation = MVSXSphereSegmentation
