from typing import Literal

from pydantic import BaseModel


class CVSXQuery(BaseModel):
    segmentation_kind: Literal["mesh", "lattice", "geometric-segmentation"] | None
    entry_id: str
    source_db: str
    time: int | None
    channel_id: str | None
    segmentation_id: str | None
    detail_lvl: int | None
    max_points: int | None
