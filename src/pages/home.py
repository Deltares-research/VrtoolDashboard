import dash
from dash import html, dcc

dash.register_page(__name__, path='/')

layout = html.Div([
    html.H1('This is our Home page'),
    html.Div('This is our Home page content.'),

    # html.Div([
    #     html.Div(
    #         dcc.Link(f"{page['name']} - {page['path']}", href=page["relative_path"])
    #     ) for page in dash.page_registry.values()
    # ]),
    dcc.Link("Go to traject page", href="/traject-page"),
    # dcc.Link("Go to database interaction page", href="/traject-page")
    # dcc.Link("Go to region page", href="/traject-page")

])