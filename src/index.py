import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

from src.component_ids import STORE_CONFIG
from src.layouts.layout_modal_optimize import modal_optimize
from src.layouts.layout_navigation_bar import nav_bar_layout
from src.layouts.layout_main_page import make_layout_main_page

from src.app import app

print(dash.page_registry.values())
print(len(dash.page_registry.values()))

nav_bar_layout_1 = html.Div([
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Home", href="/")),
            dbc.DropdownMenu([
                dbc.DropdownMenuItem("Traject", href="/traject-page"),
                dbc.DropdownMenuItem("Optimization run", href="/database-interaction-page")
            ],

                nav=True,
                label="More Pages",
            ),
            # dbc.DropdownMenu(
            #     children=[
            #         dbc.DropdownMenuItem("Page 1", href="/page-1"),
            #         dbc.DropdownMenuItem("Page 2", href="/page-2"),
            #     ],
            #     nav=True,
            #     in_navbar=True,
            #     label="Menu",
            # ),
            # dbc.NavItem(dbc.NavLink("Page 1", href="/page1")),
            # dbc.NavItem(dbc.NavLink("Page 2", href="/page2")),
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
        sticky='Top'
        # color='primary'
    ),
])

# Define the app layout
app.layout = dbc.Container(
    id="app-container",
    children=
    [
        dcc.Location(id='url', pathname='welcome', refresh=False),
        dcc.Store(id='stored-data', data=None),
        dcc.Store(id=STORE_CONFIG, data=None),
        nav_bar_layout_1,
        # # make_layout_main_page(),
        modal_optimize,  # keep this line to import the modal as closed to the app by default
        # # sidebar

        # html.H1('Multi-page app with Dash Pages'),
        # html.Div([
        #     html.Div(
        #         dcc.Link(f"{page['name']} - {page['path']}", href=page["relative_path"])
        #     ) for page in dash.page_registry.values()
        # ]),
        dash.page_container
    ],
    fluid=True,
)

# Run the app on localhost:8050
if __name__ == '__main__':
    ascii_art = """
    ____    ____ .______         .___________.  ______     ______     __
    \   \  /   / |   _  \        |           | /  __  \   /  __  \   |  |
     \   \/   /  | | _)  |       `--- | | ----`|  | |  |  |  | |  |  |  |
      \      /   |      /             | |      |  | |  |  |  | |  |  |  |
       \    /    | | \  \----.        | |      | `--'  |  |  `--' |  |  `----.
        \__/     |_|  `._____ |       |_|      \______/    \______/  |_______|

    """
    print("============================= RERUN THE APP ====================================")
    print(ascii_art)
    app.run_server(debug=True)
