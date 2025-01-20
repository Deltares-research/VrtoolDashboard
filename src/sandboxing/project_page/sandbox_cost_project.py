from pathlib import Path
import json

from src.linear_objects.dike_section import DikeSection
from src.linear_objects.dike_traject import DikeTraject

path_data_runs = Path(__file__).parent / 'imported_runs_data.json'
path_overview_projects = Path(__file__).parent / 'project_overview_data.json'



#open the json files
with open(path_data_runs) as f:
    imported_runs_data = json.load(f)

with open(path_overview_projects) as f:
    project_overview_data = json.load(f)




