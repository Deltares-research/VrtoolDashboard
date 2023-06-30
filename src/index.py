from dash import html, dcc
import dash_bootstrap_components as dbc

from src.layouts.layout_navigation_bar import nav_bar_layout
from src.layouts.layout_main_page import make_layout_main_page

from src.app import app
from src.callbacks import callbacks_main_page  # !!! KEEP THIS LINE !!!

# Define the app layout
app.layout = dbc.Container(
    id="app-container",
    children=
    [
        dcc.Location(id='url', pathname='welcome', refresh=False),
        dcc.Store(id='stored-data', data=None),
        nav_bar_layout,
        make_layout_main_page(),
    ],
    fluid=True,
)

# Run the app on localhost:8050
if __name__ == '__main__':
    print("============================= RERUN THE APP ====================================")
app.run_server(debug=True)
