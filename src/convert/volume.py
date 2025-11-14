from zipfile import ZipFile

from src.io.cif.read.volume import parse_volume_bcif
from src.models.cvsx.cvsx_annotations import ChannelAnnotation
from src.models.cvsx.cvsx_file import CVSXFile
from src.models.mvsx.mvsx_entry import MVSXVolume
from src.models.read.volume import VolumeCif
from src.utils import get_hex_color


def get_volume_annotations(cvsx_entry: CVSXFile) -> dict[str, ChannelAnnotation]:
    if not cvsx_entry.annotations.volume_channels_annotations:
        return {}
    annotations_map = {}
    for annotation in cvsx_entry.annotations.volume_channels_annotations:
        annotations_map[annotation.channel_id] = annotation
    return annotations_map


def get_volume_cif(cvsx_path: str, inner_path: str) -> VolumeCif:
    with ZipFile(cvsx_path, "r") as z:
        with z.open(inner_path) as f:
            bcif_data = f.read()
            volume_cif: VolumeCif = parse_volume_bcif(bcif_data)
            return volume_cif


def get_list_of_all_volumes(cvsx_file: CVSXFile) -> list[MVSXVolume]:
    mvsx_volumes = []
    annotations = get_volume_annotations(cvsx_file)

    for source_filepath, volume_info in cvsx_file.index.volumes.items():
        destination_filepath = f"volumes/{source_filepath}"
        annotation = annotations.get(volume_info.channelId)

        print(volume_info.channelId)
        color = get_hex_color(annotation)
        label = annotation.label if annotation else None

        # volume_cif = get_volume_cif(cvsx_file.filepath, source_filepath)

        mvsx_volume = MVSXVolume(
            source_filepath=source_filepath,
            destination_filepath=destination_filepath,
            channel_id=volume_info.channelId,
            timeframe_id=volume_info.timeframeIndex,
            label=label,
            color=color,
            opacity=None,
        )

        mvsx_volumes.append(mvsx_volume)

    return mvsx_volumes
