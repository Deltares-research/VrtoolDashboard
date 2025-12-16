from dash import Input, Output, State, callback, dash

from src.component_ids import (
    ADD_PROJECT_BUTTON_ID,
    ALERT_PROJECT_CREATION_ID,
    EDITABLE_IMPORTED_RUNS_TABLE_ID,
    MULTI_SELECT_SECTION_FOR_PROJECT_ID,
    OVERVIEW_PROJECT_MAP_ID_2,
    PROGRAM_SELECTION_MAP_RADIO_SWITCH_ID,
    PROJECT_END_YEAR_INPUT_FIELD_ID,
    PROJECT_NAME_INPUT_FIELD_ID,
    PROJECT_START_YEAR_INPUT_FIELD_ID,
    STORED_IMPORTED_RUNS_DATA,
    STORED_PROJECT_OVERVIEW_DATA,
    TABLE_PROJECT_SUMMARY_ID,
    UPDATE_PROJECT_BUTTON_ID,
)
from src.constants import ProgramDefinitionMapType
from src.linear_objects.dike_traject import DikeTraject
from src.linear_objects.reinforcement_program import get_projects_from_saved_data
from src.plotly_graphs.plotly_maps import plot_default_overview_map_dummy
from src.plotly_graphs.project_page.plotly_maps import (
    plot_comparison_runs_overview_map_assessment,
    plot_comparison_runs_overview_map_projects,
    plot_comparison_runs_overview_map_simple,
    plot_order_reinforcement_index_map,
    plot_project_overview_map,
)


@callback(
    Output(MULTI_SELECT_SECTION_FOR_PROJECT_ID, "data"),
    Input(EDITABLE_IMPORTED_RUNS_TABLE_ID, "rowData"),
    State(STORED_IMPORTED_RUNS_DATA, "data"),
)
def get_multiselect_options(table_data: list[dict], project_data: dict) -> list[dict]:
    """
    Get the options for the multi select dropdown based on the stored runs data.

    :param table_data:
    :param project_data:
    :return:
    """
    data = []

    for dike_traject_data in project_data.values():
        dike_traject = DikeTraject.deserialize(dike_traject_data)

        if dike_traject.name in [group["group"] for group in data]:
            continue
        group_dict = {"group": dike_traject.name, "items": []}
        for section in dike_traject.dike_sections:
            group_dict["items"].append(
                {"label": section.name, "value": section.name + "|" + dike_traject.name}
            )
        data.append(group_dict)
    return data


@callback(
    Output(ALERT_PROJECT_CREATION_ID, "is_open"),
    Output(ALERT_PROJECT_CREATION_ID, "children"),
    Output(STORED_PROJECT_OVERVIEW_DATA, "data"),
    Input(ADD_PROJECT_BUTTON_ID, "n_clicks"),
    State(MULTI_SELECT_SECTION_FOR_PROJECT_ID, "value"),
    State(PROJECT_NAME_INPUT_FIELD_ID, "value"),
    State(PROJECT_START_YEAR_INPUT_FIELD_ID, "value"),
    State(PROJECT_END_YEAR_INPUT_FIELD_ID, "value"),
    State(STORED_PROJECT_OVERVIEW_DATA, "data"),
)
def create_and_store_project(
    n_clicks: int,
    multi_select_value: list[str],
    project_name: str,
    start_year: int,
    end_year: int,
    stored_project_data: list,
) -> tuple:
    """
    Create a project based on the project name with the selected sections and year.
    :param n_clicks: nb of clicks of the button "Add Project"
    :param multi_select_value: selected sections
    :param project_name: name of the project
    :param year: year of the project
    :param stored_project_data: list of stored projects
    :return

    """
    if stored_project_data is None:
        stored_project_data = []

    if n_clicks is None:
        return dash.no_update, dash.no_update, dash.no_update

    if project_name is None or project_name == "":
        return dash.no_update, "Project naam mag niet leeg zijn.", dash.no_update

    if len(multi_select_value) == 0:
        return dash.no_update, dash.no_update, dash.no_update

    if start_year is None or start_year == "" or end_year is None or end_year == "":
        return dash.no_update, "Jaar mag niet leeg zijn.", dash.no_update

    if start_year > end_year:
        return (
            dash.no_update,
            "Start jaar mag niet groter zijn dan eind jaar.",
            dash.no_update,
        )

    # Do nothing update if the name of the project is already in the table
    for project in stored_project_data:
        if project["project"] == project_name:
            return True, f"Project {project_name} bestaat al.", dash.no_update

    for project in stored_project_data:
        for section in project["sections"]:
            if section in multi_select_value:
                return (
                    True,
                    f"Section {section} is already in project {project['project']}",
                    dash.no_update,
                )

    stored_project_data.append(
        {
            "project": project_name,
            "sections": multi_select_value,  # not displayed in the table but is kept in memory
            "section_number": len(multi_select_value),
            "start_year": start_year,
            "end_year": end_year,
            "length": 0.0,
        }
    )

    return False, dash.no_update, stored_project_data


