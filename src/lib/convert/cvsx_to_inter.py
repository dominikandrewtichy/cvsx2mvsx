from lib.models.cvsx.cvsx_entry import CVSXEntry
from lib.models.intermediary.inter import (
    InterEntryInfo,
    InterSegmentationFileInfo,
    InterTimeframeInfo,
    InterVolumeFileInfo,
)


def convert_cvsx_to_inter(cvsx_entry: CVSXEntry) -> InterEntryInfo:
    timeframe_map: dict[int, InterTimeframeInfo] = {}

    def _get_or_create(tf_index: int) -> InterTimeframeInfo:
        if tf_index not in timeframe_map:
            timeframe_map[tf_index] = InterTimeframeInfo(timeframe_index=tf_index)
        return timeframe_map[tf_index]

    for filepath, file_info in cvsx_entry.index.volumes.items():
        timeframe = _get_or_create(file_info.timeframeIndex)
        timeframe.volumes.append(
            InterVolumeFileInfo(
                filepath=filepath,
                channel_id=file_info.channelId,
                timeframe_index=file_info.timeframeIndex,
            )
        )

    if cvsx_entry.index.meshSegmentations:
        for mesh_info in cvsx_entry.index.meshSegmentations:
            timeframe = _get_or_create(mesh_info.timeframeIndex)
            for mesh_filename in mesh_info.segmentsFilenames:
                timeframe.segmentations.mesh.append(
                    InterSegmentationFileInfo(
                        filepath=mesh_filename,
                        timeframe_index=mesh_info.timeframeIndex,
                        segmentation_id=mesh_info.segmentationId,
                    )
                )

    if cvsx_entry.index.latticeSegmentations:
        for file_info in cvsx_entry.index.latticeSegmentations.values():
            timeframe = _get_or_create(file_info.timeframeIndex)
            timeframe.segmentations.lattice.append(
                InterSegmentationFileInfo(
                    filepath=mesh_filename,
                    timeframe_index=mesh_info.timeframeIndex,
                    segmentation_id=mesh_info.segmentationId,
                )
            )

    if cvsx_entry.index.geometricSegmentations:
        for file_info in cvsx_entry.index.geometricSegmentations.values():
            timeframe = _get_or_create(file_info.timeframeIndex)
            timeframe.segmentations.geometric.append(
                InterSegmentationFileInfo(
                    filepath=mesh_filename,
                    timeframe_index=mesh_info.timeframeIndex,
                    segmentation_id=mesh_info.segmentationId,
                )
            )

    timeframes = [timeframe_map[i] for i in sorted(timeframe_map.keys())]

    return InterEntryInfo(
        cvsx_entry=cvsx_entry,
        timeframes=timeframes,
    )
