from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dash_table import DataTable

from src.component_ids import OPTIMIZE_BUTTON_ID, DUMMY_OPTIMIZE_BUTTON_OUTPUT_ID, EDITABLE_TRAJECT_TABLE_ID, \
    NAME_NEW_OPTIMIZATION_RUN_ID
from src.constants import Measures, MeasuresTable

dike_vr_optimization_layout = html.Div([

    DataTable(id=EDITABLE_TRAJECT_TABLE_ID,
              columns=(
                  [{'id': 'section_col', 'name': 'Dijkvak'},
                   {'id': 'reinforcement_col', 'name': 'Versterking', 'presentation': 'dropdown'},
                   {'id': MeasuresTable.GROUND_IMPROVEMENT.name, 'name': MeasuresTable.GROUND_IMPROVEMENT.value,
                    'presentation': 'dropdown'},
                   {'id': MeasuresTable.GROUND_IMPROVEMENT_WITH_STABILITY_SCREEN.name,
                    'name': MeasuresTable.GROUND_IMPROVEMENT_WITH_STABILITY_SCREEN.value,
                    'presentation': 'dropdown'},
                   {'id': MeasuresTable.GEOTEXTILE.name, 'name': MeasuresTable.GEOTEXTILE.value,
                    'presentation': 'dropdown'},
                   {'id': MeasuresTable.DIAPHRAGM_WALL.name, 'name': MeasuresTable.DIAPHRAGM_WALL.value,
                    'presentation': 'dropdown'},
                   {'id': MeasuresTable.STABILITY_SCREEN.name, 'name': MeasuresTable.STABILITY_SCREEN.value,
                    'presentation': 'dropdown'},

                   {'id': 'reference_year_col', 'name': 'Referentiejaar'},
                   ]
              ),
              data=[],
              dropdown={
                  'reinforcement_col': {
                      'options': [{'label': 'Aan', 'value': "yes"}, {'label': 'Uit', 'value': "no"}]},
                  MeasuresTable.GROUND_IMPROVEMENT.name: {
                      'options': [{'label': meas.value, 'value': meas.name} for meas in Measures]},
                  MeasuresTable.GROUND_IMPROVEMENT_WITH_STABILITY_SCREEN.name: {
                      'options': [{'label': meas.value, 'value': meas.name} for meas in Measures]},
                  MeasuresTable.GEOTEXTILE.name: {
                      'options': [{'label': meas.value, 'value': meas.name} for meas in Measures]},
                  MeasuresTable.DIAPHRAGM_WALL.name: {
                      'options': [{'label': meas.value, 'value': meas.name} for meas in Measures]},
                  MeasuresTable.STABILITY_SCREEN.name: {
                      'options': [{'label': meas.value, 'value': meas.name} for meas in Measures]},

              },
              style_cell={'textAlign': 'left', 'whiteSpace': "pre-line"},
              editable=True,
              # fixed_rows={'headers': True},  # either fix row with risk of overlap or have a slider
              style_table={'overflowX': 'scroll',
                           'overflowY': 'scroll'},

              ),

    html.Div(
        [
            dbc.Input(id=NAME_NEW_OPTIMIZATION_RUN_ID, placeholder="Optimization run naam", type="text"),
            dbc.Button("Optimize", id=OPTIMIZE_BUTTON_ID, color="primary", className="mr-1"),
            dbc.Tooltip("Click to call VRCore optimization routine via the new calculation constraints.",
                        target=OPTIMIZE_BUTTON_ID),
            html.Div(id=DUMMY_OPTIMIZE_BUTTON_OUTPUT_ID)
        ])

])
