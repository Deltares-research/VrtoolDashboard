import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

dash.register_page(__name__, path='/')

layout = html.Div([

    html.H1("Welkom bij het dashboard van Versterkingsaanpak vanuit VR tool 🌊",
            style={"textAlign": "center", "marginTop": "100px"}),

    dmc.Text(
        " Dit dashboard kan worden gebruikt om de resultaten van veiligheidsrendementberekeningen te visualiseren, en deze te vertalen naar de scope van dijkversterkingsprojecten.",
        style={"textAlign": "center", "marginTop": "20px", "marginBottom": "40px"}
    ),

    # Clickable Card Layout
    dbc.Container([
        dbc.Row([
            dbc.Col(
                dcc.Link(
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.H4("Traject analyse", className="card-title"),
                                    dmc.List(
                                        [
                                            dmc.ListItem("Importeer een dijktraject", className="card-text"),
                                            dmc.ListItem("Visualiseer de resultaten van de VR optimalisatie",
                                                         className="card-text"),
                                            dmc.ListItem("Bekijk de veiligheid van de dijkvakken",
                                                         className="card-text"),
                                            dmc.ListItem("Bekijk de toegepaste maatregelen", className="card-text"),
                                        ]
                                    ),

                                ]
                            ),
                        ],
                        style={"cursor": "pointer", "height": "100%", "borderColor": "#007BFF"},  # Hover effect
                    ),
                    href="/traject-page",  # Redirect URL for Dashboard page
                    style={"textDecoration": "none"}  # Remove underline from the link
                ),
                width=4,  # Adjust size of the columns
            ),
            dbc.Col(
                dcc.Link(
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.H4("Gebied analyse ", className="card-title"),
                                    dmc.List(
                                        [
                                            dmc.ListItem("Importeer dijktrajecten", className="card-text"),
                                            dmc.ListItem("Genereer versterking plannen",
                                                         className="card-text"),
                                            dmc.ListItem("Visualiseer analytics op gebiedsniveau",
                                                         className="card-text"),
                                        ]
                                    )
                                ]
                            ),
                        ],
                        style={"cursor": "pointer", "height": "100%", "borderColor": "#28A745"},  # Hover effect
                    ),
                    href="/project-page",  # Redirect URL for Reports page
                    style={"textDecoration": "none"}  # Remove underline from the link

                ),
                width=4,
            ),
            dbc.Col(
                dcc.Link(
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.H4("Vergelijken", className="card-title"),
                                    dmc.List(
                                        [
                                            dmc.ListItem("Importeer meerdere dijktrajecten", className="card-text"),
                                            dmc.ListItem("Vergelijk de resultaten van de VR optimalisatie",
                                                         className="card-text"),

                                        ]
                                    ),
                                ]
                            ),
                        ],
                        style={"cursor": "pointer", "height": "100%", "borderColor": "#FFC107"},  # Hover effect
                    ),
                    href="/comparison-run-page",  # Redirect URL for Settings page
                    style={"textDecoration": "none"}  # Remove underline from the link

                ),
                width=4,
            ),
        ], justify="center", style={"marginTop": "40px"}),  # Center-align and add top margin
    ]),

])
