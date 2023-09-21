from dash import html
import dash_bootstrap_components as dbc



nav_bar_layout = html.Div([
    dbc.NavbarSimple(
        children=[
            # dbc.NavItem(dbc.NavLink("Page 1", href="/page1")),
            # dbc.NavItem(dbc.NavLink("Page 2", href="/page2")),
        ],
        brand="Dashboard Veiligheidsrendement",
        brand_style={'font-size': '30px', "color": 'white'},
        brand_href="/",
        color="#141e95",  # this is Deltares color
        # color='primary'
    ),
])
