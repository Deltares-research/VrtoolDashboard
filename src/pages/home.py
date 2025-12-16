import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import dcc, html

dash.register_page(__name__, path="/")

layout = html.Div(
    [
        html.H1(
            "Welkom bij het Dashboard Veiligheidsrendement 🌊",
            style={"textAlign": "center", "marginTop": "100px"},
        ),
        html.Div(
            [
                dcc.Markdown(
                    """
        Dit dashboard kan worden gebruikt om de resultaten van veiligheidsrendementberekeningen te visualiseren. Daarnaast kunnen nieuwe optimalisatieberekeningen worden uitgevoerd, en kan op basis van meerdere trajecten een programmering voor meerdere dijktrajecten worden gemaakt. 

        Voor toelichting bij het gebruik wordt verwezen naar de [gebruikershandleiding](https://deltares-research.github.io/VrtoolDocumentation/Gebruikershandleiding/Postprocessing/index.html).
        """,
                    style={
                        "textAlign": "center",
                        "marginTop": "20px",
                        "marginBottom": "40px",
                    },
                )
            ],
            style={
                "width": "50%",
                "margin": "auto",
                "marginTop": "20px",
                "marginBottom": "40px",
            },
        ),
        # Clickable Card Layout
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Link(
                                dbc.Card(
                                    [
                                        dbc.CardBody(
                                            [
                                                html.H4(
                                                    "Analyse per traject",
                                                    className="card-title",
                                                ),
                                                dmc.List(
                                                    [
                                                        dmc.ListItem(
                                                            "Visualiseer de resultaten van een veiligheidsrendementberekening",
                                                            className="card-text",
                                                        ),
                                                        dmc.ListItem(
                                                            "Bekijk de veiligheid per vak voor en na versterking",
                                                            className="card-text",
                                                        ),
                                                        dmc.ListItem(
                                                            "Bekijk welke maatregelen te verwachten zijn",
                                                            className="card-text",
                                                        ),
                                                    ]
                                                ),
                                            ]
                                        ),
                                    ],
                                    style={
                                        "cursor": "pointer",
                                        "height": "100%",
                                        "borderColor": "#007BFF",
                                    },  # Hover effect
                                ),
                                href="/traject-page",  # Redirect URL for Dashboard page
                                style={
                                    "textDecoration": "none"
                                },  # Remove underline from the link
                            ),
                            width=4,  # Adjust size of the columns
                        ),
                        dbc.Col(
                            dcc.Link(
                                dbc.Card(
                                    [
                                        dbc.CardBody(
                                            [
                                                html.H4(
                                                    "Analyse op gebiedsniveau",
                                                    className="card-title",
                                                ),
                                                dmc.List(
                                                    [
                                                        dmc.ListItem(
                                                            "Definieer versterkingsprojecten",
                                                            className="card-text",
                                                        ),
                                                        dmc.ListItem(
                                                            "Visualiseer risicoafname op gebiedsniveau",
                                                            className="card-text",
                                                        ),
                                                        dmc.ListItem(
                                                            "Inzicht in kosten op programmaniveau",
                                                            className="card-text",
                                                        ),
                                                    ]
                                                ),
                                            ]
                                        ),
                                    ],
                                    style={
                                        "cursor": "pointer",
                                        "height": "100%",
                                        "borderColor": "#28A745",
                                    },  # Hover effect
                                ),
                                href="/project-page",  # Redirect URL for Reports page
                                style={
                                    "textDecoration": "none"
                                },  # Remove underline from the link
                            ),
                            width=4,
                        ),
                        dbc.Col(
                            dcc.Link(
                                dbc.Card(
                                    [
                                        dbc.CardBody(
                                            [
                                                html.H4(
                                                    "Vergelijken berekeningen",
                                                    className="card-title",
                                                ),
                                                dmc.List(
                                                    [
                                                        dmc.ListItem(
                                                            "Importeer meerdere berekeningen",
                                                            className="card-text",
                                                        ),
                                                        dmc.ListItem(
                                                            "Vergelijk kosten en faalkans uit optimalisatie",
                                                            className="card-text",
                                                        ),
                                                        dmc.ListItem(
                                                            "Vergelijk maatregelen van beide berekeningen",
                                                            className="card-text",
                                                        ),
                                                    ]
                                                ),
                                            ]
                                        ),
                                    ],
                                    style={
                                        "cursor": "pointer",
                                        "height": "100%",
                                        "borderColor": "#FFC107",
                                    },  # Hover effect
                                ),
                                href="/comparison-run-page",  # Redirect URL for Settings page
                                style={
                                    "textDecoration": "none"
                                },  # Remove underline from the link
                            ),
                            width=4,
                        ),
                    ],
                    justify="center",
                    style={"marginTop": "40px"},
                ),  # Center-align and add top margin
            ]
        ),
    ]
)
