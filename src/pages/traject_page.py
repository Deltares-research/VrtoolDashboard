import dash
from dash import html, dcc
from src.layouts.layout_traject_page.layout_main_page import make_layout_main_page

dash.register_page(__name__, path='/traject-page')

layout = html.Div([
    make_layout_main_page(),
    dcc.Location(id='url', refresh=True),
])
