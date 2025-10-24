from molviewspec import create_builder
from pydantic import BaseModel, Field

from src.utils.utils import rgba_to_hex


def custom_tubhiswt():
    builder = create_builder()

    volume0_cif = builder.download(
        url="http://localhost:8000/backend/static/cvsx/unpacked/custom-tubhiswt/volume_0_0.bcif"
    ).parse(format="bcif")
    volume1_cif = builder.download(
        url="http://localhost:8000/backend/static/cvsx/unpacked/custom-tubhiswt/volume_1_0.bcif"
    ).parse(format="bcif")
    volume0_data = volume0_cif.volume(channel_id="0")
    volume1_data = volume1_cif.volume(channel_id="1")
    volume0_representation = volume0_data.representation(
        type="isosurface",
        relative_isovalue=1,
        show_wireframe=False,
        show_faces=True,
    )
    volume1_representation = volume1_data.representation(
        type="isosurface",
        relative_isovalue=1,
        show_wireframe=False,
        show_faces=True,
    )
    volume0_rgba = [
        0.12156862745098039,
        0.4666666666666667,
        0.7058823529411765,
        1.0,
    ]
    volume1_rgba = [
        1.0,
        0.4980392156862745,
        0.054901960784313725,
        1.0,
    ]
    volume0_color = rgba_to_hex(*volume0_rgba)
    volume1_color = rgba_to_hex(*volume1_rgba)
    volume0_representation.color(color=volume0_color).opacity(opacity=0.2)
    volume1_representation.color(color=volume1_color).opacity(opacity=0.2)

    return builder


class RGBColor(BaseModel):
    r: float = Field(ge=0, le=1)
    g: float = Field(ge=0, le=1)
    b: float = Field(ge=0, le=1)
    a: float = Field(ge=0, le=1)
