from dash import html, dcc
import dash_bootstrap_components as dbc


# Define the navbar structure
def FileDikeUpload() -> html.Div:
    """
    This function returns the navigation bar layout
    :return:
    """
    layout = html.Div([

        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or Dike geo reference or ',
                html.A('Select Files')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            # Allow multiple files to be uploaded
            multiple=True,
            accept='.geojson'
        ),
        html.Div(id='output-data-upload'),
    ])

    return layout
