from molviewspec.builder import Root

from models.mvsx.mvsx_volume import MVSXVolume, MVSXVolumeFilter


def mvsj_add_volume(
    builder: Root,
    volumes: list[MVSXVolume],
    filter: MVSXVolumeFilter,
):
    for volume in volumes:
        if filter.channel_id and volume.channel_id != filter.channel_id:
            continue
        if filter.timeframe_index and volume.timeframe_index != filter.timeframe_index:
            continue
        mvsj_add_volume(builder, volume)


def mvsj_add_volumes(
    builder: Root,
    volume: MVSXVolume,
):
    download = builder.download(url=volume.source_filepath)
    parsed = download.parse(format=volume.format)
    volume_data = parsed.volume(channel_id=volume.channel_id)
    representation = volume_data.representation(
        type="isosurface",
        relative_isovalue=1,
        show_wireframe=False,
        show_faces=True,
    )
    representation.color(color=volume.color)
    representation.opacity(opacity=volume.opacity)

    return builder
