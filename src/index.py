from dash import html, dcc
import dash_bootstrap_components as dbc

from src.component_ids import STORE_CONFIG
from src.layouts.layout_navigation_bar import nav_bar_layout
from src.layouts.layout_main_page import make_layout_main_page

from src.app import app
# !!! Keep lines below to add callbacks to app !!!
from src.callbacks.traject_page import callbacks_main_page
from src.callbacks.traject_page import callback_tabs_switch
from src.callbacks.traject_page import callbacks_tab_content
from src.callbacks.traject_page import callback_optimize

# Define the app layout
app.layout = dbc.Container(
    id="app-container",
    children=
    [
        dcc.Location(id='url', pathname='welcome', refresh=False),
        dcc.Store(id='stored-data', data=None),
        dcc.Store(id=STORE_CONFIG, data=None),
        nav_bar_layout,
        make_layout_main_page(),
    ],
    fluid=True,
)

# Run the app on localhost:8050
if __name__ == '__main__':
    print("============================= RERUN THE APP ====================================")
app.run_server(debug=True)
