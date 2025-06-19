import dash
from dash import dcc, _dash_renderer
import dash_bootstrap_components as dbc
import logging

from src.component_ids import STORE_CONFIG, STORED_IMPORTED_RUNS_DATA, STORED_PROJECT_OVERVIEW_DATA, \
    STORED_RUNS_COMPARISONS_DATA
from src.layouts.layout_database_interaction.layout_modal_add_custom_measure import modal_custom_measure
from src.layouts.layout_traject_page.layout_modal_measure import modal_measure_reliability
from src.layouts.layout_traject_page.layout_modal_optimize import modal_optimize
import dash_mantine_components as dmc

from src.app import app

from src.layouts.layout_traject_page.layout_navigation_bar import nav_bar_layout_1

# Keep the import below to activate the callbacks
import src.callbacks.traject_page.callback_renderer
import src.callbacks.traject_page.callback_tabs_switch
import src.callbacks.traject_page.callback_download_geojson
import src.callbacks.traject_page.callbacks_main_page
import src.callbacks.traject_page.callbacks_tab_content
import src.callbacks.database_interaction_page.callback_optimize
import src.callbacks.database_interaction_page.callback_tabs_switch_database
import src.callbacks.database_interaction_page.callback_custom_measure
import src.callbacks.project_page.callback_tabs_switch_project_page
import src.callbacks.project_page.callback_import_run
import src.callbacks.project_page.callback_create_projects
import src.callbacks.project_page.callback_save_and_load_projects
import src.callbacks.comparison_page.callback_import_run
import src.callbacks.comparison_page.callback_tabs_output_switch

_dash_renderer._set_react_version("18.2.0")  # keep this line to avoid error with MantineProvider
# Define the app layout
app.layout = dmc.MantineProvider(dbc.Container(
    id="app-container",
    children=
    [
        dcc.Store(id='stored-data', data=None, storage_type="session"),
        dcc.Store(id=STORE_CONFIG, data=None, storage_type="session"),
        dcc.Store(id=STORED_RUNS_COMPARISONS_DATA, data=None),
        dcc.Store(id=STORED_IMPORTED_RUNS_DATA, data=None, storage_type="session"),
        dcc.Store(id=STORED_PROJECT_OVERVIEW_DATA, data=None, storage_type="session"),
        nav_bar_layout_1,
        modal_optimize,  # keep this line to import the modal as closed to the app by default
        modal_custom_measure,
        modal_measure_reliability,
        dash.page_container,
        dcc.Location(id='url', refresh=True),
    ],
    fluid=True,
))

# Run the app on localhost:8050
if __name__ == '__main__':
    print("============================= STARTING THE APP ====================================")
    print("Please wait while the app is starting...")
    ascii_art = """
    ____    ____ .______         .___________.  ______     ______     __
    \   \  /   / |   _  \        |           | /  __  \   /  __  \   |  |
     \   \/   /  | | _)  |       `--- | | ----`|  | |  |  |  | |  |  |  |
      \      /   |      /             | |      |  | |  |  |  | |  |  |  |
       \    /    | | \  \----.        | |      | `--'  |  |  `--' |  |  `----.
        \__/     |_|  `._____ |       |_|      \______/    \______/  |_______|

    """
    print("=============================                   ====================================")
    print(ascii_art)

    # Supress GET and POST messages in the console for production mode
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    app.run_server(debug=True)
