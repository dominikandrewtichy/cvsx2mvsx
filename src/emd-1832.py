import json
import os
from uuid import uuid4

from molviewspec import create_builder
from molviewspec.builder import Root
from molviewspec.mvsx_converter import mvsj_to_mvsx

from lib.convert.convert_all import rgb_to_hex
from lib.convert.lattice_segmentation import (
    bcif_to_lattice_segmentation_cif,
    get_lattice_segment,
    lattice_model_to_bcif,
    pretty_print_lattice_cif,
    read_bcif_file,
)


def emd_1832_volume(builder: Root):
    volume_cif = builder.download(url="./volume_0_0.bcif").parse(format="bcif")
    volume_data = volume_cif.volume(custom={"is_volume": True})
    volume_representation = volume_data.representation(
        type="isosurface",
        relative_isovalue=2.73,
        show_faces=True,
        show_wireframe=False,
    )
    volume_representation.color(color="white").opacity(opacity=0.4)

    return builder


def emd_1832_lattices(builder: Root):
    segment_ids = [
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
    for segment_id in segment_ids:
        volume_cif = builder.download(
            url=f"./lattice_0_0_{segment_id['segment_id']}.bcif"
        ).parse(format="bcif")
        volume_data = volume_cif.volume(custom={"is_volume": True})
        volume_representation = volume_data.representation(
            type="isosurface",
            relative_isovalue=2.73,
            show_wireframe=False,
            show_faces=True,
        )
        r, g, b = segment_id["color"][:3]
        color = rgb_to_hex(r, g, b)
        volume_representation.color(color=color).opacity(opacity=1)

    return builder


def emd_1832() -> Root:
    builder: Root = create_builder()

    emd_1832_volume(builder)
    emd_1832_lattices(builder)

    return builder


if not os.path.exists("temp"):
    os.mkdir("temp")

filename = "lattice_0_0"
data = read_bcif_file(
    zip_path="data/cvsx/zipped/emd-1832.cvsx",
    inner_path=f"{filename}.bcif",
)
lattice_model = bcif_to_lattice_segmentation_cif(data, "0")
pretty_print_lattice_cif(lattice_model)
segment_ids = lattice_model.segmentation_block.segmentation_data_table.segment_id
for segment_id in set(segment_ids):
    if segment_id == 0:
        continue
    model = get_lattice_segment(
        lattice_model.model_copy(deep=True),
        segment_id,
        f"{filename}_{segment_id}",
        smooth_iterations=1,
    )
    name = model.filename if model.filename else uuid4()

    filepath = f"temp/{name}.bcif"
    bcif_data = lattice_model_to_bcif(model)
    with open(filepath, "wb") as f:
        f.write(bcif_data)

json_data = emd_1832().get_state()
with open("temp/emd-1832.mvsj", "w") as f:
    f.write(json.dumps(json_data.model_dump(exclude_none=True)))

mvsj_to_mvsx(
    input_mvsj_path="temp/emd-1832.mvsj",
    output_mvsx_path="temp/emd-1832.mvsx",
)
