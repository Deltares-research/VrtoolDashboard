import dash
import dash_bootstrap_components as dbc

custom_css = '/assets/custom.css'

theme = dbc.themes.FLATLY  # https://bootswatch.com/flatly/


app = dash.Dash(__name__,
                external_stylesheets=[theme],
                meta_tags=[{"name": "viewport", "content": "width=device-width"}],
                suppress_callback_exceptions=True)


app.config.suppress_callback_exceptions = True
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True