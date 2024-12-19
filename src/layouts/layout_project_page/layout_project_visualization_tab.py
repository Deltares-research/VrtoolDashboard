from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import dash_ag_grid as dag

from src.component_ids import PROJECT_PAGE_VISUALIZATION_COST_GRAPH, PROJECT_PAGE_VISUALIZATION_RELIABILITY_GRAPH, \
    OVERVIEW_PROJECT_MAP_ID, PROJECT_OVERVIEW_TABLE_DISPLAY, TOTAL_AREA_COST, TOTAL_AREA_RISK_TABLE
from src.layouts.layout_traject_page.layout_radio_items import layout_radio_result_type_project_page
from src.linear_objects.project import DikeProject
from src.plotly_graphs.pf_length_cost import plot_default_scatter_dummy
from src.plotly_graphs.plotly_maps import plot_default_overview_map_dummy
import pandas as pd

max_length = 100

elements = [
]

rows = [
    dmc.TableTr(
        [
            dmc.TableTd(element["project"]),
            dmc.TableTd(element["nb_sections"]),
            dmc.TableTd(element["start_year"]),
            dmc.TableTd(element["end_year"]),
            dmc.TableTd(element["length"]),
            dmc.TableTd(element["project_full_cost"]),
            dmc.TableTd(element["project_reliability_before_reinforcement"]),
            dmc.TableTd(element["project_reliability_after_reinforcement"]),
        ]
    )
    for element in elements
]

head = dmc.TableThead(
    dmc.TableTr(
        [
            dmc.TableTh("Project"),
            dmc.TableTh("Aantal vakken"),
            dmc.TableTh("Startjaar"),
            dmc.TableTh("Eindjaar"),
            dmc.TableTh("Lengte (km)"),
            dmc.TableTh("Kosten (M€)"),
            dmc.TableTh("Faalkans beoordeling"),
            dmc.TableTh("Faalkans na versterking"),

        ],

    )
)
body = dmc.TableTbody(rows)
caption = dmc.TableCaption(" ")


def fill_project_display_overview_table(projects: list[DikeProject]):
    elements_updated = [
        {"project": project.name,
         "nb_sections": len(project.dike_sections),
         "start_year": project.start_year,
         "end_year": project.end_year,
         "length": f"{project.total_length / 1e3:.2f}",  # km
         "project_full_cost": f"{project.calc_project_cost() / 1e6:.2f}",  # M€
         "project_reliability_before_reinforcement": "{:.2e}".format(project.project_failure_prob_assessement),
         "project_reliability_after_reinforcement": "{:.2e}".format(project.project_failure_prob_after_reinforcement),
         }
        for project in projects
    ]
    rows_updated = [
        dmc.TableTr(
            [
                dmc.TableTd(element["project"]),
                dmc.TableTd(element["nb_sections"]),
                dmc.TableTd(element["start_year"]),
                dmc.TableTd(element["end_year"]),
                dmc.TableTd(element["length"]),
                dmc.TableTd(element["project_full_cost"]),
                dmc.TableTd(element["project_reliability_before_reinforcement"]),
                dmc.TableTd(element["project_reliability_after_reinforcement"]),
            ]
        )
        for element in elements_updated
    ]
    body_updated = dmc.TableTbody(rows_updated)

    return [dmc.Table(children=[head, body_updated, caption],
                      withTableBorder=True,
                      withColumnBorders=True,
                      highlightOnHover=True,
                      horizontalSpacing=10,
                      )]


def get_risk_table():
    """Get Ag Grid table for the risk display (current situation and after reinforcement)"""

    df = pd.DataFrame([])
    columnDefs = [
        {"field": "year", 'headerName': 'Jaar', "pinned": True, 'width': 80},
        {
            'headerName': 'Risico (M€)',
            'children': [

                {'field': "current_risk", 'headerName': 'Huidige', "width": 100,
                 },

                {
                    "field": "program_risk", "headerName": "Programma", "width": 120,
                }

            ]
        }
    ]

    risk_table = dag.AgGrid(
        id=TOTAL_AREA_RISK_TABLE,
        rowData=df.to_dict("records"),
        defaultColDef={
            "wrapHeaderText": True,
            "autoHeaderHeight": True,
        },
        columnDefs=columnDefs,
        # columnSize="sizeToFit",
        dashGridOptions={"animateRows": False},
        style={'height': "100%"},
    )
    return risk_table


def left_side_area_stats():
    return html.Div(
        id="quick-stats",
        className="row",
        children=[
            html.Div(
                id="card-1",
                children=[
                    dmc.Center(style={"width": "100%"},
                               children=[
                                   dmc.SimpleGrid(
                                       cols=1,
                                       spacing="md",
                                       verticalSpacing="md",
                                       children=[
                                           html.P(""),
                                           dmc.Text("Totale versterkingskosten:", td="underline"),
                                           dmc.Text("", id=TOTAL_AREA_COST, fw=700, size="xl"),
                                           # add white vertical space
                                           html.P(""),
                                           html.P(""),
                                       ]
                                   ),

                               ]),
                    html.Div(
                        [get_risk_table()],
                        style={"height": "220px"}  # Set container height to ensure the grid is displayed
                    )


                ],

            ),

        ],
    )


cost_chart = dcc.Graph(id=PROJECT_PAGE_VISUALIZATION_COST_GRAPH, figure=plot_default_scatter_dummy(),
                       style={'width': '100%', 'height': '100%'}, )

reliability_chart_box = html.Div(children=[
    layout_radio_result_type_project_page,
    dcc.Graph(id=PROJECT_PAGE_VISUALIZATION_RELIABILITY_GRAPH, figure=plot_default_scatter_dummy(),
              style={'width': 800, 'height': 400})

])

map_overview_area = dcc.Graph(
    id=OVERVIEW_PROJECT_MAP_ID,
    figure=plot_default_overview_map_dummy(),
    style={"width": "100%", "height": "100%"},
)

table = html.Div(id=PROJECT_OVERVIEW_TABLE_DISPLAY, children=[dmc.Table([head, body, caption])])

right_side_visualization = html.Div(
    id="project_page_visualization__",
    children=[
        dbc.Row(children=[

            dbc.Col(children=[
                dbc.Row(map_overview_area),
                dbc.Row(table),

            ], md=7),
            dbc.Col(children=[
                dbc.Row(cost_chart),
                dbc.Row(reliability_chart_box),
            ], md=5),

        ])

    ]
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
