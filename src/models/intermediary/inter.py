from pydantic import BaseModel

from src.models.cvsx.cvsx_entry import CVSXEntry
from src.models.cvsx.cvsx_index import (
    GeometricSegmentationFileInfo,
    LatticeSegmentationFileInfo,
    MeshSegmentationFilesInfo,
)


class InterVolume(BaseModel):
    filepath: str
    channelId: str
    timeframeIndex: int


class InterTimeframeSegmentations(BaseModel):
    mesh: list[MeshSegmentationFilesInfo] = []
    lattice: list[LatticeSegmentationFileInfo] = []
    geometric: list[GeometricSegmentationFileInfo] = []


class InterTimeframe(BaseModel):
    index: int
    volumes: list[InterVolume] = []
    segmentations: InterTimeframeSegmentations = InterTimeframeSegmentations()


class InterTimeframeGroupedIndex(BaseModel):
    timeframes: list[InterTimeframe]

    @classmethod
    def from_cvsx_index(cls, entry: CVSXEntry) -> "InterTimeframeGroupedIndex":
        timeframe_map: dict[int, InterTimeframe] = {}

        def _get_or_create(tf_index: int) -> InterTimeframe:
            if tf_index not in timeframe_map:
                timeframe_map[tf_index] = InterTimeframe(index=tf_index)
            return timeframe_map[tf_index]

        index = entry.index

        for filepath, file_info in index.volumes.items():
            tf = _get_or_create(file_info.timeframeIndex)
            tf.volumes.append(
                InterVolume(
                    filepath=filepath,
                    channelId=file_info.channelId,
                    timeframeIndex=file_info.timeframeIndex,
                )
            )
        if index.meshSegmentations:
            for mesh_info in index.meshSegmentations:
                tf = _get_or_create(mesh_info.timeframeIndex)
                tf.segmentations.mesh.append(mesh_info)
        if index.latticeSegmentations:
            for file_info in index.latticeSegmentations.values():
                tf = _get_or_create(file_info.timeframeIndex)
                tf.segmentations.lattice.append(file_info)
        if index.geometricSegmentations:
            for file_info in index.geometricSegmentations.values():
                tf = _get_or_create(file_info.timeframeIndex)
                tf.segmentations.geometric.append(file_info)

        sorted_timeframes = [timeframe_map[i] for i in sorted(timeframe_map.keys())]

        return cls(timeframes=sorted_timeframes)
