
import dash
import dash_bootstrap_components as dbc
from dash import DiskcacheManager
from dash.long_callback import DiskcacheLongCallbackManager

custom_css = '/assets/custom.css'

theme = dbc.themes.FLATLY  # https://bootswatch.com/flatly/

import diskcache

cache = diskcache.Cache("./cache")
background_callback_manager = DiskcacheManager(cache)


app = dash.Dash(__name__,
                external_stylesheets=[theme],
                meta_tags=[{"name": "viewport", "content": "width=device-width"}],
                suppress_callback_exceptions=True)



app.config.suppress_callback_exceptions = True
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True