import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

from src.component_ids import STORE_CONFIG
from src.layouts.layout_modal_optimize import modal_optimize
from src.layouts.layout_main_page import make_layout_main_page

from src.app import app

# The navbar must be defined in this file, otherwise the page_registry of the app will not be able to find the pages?


from src.callbacks.traject_page import callbacks_main_page
from src.callbacks.traject_page import callback_tabs_switch
from src.callbacks.traject_page import callbacks_tab_content
from src.callbacks.traject_page import callback_optimize
from src.callbacks.traject_page import callback_download_geojson
from src.callbacks.traject_page import callback_renderer
from src.layouts.layout_navigation_bar import nav_bar_layout_1

# Define the app layout
app.layout = dbc.Container(
    id="app-container",
    children=
    [
        # dcc.Location(id='url', pathname='welcome', refresh=False),
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
