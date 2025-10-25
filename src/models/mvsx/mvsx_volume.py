from typing import Literal

from pydantic import BaseModel, Field


class MVSXColor(BaseModel):
    hex: str = Field(pattern=r"^#[0-9a-fA-F]{6}$")


class MVSXVolume(BaseModel):
    source_filepath: str
    destination_filepath: str
    format: Literal["bcif"]
    channel_id: str
    timeframe_index: int
    color: MVSXColor | None = Field(default="#ffffff")
    opacity: float = Field(default=1, ge=0, le=1)


class MVSXVolumeFilter(BaseModel):
    channel_id: str | None
    timeframe_index: int | None
