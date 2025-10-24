import json

from molviewspec import create_builder
from molviewspec.builder import Root

from src.utils.utils import rgba_to_hex


def empiar_11756_ribosomes_volume(builder: Root):
    volume_cif = builder.download(url="./volume_0_0.bcif").parse(format="bcif")
    volume_data = volume_cif.volume()
    volume_representation = volume_data.representation(
        type="isosurface",
        relative_isovalue=1,
        show_faces=True,
        show_wireframe=False,
    )
    volume_representation.color(color="white").opacity(opacity=0.2)

    return builder


def empiar_11756_ribosomes_spheres(builder: Root):
    with open(
        "static/cvsx/unzipped/empiar_11756_ribosomes/geometric-segmentation_ribosomes_0.json"
    ) as f:
        json_string = f.read()
        segmentation = json.loads(json_string)
    with open("static/cvsx/unzipped/empiar_11756_ribosomes/annotations.json") as f:
        json_string = f.read()
        annotations = json.loads(json_string)
    spheres = segmentation["shape_primitive_list"]
    segment_annotations = annotations["segment_annotations"]
    primitives = builder.primitives()
    for sphere in spheres:
        center = sphere["center"]
        radius = sphere["radius"]
        annotation = segment_annotations[sphere["id"]]
        color = rgba_to_hex(*annotation["color"])
        primitive = primitives.ellipsoid(
            center=center,
            radius=radius,
            color=color,
        )

    return builder


def empiar_11756_ribosomes() -> Root:
    builder: Root = create_builder()

    empiar_11756_ribosomes_volume(builder)
    empiar_11756_ribosomes_spheres(builder)

    return builder
