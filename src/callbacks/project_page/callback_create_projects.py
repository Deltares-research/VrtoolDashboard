from dash import callback, Output, Input, State, dash

from src.component_ids import MULTI_SELECT_SECTION_FOR_PROJECT_ID, EDITABLE_PROJECT_TABLE_ID, STORED_IMPORTED_RUNS_DATA, \
    TABLE_PROJECT_SUMMARY_ID, ADD_PROJECT_BUTTON_ID, PROJECT_NAME_INPUT_FIELD_ID, ALERT_PROJECT_CREATION_ID
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
    Output(TABLE_PROJECT_SUMMARY_ID, "rowData"),
    Output(ALERT_PROJECT_CREATION_ID, "is_open"),
    Output(ALERT_PROJECT_CREATION_ID, "children"),
    Input(ADD_PROJECT_BUTTON_ID, "n_clicks"),
    Input("tabs_tab_project_page", "active_tab"),

    State(STORED_IMPORTED_RUNS_DATA, "data"),
    State(MULTI_SELECT_SECTION_FOR_PROJECT_ID, "value"),
    State(PROJECT_NAME_INPUT_FIELD_ID, "value"),
    State(TABLE_PROJECT_SUMMARY_ID, "rowData"),
)
def add_project_to_table_summary(n_clicks: int, dummy, project_data: dict, multi_select_value: list[str],
                                 project_name: str,
                                 current_table_row) -> tuple:
    """

    :param n_clicks: nb of clicks of the button "Maak Project"
    :param project_data:
    :param multi_select_value:
    :param project_name:
    :param current_table_row:
    :return:
    """
    if n_clicks is None:
        return dash.no_update, dash.no_update, dash.no_update

    if project_name is None or project_name == "":
        return dash.no_update, dash.no_update, "Project naam mag niet leeg zijn."

    if len(multi_select_value) == 0:
        return dash.no_update, dash.no_update, dash.no_update

    # Do nothing update if the name of the project is already in the table
    for project in current_table_row:
        if project["project"] == project_name:
            return dash.no_update, dash.no_update, dash.no_update

    for project in current_table_row:
        for section in project["sections"]:
            if section in multi_select_value:
                return dash.no_update, True, f"Section {section} is already in project {project['project']}"

    current_table_row.append({"project": project_name,
                              "sections": multi_select_value,  # not displayed in the table but is kept in memory
                              "section_number": len(multi_select_value),
                              "year": 2025,
                              "length": 0.0,
                              })

    return current_table_row, False, dash.no_update
