from pathlib import Path
import json
path_to_reference_file = Path(r"C:\Users\hauth\bitbucket\VRtoolDashboard\tests\data\Case_31_1\reference\reference_dike_traject.json")

with open(path_to_reference_file, "r") as file:
    reference = json.load(file)

for section in reference['dike_sections']:

    mechanisms = []
    for key in section.get("initial_assessment", {}).keys():
        if key != "Section":
            mechanisms.append(key)
    section['active_mechanisms'] = mechanisms

# Write the modified reference file
with open(path_to_reference_file, "w") as file:
    json.dump(reference, file, indent=4)

