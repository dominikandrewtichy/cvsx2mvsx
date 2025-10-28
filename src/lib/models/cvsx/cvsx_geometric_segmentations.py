from enum import Enum

from pydantic import BaseModel


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
    center: tuple[float, float, float]
    radius: float


class Box(ShapePrimitiveBase):
    translation: tuple[float, float, float]
    scaling: tuple[float, float, float]
    rotation: RotationParameters


class Cylinder(ShapePrimitiveBase):
    start: tuple[float, float, float]
    end: tuple[float, float, float]
    radius_bottom: float
    radius_top: float


class Ellipsoid(ShapePrimitiveBase):
    dir_major: tuple[float, float, float]
    dir_minor: tuple[float, float, float]
    center: tuple[float, float, float]
    radius_scale: tuple[float, float, float]


class Pyramid(ShapePrimitiveBase):
    translation: tuple[float, float, float]
    scaling: tuple[float, float, float]
    rotation: RotationParameters


class ShapePrimitiveData(BaseModel):
    shape_primitive_list: list[ShapePrimitiveBase]


class GeometricSegmentationData(BaseModel):
    segmentation_id: str
    primitives: dict[int, ShapePrimitiveData]
