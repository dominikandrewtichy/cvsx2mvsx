import numpy as np
from pydantic import BaseModel, ConfigDict, Field

from src.models.cvsx.cvsx_annotations import DescriptionData


class MVSXSegmentation(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    source_filepath: str
    destination_filepath: str

    timeframe_id: int
    segmentation_id: str
    segment_id: int

    vertices: np.ndarray[float]
    indices: np.ndarray[int]
    triangle_groups: np.ndarray[int]

    color: str = Field(default="#ffffff", pattern=r"^#[0-9a-fA-F]{6}$")
    opacity: float = Field(default=1, ge=0, le=1)
    descriptions: list[DescriptionData]
