from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class MVSXVolume(BaseModel):
    id: UUID = Field(default_factory=uuid4)

    source_filepath: str
    destination_filepath: str

    timeframe_id: int

    channel_id: str

    isovalue: float

    label: str | None
    color: str = Field(default="#ffffff", pattern=r"^#[0-9a-fA-F]{6}$")
    opacity: float = Field(default=1, ge=0, le=1)

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
