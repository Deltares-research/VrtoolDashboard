from dash import callback, Output, Input, State, dash

from src.component_ids import MULTI_SELECT_SECTION_FOR_PROJECT_ID, EDITABLE_PROJECT_TABLE_ID, STORED_PROJECT_DATA, \
    TABLE_PROJECT_SUMMARY_ID, ADD_PROJECT_BUTTON_ID, PROJECT_NAME_INPUT_FIELD_ID
from src.linear_objects.dike_traject import DikeTraject


@callback(
    Output(MULTI_SELECT_SECTION_FOR_PROJECT_ID, "data"),
    Input(EDITABLE_PROJECT_TABLE_ID, "rowData"),
    State(STORED_PROJECT_DATA, "data")
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
    Input(ADD_PROJECT_BUTTON_ID, "n_clicks"),
    State(STORED_PROJECT_DATA, "data"),
    State(MULTI_SELECT_SECTION_FOR_PROJECT_ID, "data"),
    State(PROJECT_NAME_INPUT_FIELD_ID, "value"),
    State(TABLE_PROJECT_SUMMARY_ID, "rowData"),
)

def add_project_to_table_summary(n_clicks: int, project_data: dict, multi_select_data: list[dict], project_name: str, current_table_row) -> list[dict]:

    if n_clicks is None:
        return dash.no_update

    if project_name is None or project_name == "":
        return dash.no_update

    if len(multi_select_data) == 0:
        return dash.no_update

    for group in multi_select_data:
        for item in group["items"]:
            if item["value"] in [row["section"] for row in current_table_row]:
                continue
            current_table_row.append({"project": project_name, "section": item["value"]})

    return current_table_row

