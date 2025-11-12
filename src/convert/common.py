from src.models.cvsx.cvsx_annotations import DescriptionData, SegmentAnnotationData
from src.models.cvsx.cvsx_file import CVSXFile
from src.models.mvsx.mvsx_segmentation import SegmentationType

SegmentationId = tuple[str, int]


def get_segmentation_annotations(
    cvsx_file: CVSXFile,
) -> dict[SegmentationId, SegmentAnnotationData]:
    annotations_map: dict[SegmentationId, SegmentAnnotationData] = {}
    for annotation in cvsx_file.annotations.segment_annotations:
        segmentation_id = annotation.segmentation_id
        segment_id = annotation.segment_id
        annotations_map[(segmentation_id, segment_id)] = annotation
    return annotations_map


def get_segmentation_descriptions(
    cvsx_file: CVSXFile,
    target_kind: SegmentationType,
) -> dict[SegmentationId, list[DescriptionData]]:
    descriptions_map: dict[SegmentationId, list[DescriptionData]] = {}

    for description_data in cvsx_file.annotations.descriptions.values():
        if description_data.target_kind != target_kind:
            continue
        if not description_data.target_id:
            continue

        segmentation_id = description_data.target_id.segmentation_id
        segment_id = description_data.target_id.segment_id

        key = (segmentation_id, segment_id)
        if key not in descriptions_map:
            descriptions_map[key] = []
        descriptions_map[key].append(description_data)

    return descriptions_map
