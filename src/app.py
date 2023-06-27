
import dash
import dash_bootstrap_components as dbc


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.FLATLY],
                meta_tags=[{"name": "viewport", "content": "width=device-width"}],
                suppress_callback_exceptions=True,)
