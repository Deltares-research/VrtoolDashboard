import dash_bootstrap_components as dbc

from src.component_ids import SELECT_GREEDY_OPTIMIZATION_STOP_CRITERIA, SELECT_DIKE_SECTION_FOR_MEASURES_ID, \
    RADIO_PROJECT_PAGE_RESULT_TYPE, RADIO_COMPARISON_PAGE_RESULT_TYPE, SELECT_LENGTH_COST_SWITCH
from src.constants import ColorBarResultType, ResultType, CalcType, Mechanism, SubResultType, GreedyOPtimizationCriteria

"""
Keep preferably RadioItems components from .dbc library as they can be styled easily from css file.
"""

layout_radio_color_bar_result_type = dbc.RadioItems(
    id="select_measure_map_result_type",
    options=[
        {"label": ColorBarResultType.MEASURE.value, "value": ColorBarResultType.MEASURE.name},
        {"label": ColorBarResultType.RELIABILITY.value,
         "value": ColorBarResultType.RELIABILITY.name},
        {"label": ColorBarResultType.COST.value, "value": ColorBarResultType.COST.name},
    ],
    value=ColorBarResultType.MEASURE.name,
    inline=True,
    className='my-radio-items',  # add a class name
    style={'width': '40vh', "height": "6vh", "margin-top": "2px"}

)

layout_radio_result_type = dbc.RadioItems(
    id="select_result_type",
    options=[
        {"label": ResultType.RELIABILITY.value, "value": ResultType.RELIABILITY.name},
        {"label": ResultType.PROBABILITY.value, "value": ResultType.PROBABILITY.name},
        {"label": ResultType.INTERPRETATION_CLASS.value, "value": ResultType.INTERPRETATION_CLASS.name},

    ],
    value=ResultType.RELIABILITY.name,
    style={'width': '40vh', "height": "6vh", "margin-top": "2px"}
)

layout_radio_calc_type = dbc.RadioItems(
    id="select_calculation_type",
    options=[
        {"label": CalcType.DOORSNEDE_EISEN.value, "value": CalcType.DOORSNEDE_EISEN.name},
        {"label": CalcType.VEILIGHEIDSRENDEMENT.value,
         "value": CalcType.VEILIGHEIDSRENDEMENT.name},
    ],
    value=CalcType.VEILIGHEIDSRENDEMENT.name,
    style={'width': '40vh', "height": "6vh", "margin-top": "2px"}
)

layout_radio_mechanism = dbc.RadioItems(
    id="select_mechanism_type",
    options=[
        {"label": Mechanism.PIPING.value, "value": Mechanism.PIPING.name},
        {"label": Mechanism.STABILITY.value, "value": Mechanism.STABILITY.name},
        {"label": Mechanism.OVERFLOW.value, "value": Mechanism.OVERFLOW.name},
        {"label": Mechanism.REVETMENT.value, "value": Mechanism.REVETMENT.name},
        {"label": Mechanism.SECTION.value, "value": Mechanism.SECTION.name},
    ],
    value=Mechanism.SECTION.name,
    style={'width': '40vh', "height": "6vh", "margin-top": "2px"}
)

layout_radio_sub_type_result = dbc.RadioItems(
    id='select_sub_result_type_measure_map',
    options=[],
    value=SubResultType.MEASURE_TYPE.name,
)

layout_radio_length_switch = dbc.RadioItems(
    id=SELECT_LENGTH_COST_SWITCH,
    options=[{"label": "Kosten", "value": "COST"},
             {"label": "Lengte", "value": "LENGTH"},
             ],
    value="COST",
)

layout_radio_greedy_optimization_stop_criteria = dbc.RadioItems(
    id=SELECT_GREEDY_OPTIMIZATION_STOP_CRITERIA,
    options=[{"label": GreedyOPtimizationCriteria.ECONOMIC_OPTIMAL.value,
              "value": GreedyOPtimizationCriteria.ECONOMIC_OPTIMAL.name},
             {"label": GreedyOPtimizationCriteria.TARGET_PF.value, "value": GreedyOPtimizationCriteria.TARGET_PF.name},
             ],
    value=GreedyOPtimizationCriteria.ECONOMIC_OPTIMAL.name,

)

layout_radio_helper_map_switch = dbc.RadioItems(
    id="select_helper_map_switch",
    options=[{"label": "Simpel", "value": "SIMPLE"},
             {"label": "Gedetailleerd", "value": "DETAILED"},
             ],
    value="SIMPLE",
    inline=True
)

##### Projects page #####

layout_radio_result_type_project_page = dbc.RadioItems(
    id=RADIO_PROJECT_PAGE_RESULT_TYPE,
    options=[
        {"label": ResultType.RELIABILITY.value, "value": ResultType.RELIABILITY.name},
        {"label": ResultType.PROBABILITY.value, "value": ResultType.PROBABILITY.name},
        {"label": ResultType.DISTANCE_TO_NORM.value, "value": ResultType.DISTANCE_TO_NORM.name},
        {"label": ResultType.RISK.value, "value": ResultType.RISK.name},
        {"label": ResultType.RISK_FACTOR.value, "value": ResultType.RISK_FACTOR.name},
    ],
    inline=True,
    value=ResultType.RELIABILITY.name,
    style={"margin-top": "2px", "margin-left": "10px"}
)

#### Comparison Page ####

layout_radio_result_type_comparison_page = dbc.RadioItems(
    id=RADIO_COMPARISON_PAGE_RESULT_TYPE,
    options=[
        {"label": ResultType.RELIABILITY.value, "value": ResultType.RELIABILITY.name},
        {"label": ResultType.PROBABILITY.value, "value": ResultType.PROBABILITY.name},
    ],
    inline=True,
    value=ResultType.RELIABILITY.name,
    style={"margin-top": "2px", "margin-left": "10px"}
)
