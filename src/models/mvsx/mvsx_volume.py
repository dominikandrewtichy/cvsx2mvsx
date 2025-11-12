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

    def print_fields(self):
        print("VOLUME")

        print("source_filepath      :", self.source_filepath)
        print("destination_filepath :", self.destination_filepath)
        print("timeframe_id         :", self.timeframe_id)
        print("channel_id           :", self.channel_id)
        print("isovalue             :", self.isovalue)
        print("label                :", self.label)
        print("color                :", self.color)
        print("opacity              :", self.opacity)
