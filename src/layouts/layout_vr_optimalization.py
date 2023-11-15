from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dash_table import DataTable

from src.component_ids import OPTIMIZE_BUTTON_ID, DUMMY_OPTIMIZE_BUTTON_OUTPUT_ID, EDITABLE_TRAJECT_TABLE_ID, \
    OPTIMIZATION_NEW_RUN_NAME_ID
from src.constants import Measures

row1 = html.Tr([html.Td("01A"), html.Td("Aan"), html.Td("Bermverbreding"), html.Td("2025")])
row2 = html.Tr([html.Td("01B"), html.Td("Uit"), html.Td("VZG"), html.Td("2025")])
row3 = html.Tr([html.Td("2"), html.Td("Aan"), html.Td("Stabiliteitsscherm"), html.Td("2035")])
row4 = html.Tr([html.Td("3"), html.Td("Aan"), html.Td("VZG"), html.Td("2035")])

table_body = [html.Tbody([row1, row2, row3, row4])]

dike_vr_optimization_layout = html.Div([

    DataTable(id=EDITABLE_TRAJECT_TABLE_ID,
              columns=(
                  [{'id': 'section_col', 'name': 'Dijkvak'},
                   {'id': 'reinforcement_col', 'name': 'Versterking', 'presentation': 'dropdown'},
                   {'id': 'measure_col', 'name': 'Maatregel', 'presentation': 'dropdown'},
                   {'id': 'reference_year_col', 'name': 'Referentiejaar'},
                   ]
              ),
              data=[],
              dropdown={
                  'reinforcement_col': {
                      'options': [{'label': 'Aan', 'value': "yes"}, {'label': 'Uit', 'value': "no"}]},
                  'measure_col': {
                      'options': [{'label': meas.value, 'value': meas.name} for meas in Measures]},
              },
              style_cell={'textAlign': 'left'},
              editable=True,
              # fixed_rows={'headers': True},  # either fix row with risk of overlap or have a slider
              style_table={'overflowX': 'scroll',
                           'overflowY': 'scroll'},

              ),

    html.Div(
        [
            dbc.Input(id=OPTIMIZATION_NEW_RUN_NAME_ID, placeholder="Optimization run naam", type="text"),
            dbc.Button("Optimize", id=OPTIMIZE_BUTTON_ID, color="primary", className="mr-1"),
            dbc.Tooltip("Click to call VRCore optimization routine via the new calculation constraints.",
                        target=OPTIMIZE_BUTTON_ID),
            html.Div(id=DUMMY_OPTIMIZE_BUTTON_OUTPUT_ID)
        ])

])
