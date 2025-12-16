import json
from pathlib import Path

with open(Path(__file__).parent / "dike_data.json") as f:
    _dike_data = json.load(f)


# for section in _dike_data["dike_sections"]:
#     section["revetment"] = False

for section in _dike_data["dike_sections"]:
    if section["final_measure_doorsnede"]:
        if "+" in section["final_measure_doorsnede"]["ID"]:
            section["final_measure_doorsnede"]["investment_year"] = [0, 0]
        else:
            section["final_measure_doorsnede"]["investment_year"] = [0]
    if section["final_measure_veiligheidsrendement"]:
        if "+" in section["final_measure_veiligheidsrendement"]["ID"]:
            section["final_measure_veiligheidsrendement"]["investment_year"] = [0, 0]
        else:
            section["final_measure_veiligheidsrendement"]["investment_year"] = [0]


# save to json
with open(Path(__file__).parent / "dike_data.json", "w") as f:
    json.dump(_dike_data, f, indent=4)
