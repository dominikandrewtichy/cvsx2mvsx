from ciftools.models.writer import CIFCategoryDesc
from ciftools.models.writer import CIFFieldDesc as Field

from lib.models.cif.lattice_segmentation import SegmentationData3D
from lib.models.cif_categories.encoders import decide_encoder


class SegmentationData3dCategory(CIFCategoryDesc):
    name = "segmentation_data_3d"

    @staticmethod
    def get_row_count(ctx: SegmentationData3D) -> int:
        return ctx.values.size

    @staticmethod
    def get_field_descriptors(ctx: SegmentationData3D):
        encoder, dtype = decide_encoder(ctx.values, "SegmentationData3d")
        return [
            Field.number_array(
                name="values",
                array=lambda volume: volume,
                encoder=lambda _: encoder,
                dtype=dtype,
            ),
        ]
