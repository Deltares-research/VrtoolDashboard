from dash import html, page_registry
import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import html
from dash_iconify import DashIconify


def get_icon(icon):
    return DashIconify(icon=icon, height=16)


nav_bar_layout = html.Div([
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Home", href="/")),
            dbc.DropdownMenu([
                dbc.DropdownMenuItem("traject_page", href="/traject"),
                # dbc.DropdownMenuItem("database", href="/database_interaction")
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

# submenu_1 = [
#     html.Li(
#         # use Row and Col components to position the chevrons
#         dbc.Row(
#             [
#                 dbc.Col("Menu 1"),
#                 dbc.Col(
#                     html.I(className="fas fa-chevron-right mr-3"), width="auto"
#                 ),
#             ],
#             className="my-1",
#         ),
#         id="submenu-1",
#     ),
#     # we use the Collapse component to hide and reveal the navigation links
#     dbc.Collapse(
#         [
#             dbc.NavLink("Page 1.1", href="/page-1/1"),
#             dbc.NavLink("Page 1.2", href="/page-1/2"),
#         ]
#         id="submenu-1-collapse",
#     ),
# ]
#
# submenu_2 = [
#     html.Li(
#         dbc.Row(
#             [
#                 dbc.Col("Menu 2"),
#                 dbc.Col(
#                     html.I(className="fas fa-chevron-right mr-3"), width="auto"
#                 ),
#             ],
#             className="my-1",
#         ),
#         id="submenu-2",
#     ),
#     dbc.Collapse(
#         [
#             dbc.NavLink("Page 2.1", href="/page-2/1"),
#             dbc.NavLink("Page 2.2", href="/page-2/2"),
#         ],
#         id="submenu-2-collapse",
#     ),
# ]
#
# sidebar = html.Div(
#     [
#         html.H2("Sidebar", className="display-5"),
#         html.Hr(),
#         html.P(
#             "A sidebar with collapsible navigation links", className="lead"
#         ),
#         dbc.Nav(submenu_1 + submenu_2, vertical=True),
#     ],
#     style={
#         "position": "fixed",
#         "top": 0,
#         "left": 0,
#         "bottom": 0,
#         "width": "16rem",
#         "padding": "2rem 1rem",
#         "background-color": "#f8f9fa",
#     },
#     id="sidebar",
# )
