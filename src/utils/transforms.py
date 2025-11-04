"""Transformation matrix utilities for mesh processing."""

import numpy as np


def translation_matrix(t: np.ndarray | list[float]) -> np.ndarray:
    """Create a 4x4 translation matrix.

    Args:
        t: Translation vector [tx, ty, tz]

    Returns:
        4x4 translation matrix
    """
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
    """Create a 4x4 scaling matrix.

    Args:
        s: Scale factors [sx, sy, sz]

    Returns:
        4x4 scaling matrix
    """
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
    """Compute transformation matrix from voxel space to world space.

    The transformation applies:
    1. Translation to align origin (negative)
    2. Scaling by voxel size
    3. Translation back to origin (positive)

    Args:
        origin: Origin coordinates in world space [x, y, z]
        voxel_size: Size of each voxel in world units [sx, sy, sz]
        origin_offset: Offset to apply to origin in voxel units (default 0.5)

    Returns:
        4x4 transformation matrix
    """
    origin_voxel = origin + origin_offset

    # Build component matrices
    S = scaling_matrix(voxel_size)
    T_neg = translation_matrix(-origin_voxel)
    T_pos = translation_matrix(origin_voxel)

    # Combine: translate to origin, scale, translate back
    M = T_pos @ S @ T_neg

    return M


def matrix_to_flat_list(matrix: np.ndarray) -> list[float]:
    """Convert a transformation matrix to a flat list for molviewspec.

    Args:
        matrix: 4x4 transformation matrix

    Returns:
        Flattened matrix as list (transposed)
    """
    return matrix.T.flatten().tolist()

def smooth_3d_volume(volume: np.ndarray, iterations: int = 1) -> np.ndarray:
    """
    Smooth a 3D binary or scalar volume using a Mol*-style 6-neighbor averaging kernel.
    Each voxel is averaged with its 6 face-connected neighbors.
    """
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

