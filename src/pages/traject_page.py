import dash
from dash import html
from src.layouts.layout_traject_page.layout_main_page import make_layout_main_page

dash.register_page(__name__)

layout = html.Div([make_layout_main_page(),
                   ],
                  )
