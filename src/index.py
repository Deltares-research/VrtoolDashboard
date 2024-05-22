import dash
from dash import dcc
import dash_bootstrap_components as dbc

from src.component_ids import STORE_CONFIG
from src.layouts.layout_traject_page.layout_modal_optimize import modal_optimize

from src.app import app

from src.layouts.layout_traject_page.layout_navigation_bar import nav_bar_layout_1

# Keep the import below to activate the callbacks
import src.callbacks.traject_page.callback_renderer
import src.callbacks.traject_page.callback_tabs_switch
import src.callbacks.traject_page.callback_download_geojson
import src.callbacks.traject_page.callbacks_main_page
import src.callbacks.traject_page.callbacks_tab_content
import src.callbacks.database_interaction_page.callback_optimize


# Define the app layout
app.layout = dbc.Container(
    id="app-container",
    children=
    [
        dcc.Store(id='stored-data', data=None, storage_type="session"),
        dcc.Store(id=STORE_CONFIG, data=None, storage_type="session"),
        nav_bar_layout_1,
        modal_optimize,  # keep this line to import the modal as closed to the app by default
        dash.page_container,
    ],
    fluid=True,
)

# Run the app on localhost:8050
if __name__ == '__main__':
    ascii_art = """
    ____    ____ .______         .___________.  ______     ______     __
    \   \  /   / |   _  \        |           | /  __  \   /  __  \   |  |
     \   \/   /  | | _)  |       `--- | | ----`|  | |  |  |  | |  |  |  |
      \      /   |      /             | |      |  | |  |  |  | |  |  |  |
       \    /    | | \  \----.        | |      | `--'  |  |  `--' |  |  `----.
        \__/     |_|  `._____ |       |_|      \______/    \______/  |_______|

    """
    print("============================= RERUN THE APP ====================================")
    print(ascii_art)
    app.run_server(debug=True)
