from dash import html
import dash_bootstrap_components as dbc


# Define the navbar structure
def Navbar():

    layout = html.Div([
        dbc.NavbarSimple(
            children=[
                # dbc.NavItem(dbc.NavLink("Page 1", href="/page1")),
                # dbc.NavItem(dbc.NavLink("Page 2", href="/page2")),
            ],
            brand="Veiligheidrendement Dashboard",
            brand_style={'font-size': '30px', "color": 'white'},
            brand_href="/",
            color="primary",
        ),
    ])

    return layout