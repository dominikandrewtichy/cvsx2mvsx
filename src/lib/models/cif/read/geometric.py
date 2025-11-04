from enum import Enum

from pydantic import BaseModel, Field


class ShapePrimitiveKind(str, Enum):
    sphere = "sphere"
    cylinder = "cylinder"
    box = "box"
    ellipsoid = "ellipsoid"
    pyramid = "pyramid"


class ShapePrimitiveBase(BaseModel):
    id: int
    kind: ShapePrimitiveKind


class RotationParameters(BaseModel):
    axis: tuple[float, float, float]
    radians: float


class Sphere(ShapePrimitiveBase):
    kind: ShapePrimitiveKind = Field(default=ShapePrimitiveKind.sphere, frozen=True)
    center: tuple[float, float, float]
    radius: float


class Box(ShapePrimitiveBase):
    kind: ShapePrimitiveKind = Field(default=ShapePrimitiveKind.box, frozen=True)
    translation: tuple[float, float, float]
    scaling: tuple[float, float, float]
    rotation: RotationParameters


class Cylinder(ShapePrimitiveBase):
    kind: ShapePrimitiveKind = Field(default=ShapePrimitiveKind.cylinder, frozen=True)
    start: tuple[float, float, float]
    end: tuple[float, float, float]
    radius_bottom: float
    radius_top: float


class Ellipsoid(ShapePrimitiveBase):
    kind: ShapePrimitiveKind = Field(default=ShapePrimitiveKind.ellipsoid, frozen=True)
    dir_major: tuple[float, float, float]
    dir_minor: tuple[float, float, float]
    center: tuple[float, float, float]
    radius_scale: tuple[float, float, float]


class Pyramid(ShapePrimitiveBase):
    kind: ShapePrimitiveKind = Field(default=ShapePrimitiveKind.pyramid, frozen=True)
    translation: tuple[float, float, float]
    scaling: tuple[float, float, float]
    rotation: RotationParameters


class ShapePrimitiveData(BaseModel):
    shape_primitive_list: list[ShapePrimitiveBase]


class GeometricSegmentationData(BaseModel):
    segmentation_id: str
    primitives: dict[int, ShapePrimitiveData]
