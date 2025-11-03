"""Configuration models for MVSX generation."""

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class SegmentAnnotation(BaseModel):
    """Segment annotation with color mapping."""

    segment_id: int
    segmentation_id: str
    color: list[float] = Field(description="RGBA color values (0-1 range)")
    segment_kind: str = "lattice"
    id: str | None = None
    time: int = 0


class MeshGenerationConfig(BaseModel):
    """Configuration for mesh generation from voxel data."""

    marching_cubes_level: float = 0.5
    marching_cubes_method: str = "lewiner"
    smooth_iterations: int = 1
    origin_offset: float = 0.5


class VolumeConfig(BaseModel):
    """Configuration for volume visualization."""

    url: str | None = None
    channel_id: str = "0"
    relative_isovalue: float = 1.0
    color: str = "white"
    opacity: float = 0.5
    show_faces: bool = True
    show_wireframe: bool = False


class SegmentationConfig(BaseModel):
    """Configuration for a single segmentation."""

    segmentation_id: str
    inner_path: str | None = None
    """Path within the CVSX zip file. If None, will be constructed as 'lattice_{segmentation_id}_0.bcif'"""


class MVSXGeneratorConfig(BaseModel):
    """Complete configuration for MVSX generation."""

    # Input/Output paths
    cvsx_input_path: Path
    mvsx_output_path: Path
    mvsj_output_path: Path | None = None
    """If provided, will save intermediate MVSJ file"""

    # Volume configuration
    volume: VolumeConfig | None = None
    """If None, no volume will be included"""

    # Segmentation configuration
    segmentations: list[SegmentationConfig] = Field(default_factory=list)
    """List of segmentations to process. If empty, will auto-discover from CVSX"""

    # Segment annotations (color mappings)
    segment_annotations: list[SegmentAnnotation] = Field(default_factory=list)
    """Color mappings for segments. Can be loaded from external JSON/YAML"""

    # Mesh generation parameters
    mesh_config: MeshGenerationConfig = Field(default_factory=MeshGenerationConfig)

    # Temporary directory
    temp_dir: Path = Path("temp")

    def get_segment_color(self, segmentation_id: str, segment_id: int) -> str | None:
        """Get hex color for a segment."""
        for annotation in self.segment_annotations:
            if (
                annotation.segmentation_id == segmentation_id
                and annotation.segment_id == segment_id
            ):
                return self._rgb_to_hex(annotation.color[:3])
        return None

    @staticmethod
    def _rgb_to_hex(rgb: list[float]) -> str:
        """Convert RGB values (0-1) to hex color string."""
        r, g, b = rgb
        return "#{:02X}{:02X}{:02X}".format(int(r * 255), int(g * 255), int(b * 255))

    @classmethod
    def from_json_file(cls, filepath: Path) -> "MVSXGeneratorConfig":
        """Load configuration from JSON file."""
        import json

        with open(filepath) as f:
            data = json.load(f)
        return cls(**data)

    @classmethod
    def from_yaml_file(cls, filepath: Path) -> "MVSXGeneratorConfig":
        """Load configuration from YAML file."""
        import yaml

        with open(filepath) as f:
            data = yaml.safe_load(f)
        return cls(**data)

    def to_json_file(self, filepath: Path) -> None:
        """Save configuration to JSON file."""
        import json

        with open(filepath, "w") as f:
            json.dump(self.model_dump(mode="json"), f, indent=2)

    def to_yaml_file(self, filepath: Path) -> None:
        """Save configuration to YAML file."""
        import yaml

        with open(filepath, "w") as f:
            yaml.dump(self.model_dump(mode="json"), f, default_flow_style=False)
