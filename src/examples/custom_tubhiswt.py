from src.convert.convert_all import convert_all
from src.convert.cvsx_to_inter import convert_cvsx_to_inter
from src.src.io.cvsx.cvsx_loader import load_cvsx_entry

cvsx_filepath = "data/cvsx/zipped/custom-tubhiswt.cvsx"

cvsx_entry = load_cvsx_entry(cvsx_filepath)

inter_entry = convert_cvsx_to_inter(cvsx_entry)

with open("inter_entry.json", "w") as f:
    f.write(inter_entry.model_dump_json(indent=2))

convert_all(inter_entry)
