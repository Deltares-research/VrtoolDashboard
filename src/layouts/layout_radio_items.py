from dash import dcc
import dash_bootstrap_components as dbc

from src.constants import ColorBarResultType, ResultType, CalcType, Mechanism, SubResultType

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
        {"label": ResultType.PROBABILITY.value, "value": ResultType.PROBABILITY.name
         },
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
    id="select_length_cost_switch",
    options=[{"label": "Kosten", "value": "COST"},
             {"label": "Lengte", "value": "LENGTH"}],
    value="COST",
)
