from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

from src.component_ids import PROJECT_PAGE_VISUALIZATION_COST_GRAPH, PROJECT_PAGE_VISUALIZATION_RELIABILITY_GRAPH, \
    OVERVIEW_PROJECT_MAP_ID, PROJECT_OVERVIEW_TABLE_DISPLAY
from src.layouts.layout_traject_page.layout_radio_items import layout_radio_result_type_project_page
from src.linear_objects.project import DikeProject
from src.plotly_graphs.pf_length_cost import plot_default_scatter_dummy
from src.plotly_graphs.plotly_maps import plot_default_overview_map_dummy

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
            dmc.TableTh("Dijkvakken"),
            dmc.TableTh("Start jaar"),
            dmc.TableTh("Eind jaar"),
            dmc.TableTh("Lengte (km)"),
            dmc.TableTh("Beoordeling \n faalkans"),
            dmc.TableTh("Versterking faalkans"),

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


def left_side_area_stats():
    return html.Div(
        id="quick-stats",
        className="row",
        children=[
            html.Div(
                id="card-1",
                children=[
                    html.P("Area stats"),

                ],
            ),
            html.Div(
                id="card-2",
                children=[
                    html.P("Total cost:"),

                ],
            ),

        ],
    )


cost_chart = dcc.Graph(id=PROJECT_PAGE_VISUALIZATION_COST_GRAPH, figure=plot_default_scatter_dummy(),
                       style={'width': '100%', 'height': '100%'}, )

reliability_chart_box = html.Div(children=[
    layout_radio_result_type_project_page,
    dcc.Graph(id=PROJECT_PAGE_VISUALIZATION_RELIABILITY_GRAPH, figure=plot_default_scatter_dummy(),
              style={'width': '100%', 'height': '100%'})

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
        dbc.Row([
            dbc.Col(table, md=7, style={"height": "100%"}),
            dbc.Col(map_overview_area, md=5, style={"height": "100%"}),
        ], className="h-60"),

        dbc.Row([
            dbc.Col(cost_chart, md=5, style={"height": "100%"}),
            dbc.Col(reliability_chart_box, md=7, style={"height": "100%"}),
        ], className="h-40"),
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
