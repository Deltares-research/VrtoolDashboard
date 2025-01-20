import dash
from dash import html, Output, Input, callback, State, dcc, Patch

from src.component_ids import TABS_SWITCH_VISUALIZATION_COMPARISON_PAGE, CONTENT_TABS_COMPARISON_PAGE_ID, \
    STORED_RUNS_COMPARISONS_DATA, RUNS_COMPARISON_GRAPH_TIME_ID, \
    SLIDER_YEAR_RELIABILITY_RESULTS_ID, OVERVIEW_COMPARISON_MAP_ID, RUNS_COMPARISON_GRAPH_ID, \
    RADIO_COMPARISON_PAGE_RESULT_TYPE, MEASURE_COMPARISON_MAP_ID, EDITABLE_COMPARISON_TABLE_ID, \
    TABLE_COMPARISON_MEASURES, TABLE_ORDER_COMPARISON_MEASURES
from src.layouts.layout_comparison_page.layout_output_tabs import layout_project_output_tab_one, \
    layout_project_output_tab_two, layout_project_output_tab_three, layout_project_output_tab_four, \
    layout_project_output_tab_five, layout_project_output_tab_six
from src.linear_objects.dike_traject import DikeTraject
from src.plotly_graphs.comparison_page.plot_measures_comparison_map import plot_comparison_measures_map

from src.plotly_graphs.pf_length_cost import plot_default_scatter_dummy
from src.plotly_graphs.plotly_maps import plot_default_overview_map_dummy
from src.plotly_graphs.project_page.pf_traject_comparison import plot_pf_project_comparison, \
    plot_pf_time_runs_comparison
from src.plotly_graphs.project_page.plotly_maps import plot_comparison_runs_overview_map_simple


@callback(

    Output(CONTENT_TABS_COMPARISON_PAGE_ID, "children"),

    [Input(TABS_SWITCH_VISUALIZATION_COMPARISON_PAGE, "active_tab")],
)
def render_project_overview_map_content(active_tab: str) -> html.Div:
    """
    Renders the content of the selected tab for the general overview page.
    :param active_tab:
    :return:
    """

    if active_tab == "tab-11111":
        return layout_project_output_tab_one()

    elif active_tab == "tab-11112":
        return layout_project_output_tab_two()

    elif active_tab == "tab-11113":
        return layout_project_output_tab_three()

    elif active_tab == "tab-11114":
        return layout_project_output_tab_four()

    elif active_tab == "tab-11115":
        return layout_project_output_tab_five()

    elif active_tab == "tab-11116":
        return layout_project_output_tab_six()

    else:
        return html.Div("Invalid tab selected")


@callback(Output(OVERVIEW_COMPARISON_MAP_ID, "children"),
          [Input(STORED_RUNS_COMPARISONS_DATA, "data"),
           # Input("tabs_tab_project_page", "active_tab")
           ])
def make_graph_overview_comparison(imported_runs_data: dict) -> dcc.Graph:
    """
    IS THIS CALLBACK DEPRECATED?
    Call to display the graph of the overview map of the dike from the saved imported dike data.

    :param dike_traject_data: The data of the dike traject to be displayed.
    """
    if imported_runs_data is None or imported_runs_data == {}:
        _fig = plot_default_overview_map_dummy()
    else:
        trajects = [DikeTraject.deserialize(imported_runs_data[run_name]) for run_name in imported_runs_data.keys()]
        _fig = plot_comparison_runs_overview_map_simple(trajects, [])
    return dcc.Graph(
        figure=_fig,
        style={"width": "100%", "height": "100%"},
    )


@callback(
    Output(RUNS_COMPARISON_GRAPH_ID, "figure"),
    [
        Input(STORED_RUNS_COMPARISONS_DATA, "data"),
        Input(SLIDER_YEAR_RELIABILITY_RESULTS_ID, "value"),
        Input(RADIO_COMPARISON_PAGE_RESULT_TYPE, "value")
    ],
)
def make_graph_pf_project_comparison(
        project_data: dict,
        selected_year: float,
        result_type: str
):
    """

    """
    if project_data is None:
        return plot_default_scatter_dummy()
    else:
        _fig = plot_pf_project_comparison(project_data, selected_year, result_type)
    return _fig


@callback(
    Output(RUNS_COMPARISON_GRAPH_TIME_ID, "figure"),
    [
        Input(STORED_RUNS_COMPARISONS_DATA, "data"),
    ],
)
def make_graph_pf_time_comparison(
        project_data: dict,
):
    """

    """
    if project_data is None:
        return plot_default_scatter_dummy()
    else:
        _fig = plot_pf_time_runs_comparison(project_data)
    return _fig


@callback(
    Output(MEASURE_COMPARISON_MAP_ID, "figure"),
    [
        Input(STORED_RUNS_COMPARISONS_DATA, "data"),
        Input(EDITABLE_COMPARISON_TABLE_ID, "rowData"),
        Input(EDITABLE_COMPARISON_TABLE_ID, "cellValueChanged")

    ],
)
def make_map_comparison_measure(imported_runs: dict, table_imported_runs_data: list[dict], dummy: dict):
    if imported_runs is None:
        return plot_default_overview_map_dummy()

    id_1, id_2 = get_ids_activated_runs(table_imported_runs_data)

    if id_1 is None or id_2 is None:
        return dash.no_update

    dike_traject_1 = DikeTraject.deserialize(list(imported_runs.values())[id_1])
    dike_traject_2 = DikeTraject.deserialize(list(imported_runs.values())[id_2])
    activated_runs = [dike_traject_1, dike_traject_2]

    _fig = plot_comparison_measures_map(imported_runs, activated_runs)
    return _fig


