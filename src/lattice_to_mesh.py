import os

import numpy as np
from molviewspec import create_builder
from skimage import measure

from lib.convert.convert_all import rgb_to_hex
from lib.convert.lattice_segmentation import (
    bcif_to_lattice_segmentation_cif,
    get_lattice_segment,
    read_bcif_file,
)
from lib.models.cif.lattice_segmentation import LatticeSegmentationCIF


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
        "color": [0.521576881408691, 0.889867722988129, 0.848475754261017, 1.0],
        "id": "847fefd0-ebe2-4768-936f-de91e7b5cd00",
        "segment_id": 85,
        "segment_kind": "lattice",
        "segmentation_id": "0",
        "time": 0,
    },
    {
        "color": [0.504164099693298, 0.644178092479706, 0.78633439540863, 1.0],
        "id": "c9577740-341d-4766-90a6-db9588fd0c24",
        "segment_id": 93,
        "segment_kind": "lattice",
        "segmentation_id": "0",
        "time": 0,
    },
    {
        "color": [0.669882595539093, 0.86139714717865, 0.948218941688538, 1.0],
        "id": "35a55e35-b02b-4379-a4b2-f87d4fd7ac3b",
        "segment_id": 97,
        "segment_kind": "lattice",
        "segmentation_id": "0",
        "time": 0,
    },
    {
        "color": [0.862361133098602, 0.965298295021057, 0.697644174098969, 1.0],
        "id": "482fd7d9-6ec7-45e3-94f1-17ac3481249f",
        "segment_id": 101,
        "segment_kind": "lattice",
        "segmentation_id": "0",
        "time": 0,
    },
    {
        "color": [0.706890761852264, 0.626759827136993, 0.604495763778687, 1.0],
        "id": "07013de2-b1dc-40c0-b237-1c3b57fe7cb6",
        "segment_id": 103,
        "segment_kind": "lattice",
        "segmentation_id": "0",
        "time": 0,
    },
    {
        "color": [0.787909328937531, 0.924791157245636, 0.951091408729553, 1.0],
        "id": "75f236b1-798c-4a43-b796-47018a62344e",
        "segment_id": 104,
        "segment_kind": "lattice",
        "segmentation_id": "0",
        "time": 0,
    },
]


def get_segment_color(segment_id: int) -> str | None:
    for annotation in segment_annotations:
        if annotation["segment_id"] == segment_id:
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


if not os.path.exists("temp"):
    os.mkdir("temp")

data = read_bcif_file(
    zip_path="data/cvsx/zipped/emd-1832.cvsx",
    inner_path="lattice_0_0.bcif",
)
lattice_model = bcif_to_lattice_segmentation_cif(data, "0")

builder = create_builder()
segment_ids = lattice_model.segmentation_block.segmentation_data_table.segment_id
for segment_id in set(segment_ids):
    if segment_id == 0:
        continue
    model = get_lattice_segment(
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
        color=get_segment_color(segment_id),
        tooltip=f"{segment_id}",
    )
    with open(f"temp/emd-1832-mesh-{segment_id}.mvsj", "w") as f:
        f.write(builder.get_state().model_dump_json(exclude_none=True))
with open("temp/emd-1832-mesh.mvsj", "w") as f:
    f.write(builder.get_state().model_dump_json(exclude_none=True))
