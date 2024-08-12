import dash
from dash import html, dcc

dash.register_page(__name__, path='/')

layout = html.Div([
    html.H1('This is our Home page'),
    html.Div('This is our Home page content. Lorem ipsum dolor sit amet, consectetur adipiscing elit. '),

    # html.Div([
    #     html.Div(
    #         dcc.Link(f"{page['name']} - {page['path']}", href=page["relative_path"])
    #     ) for page in dash.page_registry.values()
    # ]),


    dcc.Link("Go to traject page", href="/traject-page"),
    html.Br(),
    dcc.Link("Go to database interaction page", href="/database-interaction-page"),
    html.Br(),
    dcc.Link("Go to project page", href="/project-page"),
    html.Br(),
    dcc.Link("Go to comparison run page", href="/comparison-run-page"),
    # dcc.Link("Go to region page", href="/traject-page")

])