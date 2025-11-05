from src.models.cvsx.cvsx_entry import CVSXEntry
from src.models.mvsx.mvsx_entry import MVSXSegmentation

def get_segmentation_annotations(cvsx_entry: CVSXEntry) -> dict[str, ChannelAnnotation]:
    if cvsx_entry.annotations.volume_channels_annotations:
        return {}

    annotations_map = {}
    for annotation in cvsx_entry.annotations.volume_channels_annotations:
        annotations_map[annotation.channel_id] = annotation

    return annotations_map


def cvsx_to_mvsx_segmentations(cvsx_entry: CVSXEntry) -> list[MVSXSegmentation]:
    mvsx_segmentations = []
    annotations = get_segmentation_annotations(cvsx_entry)

    for source_filepath, volume_info in cvsx_entry.index.volumes.items():
        destination_filepath = f"volumes/{source_filepath}"
        annotation = annotations.get(volume_info.channelId)
        if annotation:
            color = rgba_to_hex_color(annotation.color)
            opacity = annotation.color[3]
        else:
            color = "#ffffff"
            opacity = 1
        mvsx_volume = MVSXVolume(
            source_filepath=source_filepath,
            destination_filepath=destination_filepath,
            channel_id=volume_info.channelId,
            timeframe_id=volume_info.timeframeIndex,
            isovalue=1,
            label=annotation.label,
            color=color,
            opacity=opacity,
        )

        mvsx_segmentations.append(mvsx_volume)

    return mvsx_segmentations
