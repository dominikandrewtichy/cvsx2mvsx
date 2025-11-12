import numpy as np

from src.models.cvsx.cvsx_annotations import CVSXAnnotations, SegmentAnnotationData


def translation_matrix(t: np.ndarray | list[float]) -> np.ndarray:
    if isinstance(t, list):
        t = np.array(t)
    tx, ty, tz = t
    return np.array(
        [
            [1, 0, 0, tx],
            [0, 1, 0, ty],
            [0, 0, 1, tz],
            [0, 0, 0, 1],
        ]
    )


def scaling_matrix(s: np.ndarray | list[float]) -> np.ndarray:
    if isinstance(s, list):
        s = np.array(s)
    sx, sy, sz = s
    return np.array(
        [
            [sx, 0, 0, 0],
            [0, sy, 0, 0],
            [0, 0, sz, 0],
            [0, 0, 0, 1],
        ]
    )


def compute_voxel_to_world_transform(
    origin: np.ndarray,
    voxel_size: np.ndarray,
    origin_offset: float = 0.5,
) -> np.ndarray:
    origin_voxel = origin + origin_offset

    # Build component matrices
    S = scaling_matrix(voxel_size)
    T_neg = translation_matrix(-origin_voxel)
    T_pos = translation_matrix(origin_voxel)

    # Combine: translate to origin, scale, translate back
    M = T_pos @ S @ T_neg

    return M


def matrix_to_flat_list(matrix: np.ndarray) -> list[float]:
    return matrix.T.flatten().tolist()


def smooth_3d_volume(volume: np.ndarray, iterations: int = 1) -> np.ndarray:
    vol = volume.astype(np.float32)
    for _ in range(iterations):
        padded = np.pad(vol, pad_width=1, mode="edge")

        # Center voxel + 6 neighbors
        center = padded[1:-1, 1:-1, 1:-1]
        xp = padded[2:, 1:-1, 1:-1]
        xn = padded[:-2, 1:-1, 1:-1]
        yp = padded[1:-1, 2:, 1:-1]
        yn = padded[1:-1, :-2, 1:-1]
        zp = padded[1:-1, 1:-1, 2:]
        zn = padded[1:-1, 1:-1, :-2]

        # Weighted average (Mol* kernel: center=2, neighbors=1)
        vol = (2 * center + xp + xn + yp + yn + zp + zn) / 8.0

    return vol


RgbaType = tuple[float, float, float, float]


def get_hex_color(annotation: SegmentAnnotationData | None) -> str | None:
    if not annotation or not annotation.color:
        return None
    r, g, b, _ = annotation.color
    return "#{:02X}{:02X}{:02X}".format(int(r * 255), int(g * 255), int(b * 255))


def rgba_to_opacity(annotation: SegmentAnnotationData | None) -> float | None:
    if not annotation or not annotation.color:
        return None
    return annotation.color[3]


def get_volume_color(annotations: CVSXAnnotations, channel_id: str) -> str | None:
    if not annotations.volume_channels_annotations:
        return None
    for annotation in annotations.volume_channels_annotations:
        if annotation.channel_id == channel_id:
            rgba = annotation.color[:3]
            return get_hex_color(rgba)


def get_volume_opacity(annotations: CVSXAnnotations, channel_id: str) -> float | None:
    if not annotations.volume_channels_annotations:
        return None
    for annotation in annotations.volume_channels_annotations:
        if annotation.channel_id == channel_id:
            return annotation.color[3]
