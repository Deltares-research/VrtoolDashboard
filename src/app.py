from dash import Dash, DiskcacheManager
import dash_bootstrap_components as dbc
import diskcache

custom_css = "/assets/custom.css"

theme = dbc.themes.FLATLY  # https://bootswatch.com/flatly/


cache = diskcache.Cache("./cache")
background_callback_manager = DiskcacheManager(cache)

app = Dash(
    __name__,
    external_stylesheets=[theme],
    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
    background_callback_manager=background_callback_manager,
    suppress_callback_exceptions=True,
)


app.config.suppress_callback_exceptions = True
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True