@callback(
    Output(TABLE_PROJECT_SUMMARY_ID, "rowData"),
    Input(STORED_PROJECT_OVERVIEW_DATA, "data"),
    Input("tabs_tab_project_page", "active_tab"),
)
def fill_project_overview_table(stored_project_data: list, dummy) -> list[dict]:
    """
    Fill the overview table with the project data saved in the stored_project_data.
    :param stored_project_data:
    :param dummy:
    :return:
    """
    if stored_project_data is None:
        return dash.no_update

    output_list = []
    for project in stored_project_data:
        output_list.append(
            {
                "project": project["project"],
                "section_number": project["section_number"],
                "start_year": project["start_year"],
                "end_year": project["end_year"],
            }
        )
    return output_list


@callback(
    Output(ALERT_PROJECT_CREATION_ID, "is_open", allow_duplicate=True),
    Output(ALERT_PROJECT_CREATION_ID, "children", allow_duplicate=True),
    Output(STORED_PROJECT_OVERVIEW_DATA, "data", allow_duplicate=True),
    Input(UPDATE_PROJECT_BUTTON_ID, "n_clicks"),
    State(MULTI_SELECT_SECTION_FOR_PROJECT_ID, "value"),
    State(PROJECT_NAME_INPUT_FIELD_ID, "value"),
    State(PROJECT_START_YEAR_INPUT_FIELD_ID, "value"),
    State(PROJECT_END_YEAR_INPUT_FIELD_ID, "value"),
    State(STORED_PROJECT_OVERVIEW_DATA, "data"),
    allow_duplicate=True,
    prevent_initial_call=True,
)
def update_stored_project(
    n_clicks: int,
    multi_select_value: list[str],
    project_name: str,
    start_year: int,
    end_year: int,
    stored_project_data: list,
) -> tuple:
    """
    Update a project based on the project name with the newly selected sections and/or year.
    :param n_clicks: nb of clicks of the button "Update Project"
    :param project_data:
    :param multi_select_value:
    :param project_name:
    :param year:
    :param current_table_row:
    :return:
    """
    if stored_project_data is None:
        return dash.no_update, dash.no_update, dash.no_update

    list_to_return = []
    for project in stored_project_data:
        if project["project"] == project_name:
            list_to_return.append(
                {
                    "project": project_name,
                    "sections": multi_select_value,  # not displayed in the table but is kept in memory
                    "section_number": len(multi_select_value),
                    "start_year": start_year,
                    "end_year": end_year,
                    "length": 0.0,
                }
            )

            continue  # Skip the validity check of the sections for the project to update
        list_to_return.append(project)

        # Check if the sections are not already in another project, if so, return an error message
        for section in project["sections"]:
            if section in multi_select_value:
                return (
                    True,
                    f"Section {section} is already in project {project['project']}",
                    dash.no_update,
                )

    return False, dash.no_update, list_to_return


