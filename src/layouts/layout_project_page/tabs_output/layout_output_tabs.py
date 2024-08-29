from dash import html, dcc
import dash_bootstrap_components as dbc

from src.component_ids import OVERVIEW_PROJECT_MAP_ID, RUNS_COMPARISON_GRAPH_ID, RUNS_COMPARISON_GRAPH_TIME_ID, \
    PROJECT_COMPARISON_GRAPH_TIME_VS_COST_ID
from src.layouts.layout_traject_page.layout_radio_items import layout_radio_cost_beta_switch
from src.layouts.layout_traject_page.layout_sliders import layout_year_slider
from src.plotly_graphs.pf_length_cost import plot_default_scatter_dummy


def layout_project_output_tab_one() -> html.Div:
    return html.Div(
        children=[
            dbc.Row([
                dbc.Col([html.H2("Overzicht Gebied")], md=10),
            ]),

            html.Div(id=OVERVIEW_PROJECT_MAP_ID,
                     style={'width': '90vh', 'height': '60vh', 'border': "2px solid black"}),

        ])


def layout_project_output_tab_two() -> html.Div:
    return html.Div(
        children=[
            dbc.Row([
                dbc.Col([html.H2("Tijd vs Kosten")], md=10),
            ]),
            layout_radio_cost_beta_switch,

            html.Div(
                style={'width': '90vh', 'height': '60vh', 'border': "2px solid black"},
                children=[
                    dcc.Graph(id=PROJECT_COMPARISON_GRAPH_TIME_VS_COST_ID, figure=plot_default_scatter_dummy(),
                              style={'width': '100%', 'height': '100%'}, ),
                    # dcc.Store(id="store_clicked_section", data='all')
                ],

            ),
        ])
