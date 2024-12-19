import json
from pathlib import Path

from src.linear_objects.reinforcement_program import get_projects_from_saved_data
from src.plotly_graphs.project_page.plotly_maps import plot_project_overview_map


saved_data_path = Path(r"N:\Projects\11209000\11209353\C. Report - advise\Handreiking\voorbeeld_programmering\Programmering WDOD.json")
data = json.load(open(saved_data_path))
print(data.keys())

_imported_runs_data = data['imported_runs_data']
_projects_overview_data = data['project_data']

_projects, _ = get_projects_from_saved_data(_imported_runs_data, _projects_overview_data)

# 2. Call
_fig = plot_project_overview_map(_projects)
_fig.show()