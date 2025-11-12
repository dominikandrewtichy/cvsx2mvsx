from src.models.cvsx.cvsx_annotations import ChannelAnnotation
from src.models.cvsx.cvsx_file import CVSXFile
from src.models.mvsx.mvsx_entry import MVSXVolume
from src.utils import get_hex_color, rgba_to_opacity


def get_volume_annotations(cvsx_entry: CVSXFile) -> dict[str, ChannelAnnotation]:
    if cvsx_entry.annotations.volume_channels_annotations:
        return {}
    annotations_map = {}
    for annotation in cvsx_entry.annotations.volume_channels_annotations:
        annotations_map[annotation.channel_id] = annotation
    return annotations_map


def get_list_of_all_volumes(cvsx_file: CVSXFile) -> list[MVSXVolume]:
    mvsx_volumes = []
    annotations = get_volume_annotations(cvsx_file)

    for source_filepath, volume_info in cvsx_file.index.volumes.items():
        destination_filepath = f"volumes/{source_filepath}"
        annotation = annotations.get(volume_info.channelId)

        if annotation:
            color = get_hex_color(annotation.color)
            opacity = rgba_to_opacity(annotation.color)
            label = annotation.label
        else:
            color = "#ffffff"
            opacity = 1
            label = None

        mvsx_volume = MVSXVolume(
            source_filepath=source_filepath,
            destination_filepath=destination_filepath,
            channel_id=volume_info.channelId,
            timeframe_id=volume_info.timeframeIndex,
            isovalue=1,
            label=label,
            color=color,
            opacity=opacity,
        )

        mvsx_volumes.append(mvsx_volume)

    return mvsx_volumes
