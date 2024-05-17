from dash import html, Output, Input, callback

from src.component_ids import SELECT_GREEDY_OPTIMIZATION_STOP_CRITERIA, DIV_NUMBERFIELD_OPTIMIZATION_STOP_CRITERIA, \
    DIV_BUTTON_RECOMPUTE_GREEDY_STEPS_ID
from src.constants import GreedyOPtimizationCriteria
from src.layouts.layout_main_page import layout_tab_one, layout_tab_two, layout_tab_three, layout_tab_four, \
    layout_tab_five
from src.layouts.layout_radio_items import layout_radio_calc_type, layout_radio_result_type, layout_radio_mechanism


@callback(
    [Output(DIV_NUMBERFIELD_OPTIMIZATION_STOP_CRITERIA, "hidden"),
     Output(DIV_BUTTON_RECOMPUTE_GREEDY_STEPS_ID, "hidden")],
    [Input(SELECT_GREEDY_OPTIMIZATION_STOP_CRITERIA, "value")]
)
def render_tab_map_content(type_analysis: str) -> tuple[bool, bool]:
    if type_analysis == GreedyOPtimizationCriteria.ECONOMIC_OPTIMAL.name:
        return True, True
    return False, False
