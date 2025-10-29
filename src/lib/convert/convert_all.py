import os
from pathlib import Path
from zipfile import ZipFile

from molviewspec import create_builder
from molviewspec.builder import GlobalMetadata, Root, Snapshot, States

from lib.models.cvsx.cvsx_annotations import CVSXAnnotations
from lib.models.intermediary.inter import InterEntryInfo


def rgb_to_hex(r: float, g: float, b: float) -> str:
    return "#{:02X}{:02X}{:02X}".format(int(r * 255), int(g * 255), int(b * 255))


def get_timeframe_key(index: str) -> str:
    return f"timeframe_{index}"


def get_index_key() -> str:
    return "index"


def get_volume_color(annotations: CVSXAnnotations, channel_id: str) -> str | None:
    if not annotations.volume_channels_annotations:
        return None
    for annotation in annotations.volume_channels_annotations:
        if annotation.channel_id == channel_id:
            r, g, b = annotation.color[:3]
            return rgb_to_hex(r, g, b)


def get_volume_opacity(annotations: CVSXAnnotations, channel_id: str) -> float | None:
    if not annotations.volume_channels_annotations:
        return None
    for annotation in annotations.volume_channels_annotations:
        if annotation.channel_id == channel_id:
            return annotation.color[3]


def convert_all(entry: InterEntryInfo) -> None:
    snapshots: list[Snapshot] = []

    # prepare the zip archive
    # zip_filepath = Path(entry.cvsx_entry.filepath).stem + ".mvsx"
    zip_filepath = "test.mvsx"
    ZipFile(zip_filepath, "w").close()

    # index snapshot
    snapshot_builder: Root = create_builder()

    key = get_index_key()
    title = "index"
    if entry.cvsx_entry.annotations.name:
        header = entry.cvsx_entry.annotations.name
    else:
        header = Path(entry.cvsx_entry.filepath).stem
    description = f"# {header} \n\n\n"
    for timeframe in entry.timeframes:
        index = timeframe.timeframe_index
        text = f"Timeframe {index}"
        ref_key = get_timeframe_key(index)
        description += f"[{text}](#{ref_key})\n\n"

    index_snapshot = snapshot_builder.get_snapshot(
        key=key,
        title=title,
        description=description,
        transition_duration_ms=2000,
    )
    snapshots.append(index_snapshot)

    # timeframes
    for timeframe in entry.timeframes:
        snapshot_builder: Root = create_builder()

        # volumes
        for volume in timeframe.volumes:
            # copy files
            dest_name = os.path.basename(volume.filepath)
            destination_filename = f"volumes/{dest_name}"
            with ZipFile(entry.cvsx_entry.filepath, "r") as source_zip:
                with ZipFile(zip_filepath, "a") as f:
                    data = source_zip.read(volume.filepath)
                    f.writestr(destination_filename, data)

            # build
            download = snapshot_builder.download(url=destination_filename)
            parsed = download.parse(format="bcif")
            volume_data = parsed.volume(channel_id=volume.channel_id)
            representation = volume_data.representation(
                type="isosurface",
                relative_isovalue=1,
            )
            color = get_volume_color(entry.cvsx_entry.annotations, volume.channel_id)
            opacity = get_volume_opacity(
                entry.cvsx_entry.annotations, volume.channel_id
            )
            representation.color(color=color)
            opacity_node_ref = ""
            representation.opacity(ref=opacity_node_ref, opacity=opacity)

            # snapshot_builder.animation().interpolate(
            #     kind="scalar",
            #     target_ref=opacity_node_ref,
            #     property="opacity",
            #     start_ms=0,
            #     duration_ms=1000,
            #     start=0.5,
            #     end=1.0,
            #     easing="linear",
            # )

        snapshot = snapshot_builder.get_snapshot(
            key=get_timeframe_key(timeframe.timeframe_index),
            title=f"Timeframe: {timeframe.timeframe_index}",
            description=f"[Index](#{get_index_key()})",
            # transition_duration_ms=2000,
        )
        snapshots.append(snapshot)

    metadata = GlobalMetadata()
    states = States(
        snapshots=snapshots,
        metadata=metadata,
    )

    json_string = states.dumps()

    with open("index.mvsj", "w") as f:
        f.write(json_string)

    with ZipFile(zip_filepath, "a") as f:
        f.writestr("index.mvsj", json_string)
