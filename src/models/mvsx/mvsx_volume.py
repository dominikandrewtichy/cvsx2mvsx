from pydantic import BaseModel, Field


class MVSXVolume(BaseModel):
    source_filepath: str
    destination_filepath: str

    timeframe_id: int
    channel_id: str

    isovalue: float

    label: str | None
    color: str = Field(default="#ffffff", pattern=r"^#[0-9a-fA-F]{6}$")
    opacity: float = Field(default=1, ge=0, le=1)
