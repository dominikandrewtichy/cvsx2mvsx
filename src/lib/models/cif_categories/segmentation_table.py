from ciftools.binary.data_types import DataType, DataTypeEnum
from ciftools.models.writer import CIFCategoryDesc
from ciftools.models.writer import CIFFieldDesc as Field

from lib.models.cif.lattice_segmentation import SegmentationDataTable
from lib.models.cif_categories.encoders import bytearray_encoder, delta_rl_encoder


class SegmentationDataTableCategory(CIFCategoryDesc):
    name = "segmentation_data_table"

    @staticmethod
    def get_row_count(ctx: SegmentationDataTable) -> int:
        return ctx.set_id.size

    @staticmethod
    def get_field_descriptors(ctx: SegmentationDataTable):
        dtype = DataType.to_dtype(DataTypeEnum.Int32)
        return [
            Field[SegmentationDataTable].number_array(
                name="set_id",
                array=lambda d: d.set_id,
                dtype=dtype,
                encoder=delta_rl_encoder,
            ),
            Field[SegmentationDataTable].number_array(
                name="segment_id",
                array=lambda d: d.segment_id,
                dtype=dtype,
                encoder=bytearray_encoder,
            ),
        ]
