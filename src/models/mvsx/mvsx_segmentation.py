from typing import Literal
from uuid import UUID, uuid4

import numpy as np
from pydantic import BaseModel, ConfigDict, Field

from src.models.cvsx.cvsx_annotations import DescriptionData
from src.models.read.geometric import ShapePrimitive

SegmentationType = Literal["mesh", "lattice", "primitive"]


class MVSXSegmentation(BaseModel):
    id: UUID = Field(default_factory=uuid4)

    type: SegmentationType

    source_filepath: str
    destination_filepath: str

    timeframe_id: int

    segmentation_id: str
    segment_id: int

    color: str | None = Field(default=None, pattern=r"^#[0-9a-fA-F]{6}$")
    opacity: float | None = Field(default=None, ge=0, le=1)

    descriptions: list[DescriptionData]

    def get_fields_str(self) -> str:
        lines = []
        lines.append("SEGMENTATION")
        lines.append(f"type                 : {self.type}")
        lines.append(f"source_filepath      : {self.source_filepath}")
        lines.append(f"destination_filepath : {self.destination_filepath}")
        lines.append(f"timeframe_id         : {self.timeframe_id}")
        lines.append(f"segmentation_id      : {self.segmentation_id}")
        lines.append(f"segment_id           : {self.segment_id}")

        # Descriptions
        lines.append("descriptions         :")
        if not self.descriptions:
            lines.append("  <empty>")
        else:
            for i, desc in enumerate(self.descriptions):
                lines.append(f"  Description {i + 1}:")
                lines.append(f"    id                : {desc.id}")
                lines.append(f"    target_kind       : {desc.target_kind}")
                lines.append(f"    target_id         : {desc.target_id}")
                lines.append(f"    name              : {desc.name}")
                lines.append(f"    external_references: {desc.external_references}")
                lines.append(f"    is_hidden         : {desc.is_hidden}")
                lines.append(f"    time              : {desc.time}")
                lines.append(f"    details           : {desc.details}")
                lines.append(f"    metadata          : {desc.metadata}")

        return "\n".join(lines)


class MVSXMeshSegmentation(MVSXSegmentation):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    vertices: np.ndarray[float]
    indices: np.ndarray[int]
    triangle_groups: np.ndarray[int]


class MVSXGeometricSegmentation(MVSXSegmentation):
    shape: ShapePrimitive
