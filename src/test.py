from lib.convert.cvsx_to_inter import convert_cvsx_to_inter
from lib.convert.inter_to_mvsx import convert
from lib.io.cvsx_loader import load_cvsx_entry

cvsx_filepath = "data/cvsx/zipped/custom-tubhiswt.cvsx"

cvsx_entry = load_cvsx_entry(cvsx_filepath)

inter_entry = convert_cvsx_to_inter(cvsx_entry)

with open("inter_entry.json", "w") as f:
    f.write(inter_entry.model_dump_json(indent=2))


convert(inter_entry)
