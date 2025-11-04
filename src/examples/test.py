import os
from uuid import uuid4

from lib.convert.lattice_segmentation import (
    bcif_to_lattice_segmentation_cif,
    get_lattice_segment,
    lattice_model_to_bcif,
    pretty_print_lattice_cif,
    read_bcif_file,
)

if not os.path.exists("temp"):
    os.mkdir("temp")

filename = "lattice_emd_1273_msk_3_0"
data = read_bcif_file(
    zip_path="data/cvsx/zipped/emd-1273.cvsx",
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
    )
    name = model.filename if model.filename else uuid4()

    filepath = f"temp/{name}.bcif"
    bcif_data = lattice_model_to_bcif(model)
    with open(filepath, "wb") as f:
        f.write(bcif_data)
