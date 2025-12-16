import json
from pathlib import Path

from src.plotly_graphs.project_page.pf_traject_comparison import (
    plot_pf_time_runs_comparison,
)

path_data = Path(r"C:\Users\hauth\bitbucket\VRtoolDashboard\tests\data").joinpath(
    "project_data.json"
)

with open(path_data, "r") as f:
    data = json.load(f)

switch_cost_beta = "COST"

_fig = plot_pf_time_runs_comparison(data, switch_cost_beta)
_fig.show()
