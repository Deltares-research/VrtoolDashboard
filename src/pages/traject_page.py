import dash
from dash import html, dcc
from src.layouts.layout_main_page import make_layout_main_page

dash.register_page(__name__)

layout = html.Div([make_layout_main_page(),
                   # dcc.Store(id='stored-data', data=None, storage_type="local"),
                   ],
                  )

# !!! Keep lines below to add callbacks to app !!!

