import json
from pathlib import Path

from src.constants import ResultType
from src.linear_objects.reinforcement_program import (
    DikeProgram,
    get_projects_from_saved_data,
)
from src.plotly_graphs.project_page.plotly_maps import plot_project_overview_map
from src.plotly_graphs.project_page.plotly_plots import projects_reliability_over_time

saved_data_path = Path(
    r"C:\Users\hauth\OneDrive - Stichting Deltares\Documents\tempo\VRM\bug_area\41-2 urgentie.json"
)
data = json.load(open(saved_data_path))
print(data.keys())

_imported_runs_data = data["imported_runs_data"]
_projects_overview_data = data["project_data"]

# _projects, _ = get_projects_from_saved_data(_imported_runs_data, _projects_overview_data)
#
# _fig = plot_project_overview_map(_projects)
# _fig.show()


program = DikeProgram(_imported_runs_data, _projects_overview_data)

# 2. Call
_fig = projects_reliability_over_time(program, ResultType.RELIABILITY.name)
_fig.show()
