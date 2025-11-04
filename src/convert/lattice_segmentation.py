import numpy as np

from src.models.read.lattice import LatticeCif
from src.utils.transforms import smooth_3d_volume


def get_lattice_segment(
    lattice_cif: LatticeCif,
    segment_id: int,
    name: str,
    smooth_iterations: int = 1,
) -> LatticeCif | None:
    """
    Extract the chosen segment, pad by 1 voxel on each side, optionally smooth,
    and update metadata so the padded volume aligns correctly in Mol*.
    """

    values = lattice_cif.segmentation_block.segmentation_data_3d.values
    info = lattice_cif.segmentation_block.volume_data_3d_info

    # original sample counts (before padding)
    nx, ny, nz = (
        int(info.sample_count_0),
        int(info.sample_count_1),
        int(info.sample_count_2),
    )

    # Read flat list into 3D array using the same order as earlier code:
    # values are stored z-major (slowest), so reshape -> transpose to (x,y,z)
    data = np.array(values, dtype=np.float32).reshape((nz, ny, nx))
    data = np.transpose(data, (2, 1, 0))  # -> shape (nx, ny, nz)

    # Binary mask for the requested segment
    data_3d_values = np.where(data == segment_id, 1.0, 0.0)

    # Pad with one voxel border (background = 0)
    padded = np.pad(
        data_3d_values,
        ((1, 1), (1, 1), (1, 1)),
        mode="constant",
        constant_values=0.0,
    )

    # Optional smoothing (if you call smooth_3d_volume)
    if smooth_iterations and smooth_iterations > 0:
        padded = smooth_3d_volume(padded, iterations=smooth_iterations)

    # --- Update metadata: sample counts, origin and dimensions ---
    # Save originals for voxel size calculation
    orig_dims = np.array(
        [float(info.dimensions_0), float(info.dimensions_1), float(info.dimensions_2)]
    )
    orig_counts = np.array([nx, ny, nz], dtype=np.float32)

    # physical voxel size per axis
    voxel_size = orig_dims / orig_counts  # shape (3,)

    # update sample counts (+2 per axis because padded by 1 each side)
    info.sample_count_0 = nx + 2
    info.sample_count_1 = ny + 2
    info.sample_count_2 = nz + 2

    # shift origin by -voxel_size (so original data stays put)
    info.origin_0 = float(info.origin_0) - float(voxel_size[0])
    info.origin_1 = float(info.origin_1) - float(voxel_size[1])
    info.origin_2 = float(info.origin_2) - float(voxel_size[2])

    # increase physical dimensions by 2 * voxel_size
    info.dimensions_0 = float(orig_dims[0] + 2.0 * voxel_size[0])
    info.dimensions_1 = float(orig_dims[1] + 2.0 * voxel_size[1])
    info.dimensions_2 = float(orig_dims[2] + 2.0 * voxel_size[2])

    # --- Update sampling statistics ---
    info.min_sampled = float(padded.min())
    info.max_sampled = float(padded.max())
    info.mean_sampled = float(padded.mean())
    info.sigma_sampled = float(padded.std())

    # Flatten back into CIF order (reverse of the reshape/transposition above)
    padded_for_cif = np.transpose(padded, (2, 1, 0)).ravel()
    lattice_cif.segmentation_block.segmentation_data_3d.values = padded_for_cif

    lattice_cif.filename = name

    return lattice_cif
