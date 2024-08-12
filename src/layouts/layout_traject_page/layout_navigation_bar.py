from dash import html, page_registry
import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import html
from dash_iconify import DashIconify


def get_icon(icon):
    return DashIconify(icon=icon, height=16)


nav_bar_layout_1 = html.Div([
    dbc.NavbarSimple(
        children=[
            # dbc.NavItem(dbc.NavLink("Home", href="/", style={"color": "white"})),
            dbc.DropdownMenu([
                dbc.DropdownMenuItem("Traject", href="/traject-page"),
                dbc.DropdownMenuItem("Database interaction", href="/database-interaction-page"),
                dbc.DropdownMenuItem("Project", href="/project-page"),
                dbc.DropdownMenuItem("Comparison run", href="/comparison-run-page"),
            ],
                nav=True,
                label="More Pages",
                toggle_style={
                    "color": "white",
                    "background-color": "#141e95",
                    "border": "0px"

                },
            ),

            # DashIconify(icon="oui:documentation", width=30, color='White'),  #https://icon-sets.iconify.design/
            dbc.NavLink("", href="https://deltares-research.github.io/VrtoolDocumentation/",
                        external_link=True, target="_blank",
                        class_name="fa-solid fa-book",
                        style={"color": "white", 'text-transform': 'lowercase'}
                        ),
            dbc.NavLink(" Documentatie", href="https://deltares-research.github.io/VrtoolDocumentation/",
                        external_link=True, target="_blank",
                        style={"color": "white"}
                        ),

        ],
        brand="Dashboard Veiligheidsrendement",
        brand_style={'font-size': '30px', "color": 'white'},
        brand_href="/",
        color="#141e95",  # this is Deltares color
        links_left=True,
        sticky='Top',
    ),
])
