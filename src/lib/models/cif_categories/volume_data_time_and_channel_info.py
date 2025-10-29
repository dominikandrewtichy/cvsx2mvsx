from ciftools.models.writer import CIFCategoryDesc
from ciftools.models.writer import CIFFieldDesc as Field

from lib.models.cif.common import VolumeDataTimeAndChannelInfo
from lib.models.cif_categories.encoders import bytearray_encoder


class VolumeDataTimeAndChannelInfoCategory(CIFCategoryDesc):
    name = "volume_data_time_and_channel_info"

    @staticmethod
    def get_row_count(_) -> int:
        return 1

    @staticmethod
    def get_field_descriptors(ctx: VolumeDataTimeAndChannelInfo):
        return [
            Field.numbers(
                name="time_id",
                value=lambda d, i: ctx.time_id,
                encoder=bytearray_encoder,
                dtype="i4",
            ),
            Field.numbers(
                name="channel_id",
                value=lambda d, i: ctx.channel_id,
                encoder=bytearray_encoder,
                dtype="i4",
            ),
        ]
