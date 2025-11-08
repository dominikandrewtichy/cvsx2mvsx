import json

from molviewspec import GlobalMetadata, States, create_builder

from src.convert.convert_all import rgba_to_hex_color
from src.examples.empiar_10070 import add_mesh_from_bcif


def main():
    with open("data/cvsx/unzipped/empiar-10070/annotations.json") as f:
        json_string = f.read()
        annotations = json.loads(json_string)

    builder = create_builder()

    def add_primitives_from_uri(builder, segment_annotation):
        rgba_color = segment_annotation["color"]
        color = rgba_to_hex_color(rgba_color)
        segment_id = segment_annotation["segment_id"]
        segment_kind = segment_annotation["segment_kind"]
        segmentation_id = segment_annotation["segmentation_id"]
        time = segment_annotation["time"]
        filename = f"{segment_kind}_{segment_id}_{segmentation_id}_{time}"
        opacity = 1
        uri = f"data/cvsx/unzipped/empiar-10070/{filename}.bcif"

        add_mesh_from_bcif(uri, filename, color, opacity)

        builder.primitives_from_uri(
            uri=f"http://127.0.0.1:8000/data/mvsx/unzipped/empiar-10070/{filename}.mvsj"
        )
        return builder

    for segment_annotation in annotations["segment_annotations"]:

    segment_snapshots = []

    for segment_annotation in annotations["segment_annotations"]:
        segment_id = segment_annotation["segment_id"]
        segment_kind = segment_annotation["segment_kind"]
        segmentation_id = segment_annotation["segmentation_id"]
        time = segment_annotation["time"]
        filename = f"{segment_kind}_{segment_id}_{segmentation_id}_{time}"
        builder_copy = builder.model_copy()
        builder_copy.animation(
            include_camera=True,
        ).interpolate(
            kind="scalar",
            target_ref=f"{filename}",
            property="opacity",
            start=0.5,
            end=0.5,
            duration_ms=500,
        )
        segment_snapshot = builder_copy.get_snapshot(
            key=f"{filename}",
            title=f"{filename}",
            description=f"# {filename}\n\n[index](#index)",
            transition_duration_ms=500,
            linger_duration_ms=0,
        )
        segment_snapshots.append(segment_snapshot)

    states = States(
        metadata=GlobalMetadata(),
        snapshots=[index_snapshot, *segment_snapshots],
    )

    with open("data/mvsx/unzipped/empiar-10070/index.mvsj", "w") as f:
        f.write(
            states.model_dump_json(indent=2, exclude_none=True),
        )


if __name__ == "__main__":
    main()
