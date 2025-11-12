import os

import numpy as np
from molviewspec import create_builder
from molviewspec.builder import Root
from molviewspec.mvsx_converter import mvsj_to_mvsx
from skimage import measure

from src.convert.convert_all import rgb_to_hex
from src.convert.lattice import (
    bcif_to_lattice_segmentation_cif,
    get_values_for_lattice_segment,
    read_bcif_file,
)
from src.models.read.lattice_segmentation import LatticeSegmentationCIF


def translation_matrix(t):
    tx, ty, tz = t
    return np.array(
        [
            [1, 0, 0, tx],
            [0, 1, 0, ty],
            [0, 0, 1, tz],
            [0, 0, 0, 1],
        ]
    )


# Build scaling matrix
def scaling_matrix(s):
    sx, sy, sz = s
    return np.array(
        [
            [sx, 0, 0, 0],
            [0, sy, 0, 0],
            [0, 0, sz, 0],
            [0, 0, 0, 1],
        ]
    )


segment_annotations = [
    {
        "color": [0.12156862745098039, 0.4666666666666667, 0.7058823529411765, 1.0],
        "id": "e29988a1-ed3b-4e42-b958-f227de66617b",
        "segment_id": 1,
        "segment_kind": "lattice",
        "segmentation_id": "emd_1273_msk_1",
        "time": 0,
    },
    {
        "color": [1.0, 0.4980392156862745, 0.054901960784313725, 1.0],
        "id": "f4cbed15-3d14-4a3f-8396-837bc566ee5b",
        "segment_id": 1,
        "segment_kind": "lattice",
        "segmentation_id": "emd_1273_msk_2",
        "time": 0,
    },
    {
        "color": [0.17254901960784313, 0.6274509803921569, 0.17254901960784313, 1.0],
        "id": "6b4750f0-c510-412d-80cb-e5c32c811891",
        "segment_id": 1,
        "segment_kind": "lattice",
        "segmentation_id": "emd_1273_msk_3",
        "time": 0,
    },
    {
        "color": [0.8392156862745098, 0.15294117647058825, 0.1568627450980392, 1.0],
        "id": "4bd8bca4-1495-431c-8683-33757e5c8353",
        "segment_id": 1,
        "segment_kind": "lattice",
        "segmentation_id": "emd_1273_msk_4",
        "time": 0,
    },
    {
        "color": [0.5803921568627451, 0.403921568627451, 0.7411764705882353, 1.0],
        "id": "bece6f9e-0b37-4702-9c76-93535e18e642",
        "segment_id": 1,
        "segment_kind": "lattice",
        "segmentation_id": "emd_1273_msk_5",
        "time": 0,
    },
]


def get_segment_color(segmentation_id: str, segment_id: int) -> str | None:
    for annotation in segment_annotations:
        if (
            annotation["segmentation_id"] == segmentation_id
            and annotation["segment_id"] == segment_id
        ):
            r, g, b = annotation["color"][:3]
            color = rgb_to_hex(r, g, b)
            return color
    return None


def voxel_to_mesh(
    lattice_cif: LatticeSegmentationCIF,
    segment_id: int,
) -> LatticeSegmentationCIF | None:
    values = lattice_cif.segmentation_block.segmentation_data_3d.values
    info = lattice_cif.segmentation_block.volume_data_3d_info

    nx, ny, nz = (
        int(info.sample_count_0),
        int(info.sample_count_1),
        int(info.sample_count_2),
    )

    data = values.reshape((nz, ny, nx)).transpose((2, 1, 0))

    # data_3d_values = np.where(data == segment_id, 1.0, 0.0)

    # padded = np.pad(
    #     data_3d_values,
    #     ((1, 1), (1, 1), (1, 1)),
    #     mode="constant",
    #     constant_values=0.0,
    # )

    verts, faces, normals, values = measure.marching_cubes(data, level=0.5)

    faces = faces[:, ::-1]

    vertices = verts.ravel()
    indices = faces.ravel()
    triangle_groups = np.zeros(len(faces))

    return vertices, indices, triangle_groups


def add_segments(builder: Root, zip_path, segmentation_id):
    data = read_bcif_file(
        zip_path=zip_path,
        inner_path=f"lattice_{segmentation_id}_0.bcif",
    )
    lattice_model = bcif_to_lattice_segmentation_cif(data, "0")

    segment_ids = lattice_model.segmentation_block.segmentation_data_table.segment_id
    for segment_id in set(segment_ids):
        if segment_id == 0:
            continue
        model = get_values_for_lattice_segment(
            lattice_model.model_copy(deep=True),
            segment_id,
            f"{segment_id}",
            smooth_iterations=1,
        )
        vertices, indices, triangle_groups = voxel_to_mesh(model, segment_id)
        info = model.segmentation_block.volume_data_3d_info

        voxel_size = np.array(
            [
                info.spacegroup_cell_size_0 / info.sample_count_0,
                info.spacegroup_cell_size_1 / info.sample_count_1,
                info.spacegroup_cell_size_2 / info.sample_count_2,
            ],
        )
        origin = np.array([info.origin_0, info.origin_1, info.origin_2])
        origin_voxel = origin + 0.5

        # 2. Scale vertices by voxel_size to get world units
        S = scaling_matrix(voxel_size)

        # 3. Build translation matrices in **voxel units before scaling**
        T_neg = translation_matrix(-origin_voxel)
        T_pos = translation_matrix(origin_voxel)

        M = T_pos @ S @ T_neg
        matrix = M.T.flatten().tolist()

        builder.primitives(
            instances=[matrix],
        ).mesh(
            vertices=vertices.tolist(),
            indices=indices.tolist(),
            triangle_groups=triangle_groups.tolist(),
            color=get_segment_color(segmentation_id, segment_id),
            tooltip=f"{segment_id}",
        )


def add_volume(builder: Root):
    volume_cif = builder.download(url="./emd-1273/volume_0_0.bcif").parse(format="bcif")
    volume_data = volume_cif.volume(channel_id="0")
    volume_representation = volume_data.representation(
        type="isosurface",
        relative_isovalue=1,
        show_faces=True,
        show_wireframe=False,
    )
    volume_representation.color(color="gray").opacity(opacity=0.2)

    return builder


def main():
    if not os.path.exists("temp"):
        os.mkdir("temp")

    builder = create_builder()
    zip_path = "data/cvsx/zipped/emd-1273.cvsx"

    segmentation_ids = [
        "emd_1273_msk_1",
        "emd_1273_msk_2",
        "emd_1273_msk_3",
        "emd_1273_msk_4",
        "emd_1273_msk_5",
    ]
    add_volume(builder)
    for segmentation_id in segmentation_ids:
        add_segments(builder, zip_path, segmentation_id)
    state = builder.get_state()
    with open("temp/mesh.mvsj", "w") as f:
        f.write(state.model_dump_json(exclude_none=True))

    mvsj_to_mvsx(
        input_mvsj_path="temp/mesh.mvsj",
        output_mvsx_path="temp/mesh.mvsx",
    )


if __name__ == "__main__":
    main()
