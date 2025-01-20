import json
from pathlib import Path

from src.callbacks.project_page.callback_tabs_switch_project_page import update_project_page_visualization
from src.constants import ResultType

_data = json.load(
    open(Path(r"C:\Users\hauth\OneDrive - Stichting Deltares\Documents\tempo\VRM\risk_table").joinpath(
        "Programmering VRM januari 2025 - versneld.json")))

_imported_runs_data = _data['imported_runs_data']
_projects_overview_data = _data['project_data']

_, _, _, _, _, risk_table = update_project_page_visualization("tab-112", ResultType.PROBABILITY.name,
                                                              _imported_runs_data,
                                                              _projects_overview_data)

print(risk_table)
