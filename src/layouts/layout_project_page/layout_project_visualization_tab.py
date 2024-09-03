from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_daq as daq
import dash_mantine_components as dmc

from src.component_ids import PROJECT_PAGE_VISUALIZATION_COST_GRAPH, PROJECT_PAGE_VISUALIZATION_RELIABILITY_GRAPH
from src.constants import get_mapbox_token
from src.plotly_graphs.pf_length_cost import plot_default_scatter_dummy
from src.plotly_graphs.plotly_maps import plot_default_overview_map_dummy

max_length = 100

elements = [
    {"position": 6, "mass": 12.011, "symbol": "C", "name": "Carbon"},
    {"position": 7, "mass": 14.007, "symbol": "N", "name": "Nitrogen"},
    {"position": 39, "mass": 88.906, "symbol": "Y", "name": "Yttrium"},
    {"position": 56, "mass": 137.33, "symbol": "Ba", "name": "Barium"},
    {"position": 58, "mass": 140.12, "symbol": "Ce", "name": "Cerium"},
]

rows = [
    dmc.TableTr(
        [
            dmc.TableTd(element["position"]),
            dmc.TableTd(element["name"]),
            dmc.TableTd(element["symbol"]),
            dmc.TableTd(element["mass"]),
        ]
    )
    for element in elements
]

head = dmc.TableThead(
    dmc.TableTr(
        [
            dmc.TableTh("Element Position"),
            dmc.TableTh("Element Name"),
            dmc.TableTh("Symbol"),
            dmc.TableTh("Atomic Mass"),
        ]
    )
)
body = dmc.TableTbody(rows)
caption = dmc.TableCaption("Some elements from periodic table")


def left_side_area_stats():
    return html.Div(
        id="quick-stats",
        className="row",
        children=[
            html.Div(
                id="card-1",
                children=[
                    html.P("Operator ID"),
                    daq.LEDDisplay(
                        id="operator-led",
                        value="1704",
                        color="#92e0d3",
                        backgroundColor="#1e2130",
                        size=50,
                    ),
                ],
            ),
            html.Div(
                id="card-2",
                children=[
                    html.P("Time to completion"),
                    daq.Gauge(
                        id="progress-gauge",
                        max=max_length * 2,
                        min=0,
                        showCurrentValue=True,  # default size 200 pixel
                    ),
                ],
            ),
            html.Div(
                id="utility-card",
                children=[daq.StopButton(id="stop-button", size=160, n_clicks=0)],
            ),
        ],
    )


def generate_piechart():
    return dcc.Graph(
        id="piechart",
        figure={
            "data": [
                {
                    "labels": [1, 1, 1],
                    "values": [3, 3, 3],
                    "type": "pie",
                    "marker": {"line": {"color": "white", "width": 1}},
                    "hoverinfo": "label",
                    "textinfo": "label",
                }
            ],
            "layout": {
                "margin": dict(l=20, r=20, t=20, b=20),
                "showlegend": True,
                "paper_bgcolor": "rgba(0,0,0,0)",
                "plot_bgcolor": "rgba(0,0,0,0)",
                "font": {"color": "white"},
                "autosize": True,
            },
        },
    )





cost_chart = dcc.Graph(id=PROJECT_PAGE_VISUALIZATION_COST_GRAPH, figure=plot_default_scatter_dummy(),
                       style={'width': '100%', 'height': '100%'}, )

reliability_chart = dcc.Graph(id=PROJECT_PAGE_VISUALIZATION_RELIABILITY_GRAPH, figure=plot_default_scatter_dummy(),
                              style={'width': '100%', 'height': '100%'}, )

map_overview_area = dcc.Graph(
        figure=plot_default_overview_map_dummy(),
        style={"width": "100%", "height": "100%"},
        config={"mapboxAccessToken": get_mapbox_token()},
    )

table = dmc.Table([head, body, caption])
right_side_visualization = html.Div(
    id="project_page_visualization__",
    children=[
        dbc.Row([
            dbc.Col(table, md=7),
            dbc.Col(map_overview_area, md=5),
        ]),

        dbc.Row([
            dbc.Col(cost_chart, md=5),
            dbc.Col(reliability_chart, md=7),
        ]),
    ],
)

project_visualization_tab_layout = html.Div(
    id="status-container",
    children=[
        dbc.Row(
            [
                dbc.Col(left_side_area_stats(), md=2),
                dbc.Col(right_side_visualization, md=10),
            ],
        ),

    ],

)
