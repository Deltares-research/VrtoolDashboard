import dash
from dash import html

from src.layouts.layout_comparison_page.layout_comparison_page_tab import project_definition_tab_layout

dash.register_page(__name__)


layout = html.Div([
    project_definition_tab_layout,

])
