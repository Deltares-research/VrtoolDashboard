import dash
from dash import dcc, html

from src.layouts.layout_traject_page.layout_main_page import make_layout_main_page

dash.register_page(__name__, path="/traject-page")

layout = html.Div(
    [
        make_layout_main_page(),
        dcc.Location(
            id="url", refresh=True
        ),  # Keep this line for the callback "fill_option_field_run_selection" to work properly
    ]
)