@callback(
    Output(ALERT_PROJECT_CREATION_ID, "is_open", allow_duplicate=True),
    Output(ALERT_PROJECT_CREATION_ID, "children", allow_duplicate=True),
    Output(STORED_PROJECT_OVERVIEW_DATA, "data", allow_duplicate=True),
    Input("delete_project_button", "n_clicks"),
    State(PROJECT_NAME_INPUT_FIELD_ID, "value"),
    State(STORED_PROJECT_OVERVIEW_DATA, "data"),
    allow_duplicate=True,
    prevent_initial_call=True,
)
def delete_project(
    n_clicks: int, project_name: str, stored_project_data: list
) -> tuple:
    """
    Delete a project based on the project name.
    :param n_clicks:
    :param project_name:
    :param stored_project_data:
    :return:
    """
    if stored_project_data is None:
        return dash.no_update, dash.no_update, dash.no_update

    list_to_return = []
    switch = False
    for project in stored_project_data:
        if project["project"] == project_name:
            switch = True
            continue
        list_to_return.append(project)

    if not switch:
        return True, f"Project {project_name} bestaat niet.", dash.no_update
    return False, dash.no_update, list_to_return


@callback(
    Output(MULTI_SELECT_SECTION_FOR_PROJECT_ID, "value"),
    Output(PROJECT_NAME_INPUT_FIELD_ID, "value"),
    Output(PROJECT_START_YEAR_INPUT_FIELD_ID, "value"),
    Output(PROJECT_END_YEAR_INPUT_FIELD_ID, "value"),
    Input(TABLE_PROJECT_SUMMARY_ID, "selectedRows"),
    State(STORED_PROJECT_OVERVIEW_DATA, "data"),
)
def update_section_selection_on_click_event(
    selected_row: dict, project_data_overview
) -> tuple[list[str], str, int, int]:
    """
    Update the selected sections in the multi select dropdown when a row is selected in the project overview table.
    :param selected_row:
    :param project_data_overview:
    :return:
    """
    if selected_row is None:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    if not selected_row:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    selected_project_name = selected_row[0]["project"]
    for project in project_data_overview:
        if project["project"] == selected_project_name:
            return (
                project["sections"],
                selected_project_name,
                project["start_year"],
                project["end_year"],
            )
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update


@callback(
    Output(OVERVIEW_PROJECT_MAP_ID_2, "figure"),
    [
        Input("tabs_tab_project_page", "value"),
        # Input(TABLE_PROJECT_SUMMARY_ID, "selectedRows"),
        Input(MULTI_SELECT_SECTION_FOR_PROJECT_ID, "value"),
        Input(PROGRAM_SELECTION_MAP_RADIO_SWITCH_ID, "value"),
        Input(STORED_IMPORTED_RUNS_DATA, "data"),
        State(STORED_PROJECT_OVERVIEW_DATA, "data"),
    ],
)
def update_map_project_definition_page(
    dummy,
    selected_sections: list,
    switch_type_map: str,
    imported_runs_data: dict,
    project_overview_data: list,
):
    if imported_runs_data is None:
        return dash.no_update

    projects, trajects = get_projects_from_saved_data(
        imported_runs_data, project_overview_data, calc_failure_pro=False
    )

    if switch_type_map == ProgramDefinitionMapType.SIMPLE.name:
        _fig = plot_comparison_runs_overview_map_simple(
            list(trajects.values()), selected_sections
        )
    elif switch_type_map == ProgramDefinitionMapType.PROJECTS.name:
        _fig = plot_comparison_runs_overview_map_projects(
            projects, list(trajects.values())
        )
    elif switch_type_map == ProgramDefinitionMapType.ASSESSMENT_PROBABILITIES.name:
        _fig = plot_comparison_runs_overview_map_assessment(list(trajects.values()))
    elif switch_type_map == ProgramDefinitionMapType.VEILIGHEIDSRENDEMENT_INDEX.name:
        _fig = plot_order_reinforcement_index_map(list(trajects.values()))
    else:
        _fig = plot_default_overview_map_dummy()
    return _fig
