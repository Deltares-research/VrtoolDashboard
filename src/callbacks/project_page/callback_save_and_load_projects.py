import base64
import json

from dash import html, Output, Input, callback, State, dcc, no_update

from src.component_ids import EXPORT_PROJECTS_TO_JSON_ID, BUTTON_DOWNLOAD_PROJECTS_EXPORT_NB_CLICKS, \
    BUTTON_DOWNLOAD_PROJECTS_EXPORT, STORED_PROJECT_OVERVIEW_DATA, STORED_IMPORTED_RUNS_DATA, UPLOAD_SAVED_PROJECTS, \
    SAVE_PROJECTS_NAME_ID


@callback(
    [Output(EXPORT_PROJECTS_TO_JSON_ID, 'data'),
     Output(BUTTON_DOWNLOAD_PROJECTS_EXPORT_NB_CLICKS, "value")],
    [
        Input(BUTTON_DOWNLOAD_PROJECTS_EXPORT, 'n_clicks'),
        Input(BUTTON_DOWNLOAD_PROJECTS_EXPORT_NB_CLICKS, 'value'),
        State(SAVE_PROJECTS_NAME_ID, "value"),
        State(STORED_PROJECT_OVERVIEW_DATA, "data"),
        State(STORED_IMPORTED_RUNS_DATA, "data"), ]
)
def download_reinforced_sections_geojson(n_clicks: int, store_n_click_button: int, filename_save: int,
                                         project_data: list[dict],
                                         imported_runs_data: dict,
                                         ) -> tuple[dict, int]:
    """
    Trigger the button to download and save the projects data into a json file so that it can reused later on.

    :return:
    """

    if imported_runs_data is None or project_data is None or n_clicks == 0 or n_clicks is None:
        return no_update, no_update

    if n_clicks is None or store_n_click_button == n_clicks:  # update when clicking on button ONLY
        return no_update, no_update

    else:
        _content = dict(imported_runs_data=imported_runs_data,
                        project_data=project_data)
        _content_json = json.dumps(_content)

        return dict(content=_content_json,
                    filename=f"{filename_save}.json"), n_clicks


@callback(
    [Output(STORED_IMPORTED_RUNS_DATA, "data", allow_duplicate=True),
     Output(STORED_PROJECT_OVERVIEW_DATA, "data", allow_duplicate=True)],
    [Input(UPLOAD_SAVED_PROJECTS, 'contents')],
    [State(UPLOAD_SAVED_PROJECTS, 'filename')],
    allow_duplicate=True,
    prevent_initial_call=True,
)
def upload_existing_saved_projects(contents: str, filename: str):
    """
    Import projects that have been previously saved by clicking on the button "Opslaan projects". It overwrites the
    current stored projects in STORED_PROJECT_OVERVIEW_DATA and STORED_IMPORTED_RUNS_DATA.

    :param contents: string content of the uploaded json. The file should content at least:
        - imported_runs_data: imported_runs_data
        - project_data: project_data


    :return: imported_runs_data, project_data
    """
    if contents is not None:
        try:

            content_type, content_string = contents.split(',')

            decoded = base64.b64decode(content_string)
            json_content = json.loads(decoded)
            imported_runs_data = json_content["imported_runs_data"]
            project_data = json_content["project_data"]
            return imported_runs_data, project_data

        except:
            return no_update, no_update
    else:
        return no_update, no_update