@callback(
    Output(TABLE_COMPARISON_MEASURES, "rowData"),
    Output(TABLE_COMPARISON_MEASURES, "columnDefs"),
    [
        State(STORED_RUNS_COMPARISONS_DATA, "data"),
        Input(EDITABLE_COMPARISON_TABLE_ID, "rowData"),
        Input(EDITABLE_COMPARISON_TABLE_ID, "cellValueChanged")
    ],
)
def update_table_comparison_measures(imported_runs: dict, table_imported_runs_data: list[dict], dummy: dict):
    """

    Args:
        imported_runs:
        table_imported_runs_data:
        dummy: KEEP THIS ONE, otherwise the callback does not trigger when editing the table

    Returns:

    """
    if imported_runs is None or len(imported_runs) < 2:
        return dash.no_update, dash.no_update

    # Initialize variables
    id_1, id_2 = get_ids_activated_runs(table_imported_runs_data)

    if id_1 is None or id_2 is None:
        return dash.no_update, dash.no_update

    dike_traject_1 = DikeTraject.deserialize(list(imported_runs.values())[id_1])
    dike_traject_2 = DikeTraject.deserialize(list(imported_runs.values())[id_2])
    data = []
    for section_1, section_2 in zip(dike_traject_1.dike_sections, dike_traject_2.dike_sections):
        data.append({
            "section_name": section_1.name,
            "section_length": section_1.length,
            "run_1_measure": ", ".join(section_1.final_measure_veiligheidsrendement.get('type', ["Geen maatregel"])),
            "run_1_dberm": section_1.final_measure_veiligheidsrendement.get('dberm'),
            "run_1_dcrest": section_1.final_measure_veiligheidsrendement.get('dcrest'),
            "run_1_Lscreen": section_1.final_measure_veiligheidsrendement.get('L_stab_screen'),
            "run_1_cost": round(section_1.final_measure_veiligheidsrendement.get('LCC') / 1e6, 2),
            "run_2_measure": ", ".join(section_2.final_measure_veiligheidsrendement.get('type', ["Geen maatregel"])),
            "run_2_dberm": section_2.final_measure_veiligheidsrendement.get('dberm'),
            "run_2_dcrest": section_2.final_measure_veiligheidsrendement.get('dcrest'),
            "run_2_Lscreen": section_2.final_measure_veiligheidsrendement.get('L_stab_screen'),
            "run_2_cost": round(section_2.final_measure_veiligheidsrendement.get('LCC') / 1e6, 2),
        })

    patched_grid = Patch()
    patched_grid[2]["headerName"] = f"{dike_traject_1.name}|{dike_traject_1.run_name}"
    patched_grid[3]["headerName"] = f"{dike_traject_2.name}|{dike_traject_2.run_name}"

    return data, patched_grid


@callback(
    Output(TABLE_ORDER_COMPARISON_MEASURES, "rowData"),
    Output(TABLE_ORDER_COMPARISON_MEASURES, "columnDefs"),
    [
        State(STORED_RUNS_COMPARISONS_DATA, "data"),
        Input(EDITABLE_COMPARISON_TABLE_ID, "rowData"),
        Input(EDITABLE_COMPARISON_TABLE_ID, "cellValueChanged")
    ],
)
def update_table_comparison_order_measures(imported_runs: dict, table_imported_runs_data: list[dict], dummy: dict):
    """

    Args:
        imported_runs:
        table_imported_runs_data:
        dummy: KEEP THIS ONE, otherwise the callback does not trigger when editing the table

    Returns:

    """
    if imported_runs is None or len(imported_runs) < 2:
        return dash.no_update, dash.no_update

    # Initialize variables
    id_1, id_2 = None, None

    # Iterate through the data to find the first two active items
    for i, item in enumerate(table_imported_runs_data):
        if item.get('active'):
            if id_1 is None:
                id_1 = i
            elif id_2 is None:
                id_2 = i
                break  # Exit loop once both IDs are found

    if id_1 is None or id_2 is None:
        return dash.no_update, dash.no_update

    dike_traject_1 = DikeTraject.deserialize(list(imported_runs.values())[id_1])
    dike_traject_2 = DikeTraject.deserialize(list(imported_runs.values())[id_2])
    data = []

    for section_1, section_2 in zip(dike_traject_1.get_sections_in_reinforcement_order(),
                                    dike_traject_2.get_sections_in_reinforcement_order()):
        data.append({

            "run_1_section_name": section_1.name,
            "run_1_measure": ", ".join(section_1.final_measure_veiligheidsrendement.get('type', ["Geen maatregel"])),
            "run_2_section_name": section_2.name,
            "run_2_measure": ", ".join(section_2.final_measure_veiligheidsrendement.get('type', ["Geen maatregel"])),

        })

    patched_grid = Patch()
    patched_grid[0]["headerName"] = f"{dike_traject_1.name}|{dike_traject_1.run_name}"
    patched_grid[1]["headerName"] = f"{dike_traject_2.name}|{dike_traject_2.run_name}"

    return data, patched_grid


def get_ids_activated_runs(table_imported_runs_data: list[dict]) -> tuple[int, int]:
    id_1, id_2 = None, None

    # Iterate through the data to find the first two active items
    for i, item in enumerate(table_imported_runs_data):
        if item.get('active'):
            if id_1 is None:
                id_1 = i
            elif id_2 is None:
                id_2 = i
                break  # Exit loop once both IDs are found
    return id_1, id_2
