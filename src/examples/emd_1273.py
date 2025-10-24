import json

from molviewspec import create_builder
from molviewspec.builder import Root

from src.utils.utils import rgba_to_hex


def emd_1273_volume(builder: Root):
    volume_cif = builder.download(url="./volume_0_0.bcif").parse(format="bcif")
    volume_data = volume_cif.volume()
    volume_representation = volume_data.representation(
        type="isosurface",
        relative_isovalue=2.73,
        show_faces=True,
        show_wireframe=False,
    )
    volume_representation.color(color="white").opacity(opacity=0.4)

    return builder


def emd_1273_lattices(builder: Root):
    with open("static/cvsx/unzipped/emd-1273/annotations.json") as f:
        json_string = f.read()
        annotations = json.loads(json_string)
    for segment_annotation in annotations["segment_annotations"]:
        rgba_color = segment_annotation["color"]
        color = rgba_to_hex(*rgba_color)
        segment_id = segment_annotation["segment_id"]
        segment_kind = segment_annotation["segment_kind"]
        segmentation_id = segment_annotation["segmentation_id"]
        time = segment_annotation["time"]
        volume_cif = builder.download(
            url=f"./{segmentation_id}_{segment_id}.cif"
        ).parse(format="mmcif")
        volume_data = volume_cif.volume()
        volume_representation = volume_data.representation(
            type="isosurface",
            relative_isovalue=2.73,
            show_wireframe=False,
            show_faces=True,
        )
        color = rgba_to_hex(*segment_id["color"])
        volume_representation.color(color=color).opacity(opacity=1)

    return builder


def emd_1273() -> Root:
    builder: Root = create_builder()

    emd_1273_volume(builder)
    emd_1273_lattices(builder)

    print(builder.get_state())

    return builder
