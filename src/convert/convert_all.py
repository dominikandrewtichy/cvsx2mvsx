from src.models.cvsx.cvsx_annotations import CVSXAnnotations

RgbaType = tuple[float, float, float, float]


def rgba_to_hex_color(rgba: RgbaType) -> str:
    r, g, b, _ = rgba
    return "#{:02X}{:02X}{:02X}".format(int(r * 255), int(g * 255), int(b * 255))


def rgba_to_opacity(rgba: RgbaType) -> float:
    return rgba[3]


def get_volume_color(annotations: CVSXAnnotations, channel_id: str) -> str | None:
    if not annotations.volume_channels_annotations:
        return None
    for annotation in annotations.volume_channels_annotations:
        if annotation.channel_id == channel_id:
            r, g, b = annotation.color[:3]
            return rgb_to_hex(r, g, b)


def get_volume_opacity(annotations: CVSXAnnotations, channel_id: str) -> float | None:
    if not annotations.volume_channels_annotations:
        return None
    for annotation in annotations.volume_channels_annotations:
        if annotation.channel_id == channel_id:
            return annotation.color[3]
