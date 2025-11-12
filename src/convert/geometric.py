from zipfile import ZipFile

from src.convert.common import (
    get_segmentation_annotations,
    get_segmentation_descriptions,
)
from src.io.cif.read.geometric import parse_geometric_json
from src.models.cvsx.cvsx_file import CVSXFile
from src.models.mvsx.mvsx_entry import MVSXSegmentation
from src.models.mvsx.mvsx_segmentation import MVSXGeometricSegmentation, MVSXSphereSegmentation
from src.models.read.geometric import (
    ShapePrimitive,
    ShapePrimitiveData,
)
from src.utils import get_hex_color, rgba_to_opacity


def get_shape_mesh(cvsx_file: CVSXFile, shape: ShapePrimitive):
    raise ValueError(f"Unexpected shape kind: {shape.kind}")


def get_shape_data(cvsx_path: str, inner_path: str) -> ShapePrimitiveData:
    with ZipFile(cvsx_path, "r") as z:
        with z.open(inner_path) as f:
            bcif_data = f.read()
            lattice_cif: ShapePrimitiveData = parse_geometric_json(bcif_data)
            return lattice_cif


def get_list_of_all_geometric_segmentations(
    cvsx_file: CVSXFile,
) -> list[MVSXSegmentation]:
    if not cvsx_file.index.geometricSegmentations:
        return []

    mvsx_segmentations: list[MVSXGeometricSegmentation] = []
    segmentation_annotations = get_segmentation_annotations(cvsx_file)
    segmentation_descriptions = get_segmentation_descriptions(cvsx_file, "primitive")

    for (
        source_filepath,
        segmentation_info,
    ) in cvsx_file.index.geometricSegmentations.items():
        destination_filepath = f"segmentations/{source_filepath}"
        segmentation_id = segmentation_info.segmentationId
        timeframe_id = segmentation_info.timeframeIndex

        shape_data: ShapePrimitiveData = get_shape_data(
            cvsx_file.filepath,
            source_filepath,
        )

        for shape in shape_data.shape_primitive_list:
            segment_id = shape.id
            annotation = segmentation_annotations.get((segmentation_id, segment_id))
            descriptions = segmentation_descriptions.get((segmentation_id, segment_id))

            color = get_hex_color(annotation)
            opacity = rgba_to_opacity(annotation)

            # sanity check
            if annotation:
                assert annotation.segment_kind == "primitive"
                assert annotation.segment_id == segment_id
                assert annotation.segmentation_id == segmentation_id
                assert annotation.time == timeframe_id

            # if shape.kind == "box":
            #     return get_box_shape_mesh(cvsx_file, shape)
            # if shape.kind == "cylinder":
            #     return get_cylinder_shape_mesh(cvsx_file, shape)
            # if shape.kind == "ellipsoid":
            #     return get_ellipsoid_shape_mesh(cvsx_file, shape)
            # if shape.kind == "pyramid":
            #     return get_pyramid_shape_mesh(cvsx_file, shape)
            if shape.kind == "sphere":
                mvsx_segmentation = MVSXSphereSegmentation(
                    type="primitive",
                    source_filepath=source_filepath,
                    destination_filepath=destination_filepath,
                    timeframe_id=timeframe_id,
                    segmentation_id=segmentation_id,
                    segment_id=segment_id,
                    color=color,
                    opacity=opacity,
                    descriptions=descriptions,
                    center=shape.center,
                    radius=shape.radius,
                )

            mvsx_segmentations.append(mvsx_segmentation)

    return mvsx_segmentations
