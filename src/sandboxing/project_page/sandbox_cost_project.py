from pathlib import Path
import json

from src.linear_objects.dike_section import DikeSection
from src.linear_objects.dike_traject import DikeTraject
from src.linear_objects.project import DikeProject, get_projects_from_saved_data
from src.plotly_graphs.project_page.pf_traject_comparison import plot_cost_vs_time_projects

path_data_runs = Path(__file__).parent / 'imported_runs_data.json'
path_overview_projects = Path(__file__).parent / 'project_overview_data.json'



#open the json files
with open(path_data_runs) as f:
    imported_runs_data = json.load(f)

with open(path_overview_projects) as f:
    project_overview_data = json.load(f)


projects, _ = get_projects_from_saved_data(imported_runs_data, project_overview_data)

_fig = plot_cost_vs_time_projects(projects)
_fig.show()

