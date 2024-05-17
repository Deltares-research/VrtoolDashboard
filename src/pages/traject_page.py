import dash
from dash import html, dcc
from src.layouts.layout_main_page import make_layout_main_page

dash.register_page(__name__)

layout = html.Div([make_layout_main_page(),
                   ],
                  )



# !!! Keep lines below to add callbacks to app !!!
# from src.callbacks.traject_page import callbacks_main_page
# from src.callbacks.traject_page import callback_tabs_switch
# from src.callbacks.traject_page import callbacks_tab_content
# from src.callbacks.traject_page import callback_optimize
# from src.callbacks.traject_page import callback_download_geojson
# from src.callbacks.traject_page import callback_renderer