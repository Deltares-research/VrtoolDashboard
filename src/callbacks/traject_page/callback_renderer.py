from dash import Input, Output, callback

from src.component_ids import (
    DIV_BUTTON_RECOMPUTE_GREEDY_STEPS_ID,
    DIV_NUMBERFIELD_OPTIMIZATION_STOP_CRITERIA,
    SELECT_GREEDY_OPTIMIZATION_STOP_CRITERIA,
)
from src.constants import GreedyOPtimizationCriteria


@callback(
    [
        Output(DIV_NUMBERFIELD_OPTIMIZATION_STOP_CRITERIA, "hidden"),
        Output(DIV_BUTTON_RECOMPUTE_GREEDY_STEPS_ID, "hidden"),
    ],
    [Input(SELECT_GREEDY_OPTIMIZATION_STOP_CRITERIA, "value")],
)
def render_tab_map_content(type_analysis: str) -> tuple[bool, bool]:
    if type_analysis == GreedyOPtimizationCriteria.ECONOMIC_OPTIMAL.name:
        return True, False
    return False, False
