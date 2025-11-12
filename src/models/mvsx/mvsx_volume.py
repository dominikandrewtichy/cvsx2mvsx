from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class MVSXVolume(BaseModel):
    id: UUID = Field(default_factory=uuid4)

    source_filepath: str
    destination_filepath: str

    timeframe_id: int

    channel_id: str

    # TODO: how to set from metadata???
    isovalue: float = 1

    label: str | None = None
    color: str | None = Field(default=None, pattern=r"^#[0-9a-fA-F]{6}$")
    opacity: float | None = Field(default=None, ge=0, le=1)

    @field_validator("color", mode="before")
    @classmethod
    def default_color(cls, value):
        return value or "#000000"

    @field_validator("opacity", mode="before")
    @classmethod
    def default_opacity(cls, value):
        return value or 0.2

    def get_fields_str(self) -> str:
        lines = []
        lines.append("VOLUME")
        lines.append(f"source_filepath      : {self.source_filepath}")
        lines.append(f"destination_filepath : {self.destination_filepath}")
        lines.append(f"timeframe_id         : {self.timeframe_id}")
        lines.append(f"channel_id           : {self.channel_id}")
        lines.append(f"isovalue             : {self.isovalue}")
        lines.append(f"label                : {self.label}")
        lines.append(f"color                : {self.color}")
        lines.append(f"opacity              : {self.opacity}")
        return "\n".join(lines)
