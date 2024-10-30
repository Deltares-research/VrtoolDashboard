from dash import html, dcc
import dash_bootstrap_components as dbc

from src.component_ids import OVERVIEW_COMPARISON_MAP_ID, RUNS_COMPARISON_GRAPH_ID, RUNS_COMPARISON_GRAPH_TIME_ID, \
    MEASURE_COMPARISON_MAP_ID
from src.layouts.layout_comparison_page.layout_table_comparison import table_ag_grid_comparison_measures
from src.layouts.layout_traject_page.layout_radio_items import layout_radio_result_type_comparison_page
from src.layouts.layout_traject_page.layout_sliders import layout_year_slider
from src.plotly_graphs.pf_length_cost import plot_default_scatter_dummy
from src.plotly_graphs.plotly_maps import plot_default_overview_map_dummy


# TODO: functions below should be renamed layout_comparison_output_tab_one ...

def layout_project_output_tab_one() -> html.Div:
    return html.Div(
        children=[
            dbc.Row([
                dbc.Col([html.H2("Overzicht Projects")], md=10),
            ]),

            html.Div(id=OVERVIEW_COMPARISON_MAP_ID,
                     style={'width': '110vh', 'height': '80vh', 'border': "2px solid black"}),

        ])


def layout_project_output_tab_two() -> html.Div:
    return html.Div(
        children=[
            dbc.Row([
                dbc.Col([html.H2("Vergelijken kosten")], md=10),
            ]),
            layout_year_slider,
            html.Div(
                style={'width': '110vh', 'height': '55vh', 'border': "2px solid black"},
                children=[
                    layout_radio_result_type_comparison_page,
                    dcc.Graph(id=RUNS_COMPARISON_GRAPH_ID, figure=plot_default_scatter_dummy(),
                              style={'width': '100%', 'height': '100%'}, ),
                ],

            ),

        ])


def layout_project_output_tab_three() -> html.Div:
    return html.Div(
        children=[
            dbc.Row([
                dbc.Col([html.H2("Tijd ")], md=10),
            ]),

            html.Div(
                style={'width': '110vh', 'height': '70vh', 'border': "2px solid black"},
                children=[
                    dcc.Graph(id=RUNS_COMPARISON_GRAPH_TIME_ID, figure=plot_default_scatter_dummy(),
                              style={'width': '100%', 'height': '100%'}, ),
                ],

            ),

        ])


def layout_project_output_tab_four() -> html.Div:
    return html.Div(
        children=[
            dbc.Row([
                dbc.Col([html.H2("Maatregelen")], md=10),
            ]),

            html.Div(
                style={'width': '110vh', 'height': '70vh', 'border': "2px solid black"},
                children=[
                    dcc.Graph(id=MEASURE_COMPARISON_MAP_ID, figure=plot_default_overview_map_dummy(),
                              style={'width': '100%', 'height': '100%'}, ),
                ],

            ),

        ])


def layout_project_output_tab_five() -> html.Div:
    return html.Div(
        children=[

            table_ag_grid_comparison_measures,
        ])
