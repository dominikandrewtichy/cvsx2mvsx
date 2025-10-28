from molviewspec.builder import Root

from src.lib.models.mvsx.mvsx_entry import MVSXVolume


def mvsj_add_volume(
    builder: Root,
    volume: MVSXVolume,
):
    download = builder.download(url=volume.source_filepath)
    parsed = download.parse(format=volume.format)
    volume_data = parsed.volume(channel_id=volume.channel_id)
    representation = volume_data.representation(
        type="isosurface",
        relative_isovalue=volume.isovalue,
    )
    representation.color(color=volume.color)
    representation.opacity(opacity=volume.opacity)

    return builder
