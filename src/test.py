import os
from uuid import uuid4

from lib.convert.lattice_segmentation import (
    bcif_to_lattice_segmentation_cif,
    get_lattice_segment,
    lattice_model_to_bcif,
    read_bcif_file,
)

# with open("data/cvsx/unzipped/custom-tubhiswt/volume_0_0.bcif", "rb") as f:
#     data = f.read()
# model = bcif_to_volume_cif(data)
# model.volume_block.volume_data_3d.values = model.volume_block.volume_data_3d.values[:10]
# pretty_print_lattice_cif(model)
# print()
# exit(1)

# cvsx_filepath = "data/cvsx/zipped/custom-tubhiswt.cvsx"

# cvsx_entry = load_cvsx_entry(cvsx_filepath)

# inter_entry = convert_cvsx_to_inter(cvsx_entry)

# with open("inter_entry.json", "w") as f:
#     f.write(inter_entry.model_dump_json(indent=2))

# convert(inter_entry)

if not os.path.exists("temp"):
    os.mkdir("temp")

filename = "lattice_emd_1273_msk_3_0"
data = read_bcif_file(
    zip_path="data/cvsx/zipped/emd-1273.cvsx",
    inner_path=f"{filename}.bcif",
)
lattice_model = bcif_to_lattice_segmentation_cif(data, "0")
segment_ids = lattice_model.segmentation_block.segmentation_data_table.segment_id
for segment_id in segment_ids:
    model = get_lattice_segment(
        lattice_model.model_copy(deep=True),
        segment_id,
        f"{filename}_{segment_id}",
    )
    name = model.filename if model.filename else uuid4()

    # print(name)
    # pretty_print_lattice_cif(model)
    # print()

    info = model.segmentation_block.volume_data_3d_info

    print(f"Origin: [{info.origin_0}, {info.origin_1}, {info.origin_2}]")
    print(
        f"Dimensions: [{info.dimensions_0}, {info.dimensions_1}, {info.dimensions_2}]"
    )
    print(
        f"Sample count: [{info.sample_count_0}, {info.sample_count_1}, {info.sample_count_2}]"
    )
    print(f"Data shape: {model.segmentation_block.segmentation_data_3d.values.shape}")
    axis_order = [info.axis_order_0, info.axis_order_1, info.axis_order_2]
    print(f"Axis order: {axis_order}")

    # filepath = f"temp/{name}.cif"
    # document = lattice_model_to_cif(model)
    # cif_text = document.as_string()
    # with open(filepath, "w") as f:
    #     f.write(cif_text)

    filepath = f"temp/{name}.bcif"
    bcif_data = lattice_model_to_bcif(model)
    with open(filepath, "wb") as f:
        f.write(bcif_data)
