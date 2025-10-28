from pydantic import BaseModel

from src.models.cvsx.cvsx_entry import CVSXEntry


class InterFileInfo(BaseModel):
    filepath: str
    timeframe_index: int


class InterVolumeFileInfo(InterFileInfo):
    channel_id: str


class InterSegmentationFileInfo(InterFileInfo):
    segmentation_id: str


class InterSegmentations(BaseModel):
    mesh: list[InterSegmentationFileInfo] = []
    lattice: list[InterSegmentationFileInfo] = []
    geometric: list[InterSegmentationFileInfo] = []


class InterTimeframeInfo(BaseModel):
    timeframe_index: int
    volumes: list[InterVolumeFileInfo] = []
    segmentations: InterSegmentations = InterSegmentations()


class InterEntryInfo(BaseModel):
    cvsx_entry: CVSXEntry
    timeframes: list[InterTimeframeInfo]

    @classmethod
    def from_cvsx_index(cls, entry: CVSXEntry) -> "InterEntryInfo":
        timeframe_map: dict[int, InterTimeframeInfo] = {}

        def _get_or_create(tf_index: int) -> InterTimeframeInfo:
            if tf_index not in timeframe_map:
                timeframe_map[tf_index] = InterTimeframeInfo(timeframe_index=tf_index)
            return timeframe_map[tf_index]

        index = entry.index

        for filepath, file_info in index.volumes.items():
            timeframe = _get_or_create(file_info.timeframeIndex)
            timeframe.volumes.append(
                InterVolumeFileInfo(
                    filepath=filepath,
                    channelId=file_info.channelId,
                    timeframeIndex=file_info.timeframeIndex,
                )
            )
        if index.meshSegmentations:
            for mesh_info in index.meshSegmentations:
                timeframe = _get_or_create(mesh_info.timeframeIndex)
                for mesh_filename in mesh_info.segmentsFilenames:
                    timeframe.segmentations.mesh.append(
                        InterSegmentationFileInfo(
                            filepath=mesh_filename,
                            timeframe_index=mesh_info.timeframeIndex,
                            segmentation_id=mesh_info.segmentationId,
                        )
                    )
        if index.latticeSegmentations:
            for file_info in index.latticeSegmentations.values():
                timeframe = _get_or_create(file_info.timeframeIndex)
                timeframe.segmentations.lattice.append(file_info)
        if index.geometricSegmentations:
            for file_info in index.geometricSegmentations.values():
                timeframe = _get_or_create(file_info.timeframeIndex)
                timeframe.segmentations.geometric.append(file_info)

        sorted_timeframes = [timeframe_map[i] for i in sorted(timeframe_map.keys())]

        return cls(
            cvsx_entry=entry,
            timeframes=sorted_timeframes,
        )
