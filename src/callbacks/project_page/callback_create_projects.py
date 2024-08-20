from dash import callback, Output, Input, State, dash

from src.component_ids import MULTI_SELECT_SECTION_FOR_PROJECT_ID, EDITABLE_PROJECT_TABLE_ID, STORED_IMPORTED_RUNS_DATA, \
    TABLE_PROJECT_SUMMARY_ID, ADD_PROJECT_BUTTON_ID, PROJECT_NAME_INPUT_FIELD_ID, ALERT_PROJECT_CREATION_ID, \
    STORED_PROJECT_OVERVIEW_DATA, UPDATE_PROJECT_BUTTON_ID, PROJECT_YEAR_INPUT_FIELD_ID
from src.linear_objects.dike_traject import DikeTraject


@callback(
    Output(MULTI_SELECT_SECTION_FOR_PROJECT_ID, "data"),
    Input(EDITABLE_PROJECT_TABLE_ID, "rowData"),
    State(STORED_IMPORTED_RUNS_DATA, "data")
)
def get_multiselect_options(table_data: list[dict], project_data: dict) -> list[dict]:
    data = []

    for dike_traject_data in project_data.values():
        dike_traject = DikeTraject.deserialize(dike_traject_data)

        if dike_traject.name in [group["group"] for group in data]:
            continue
        group_dict = {"group": dike_traject.name,
                      "items": []
                      }
        for section in dike_traject.dike_sections:
            group_dict["items"].append({"label": section.name, "value": section.name + "|" + dike_traject.name})
        data.append(group_dict)

    return data


@callback(
    Output(ALERT_PROJECT_CREATION_ID, "is_open"),
    Output(ALERT_PROJECT_CREATION_ID, "children"),
    Output(STORED_PROJECT_OVERVIEW_DATA, "data"),
    Input(ADD_PROJECT_BUTTON_ID, "n_clicks"),
    State(MULTI_SELECT_SECTION_FOR_PROJECT_ID, "value"),
    State(PROJECT_NAME_INPUT_FIELD_ID, "value"),
    State(PROJECT_YEAR_INPUT_FIELD_ID, "value"),
    State(STORED_PROJECT_OVERVIEW_DATA, "data")
)
def create_and_store_project(n_clicks: int, multi_select_value: list[str],
                             project_name: str, year: int, stored_project_data: list) -> tuple:
    """

    :param n_clicks: nb of clicks of the button "Maak Project"
    :param project_data:
    :param multi_select_value:
    :param project_name:
    :param current_table_row:
    :return:
    """
    if stored_project_data is None:
        stored_project_data = []

    if n_clicks is None:
        return dash.no_update, dash.no_update, dash.no_update

    if project_name is None or project_name == "":
        return dash.no_update, "Project naam mag niet leeg zijn.", dash.no_update

    if len(multi_select_value) == 0:
        return dash.no_update, dash.no_update, dash.no_update

    if year is None or year == "":
        return dash.no_update, "Jaar mag niet leeg zijn.", dash.no_update

    # Do nothing update if the name of the project is already in the table
    for project in stored_project_data:
        if project["project"] == project_name:
            return True, f"Project {project_name} bestaat al.", dash.no_update

    for project in stored_project_data:
        for section in project["sections"]:
            if section in multi_select_value:
                return True, f"Section {section} is already in project {project['project']}", dash.no_update

    stored_project_data.append({"project": project_name,
                                "sections": multi_select_value,  # not displayed in the table but is kept in memory
                                "section_number": len(multi_select_value),
                                "year": year,
                                "length": 0.0,
                                })

    return False, dash.no_update, stored_project_data


@callback(
    Output(TABLE_PROJECT_SUMMARY_ID, "rowData"),
    Input(STORED_PROJECT_OVERVIEW_DATA, "data"),
    Input("tabs_tab_project_page", "active_tab")

)
def fill_project_overview_table(stored_project_data: list, dummy) -> list[dict]:
    output_list = []
    for project in stored_project_data:
        output_list.append({"project": project["project"],
                            "section_number": project["section_number"],
                            "year": project["year"],
                            "length": project["length"],
                            })
    return output_list


@callback(
    Output(ALERT_PROJECT_CREATION_ID, "is_open", allow_duplicate=True),
    Output(ALERT_PROJECT_CREATION_ID, "children", allow_duplicate=True),
    Output(STORED_PROJECT_OVERVIEW_DATA, "data", allow_duplicate=True),
    Input(UPDATE_PROJECT_BUTTON_ID, "n_clicks"),
    State(MULTI_SELECT_SECTION_FOR_PROJECT_ID, "value"),
    State(PROJECT_NAME_INPUT_FIELD_ID, "value"),
    State(PROJECT_YEAR_INPUT_FIELD_ID, "value"),
    State(STORED_PROJECT_OVERVIEW_DATA, "data"),
    allow_duplicate=True,
    prevent_initial_call=True,
)
def update_stored_project(n_clicks: int, multi_select_value: list[str],
                          project_name: str, year: int, stored_project_data: list) -> tuple:
    """

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

    id_list_to_update = None
    list_to_return = []
    for project in stored_project_data:
        if project["project"] == project_name:
            list_to_return.append({"project": project_name,
                                   "sections": multi_select_value,  # not displayed in the table but is kept in memory
                                   "section_number": len(multi_select_value),
                                   "year": year,
                                   "length": 0.0,
                                   })

            continue  # Skip the validity check of the sections for the project to update
        list_to_return.append(project)

        # Check if the sections are not already in another project, if so, return an error message
        for section in project["sections"]:
            if section in multi_select_value:
                return True, f"Section {section} is already in project {project['project']}", dash.no_update

    return False, dash.no_update, list_to_return
