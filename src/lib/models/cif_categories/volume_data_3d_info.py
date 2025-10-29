from ciftools.models.writer import CIFCategoryDesc
from ciftools.models.writer import CIFFieldDesc as Field

from lib.models.cif.common import VolumeData3DInfo
from lib.models.cif_categories.encoders import bytearray_encoder


class VolumeData3dInfoCategory(CIFCategoryDesc):
    name = "volume_data_3d_info"

    @staticmethod
    def get_row_count(_) -> int:
        return 1

    @staticmethod
    def get_field_descriptors(ctx: VolumeData3DInfo):
        return [
            Field.strings(
                name="name",
                value=lambda d, i: ctx.name,
            ),
            Field.numbers(
                name="axis_order[0]",
                value=lambda d, i: ctx.axis_order_0,
                encoder=bytearray_encoder,
                dtype="i4",
            ),
            Field.numbers(
                name="axis_order[1]",
                value=lambda d, i: ctx.axis_order_1,
                encoder=bytearray_encoder,
                dtype="i4",
            ),
            Field.numbers(
                name="axis_order[2]",
                value=lambda d, i: ctx.axis_order_2,
                encoder=bytearray_encoder,
                dtype="i4",
            ),
            # origin
            Field.numbers(
                name="origin[0]",
                value=lambda d, i: ctx.origin_0,
                encoder=bytearray_encoder,
                dtype="f4",
            ),
            Field.numbers(
                name="origin[1]",
                value=lambda d, i: ctx.origin_1,
                encoder=bytearray_encoder,
                dtype="f4",
            ),
            Field.numbers(
                name="origin[2]",
                value=lambda d, i: ctx.origin_2,
                encoder=bytearray_encoder,
                dtype="f4",
            ),
            # dimensions
            Field.numbers(
                name="dimensions[0]",
                value=lambda d, i: ctx.dimensions_0,
                encoder=bytearray_encoder,
                dtype="f4",
            ),
            Field.numbers(
                name="dimensions[1]",
                value=lambda d, i: ctx.dimensions_1,
                encoder=bytearray_encoder,
                dtype="f4",
            ),
            Field.numbers(
                name="dimensions[2]",
                value=lambda d, i: ctx.dimensions_2,
                encoder=bytearray_encoder,
                dtype="f4",
            ),
            # sampling
            Field.numbers(
                name="sample_rate",
                value=lambda d, i: ctx.sample_rate,
                encoder=bytearray_encoder,
                dtype="i4",
            ),
            Field.numbers(
                name="sample_count[0]",
                value=lambda d, i: ctx.sample_count_0,
                encoder=bytearray_encoder,
                dtype="i4",
            ),
            Field.numbers(
                name="sample_count[1]",
                value=lambda d, i: ctx.sample_count_1,
                encoder=bytearray_encoder,
                dtype="i4",
            ),
            Field.numbers(
                name="sample_count[2]",
                value=lambda d, i: ctx.sample_count_2,
                encoder=bytearray_encoder,
                dtype="i4",
            ),
            # spacegroup
            Field.numbers(
                name="spacegroup_number",
                value=lambda d, i: 1,
                encoder=bytearray_encoder,
                dtype="i4",
            ),
            Field.numbers(
                name="spacegroup_cell_size[0]",
                value=lambda d, i: ctx.spacegroup_cell_size_0,
                encoder=bytearray_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name="spacegroup_cell_size[1]",
                value=lambda d, i: ctx.spacegroup_cell_size_1,
                encoder=bytearray_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name="spacegroup_cell_size[2]",
                value=lambda d, i: ctx.spacegroup_cell_size_2,
                encoder=bytearray_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name="spacegroup_cell_angles[0]",
                value=lambda d, i: ctx.spacegroup_cell_angles_0,
                encoder=bytearray_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name="spacegroup_cell_angles[1]",
                value=lambda d, i: ctx.spacegroup_cell_angles_1,
                encoder=bytearray_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name="spacegroup_cell_angles[2]",
                value=lambda d, i: ctx.spacegroup_cell_angles_2,
                encoder=bytearray_encoder,
                dtype="f8",
            ),
            # misc
            Field.numbers(
                name="mean_source",
                value=lambda d, i: ctx.mean_source,
                encoder=bytearray_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name="mean_sampled",
                value=lambda d, i: ctx.mean_sampled,
                encoder=bytearray_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name="sigma_source",
                value=lambda d, i: ctx.sigma_source,
                encoder=bytearray_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name="sigma_sampled",
                value=lambda d, i: ctx.sigma_sampled,
                encoder=bytearray_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name="min_source",
                value=lambda d, i: ctx.min_source,
                encoder=bytearray_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name="min_sampled",
                value=lambda d, i: ctx.min_sampled,
                encoder=bytearray_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name="max_source",
                value=lambda d, i: ctx.max_source,
                encoder=bytearray_encoder,
                dtype="f8",
            ),
            Field.numbers(
                name="max_sampled",
                value=lambda d, i: ctx.max_sampled,
                encoder=bytearray_encoder,
                dtype="f8",
            ),
        ]
