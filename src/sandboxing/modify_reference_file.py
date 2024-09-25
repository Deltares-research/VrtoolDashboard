from pathlib import Path
import json
# path_to_reference_file = Path(r"C:\Users\hauth\bitbucket\VRtoolDashboard\tests\data\Case_31_1\reference\reference_dike_traject.json")
path_to_reference_file = Path(r"C:\Users\hauth\bitbucket\VRtoolDashboard\tests\data\TestCase1_38-1_no_housing\reference\dike_traject_data.json")

with open(path_to_reference_file, "r") as file:
    reference = json.load(file)


########## 1 #############
# for section in reference['dike_sections']:
#
#     mechanisms = []
#     if section.get("initial_assessment", {}) is None:
#         section['active_mechanisms'] = []
#         continue
#     for key in section.get("initial_assessment", {}).keys():
#         if key != "Section":
#             mechanisms.append(key)
#     section['active_mechanisms'] = mechanisms

########## 2 #############
for section in reference["dike_sections"]:
    if section.get("flood_damages", {}) is None:
        section["flood_damages"] = 0

# Write the modified reference file
with open(path_to_reference_file, "w") as file:
    json.dump(reference, file, indent=4)

