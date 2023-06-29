from dash import html, dcc
import dash_bootstrap_components as dbc



layout_upload_button = html.Div([

        dcc.Upload(
            id='upload-data-zip',
            children=html.Div([
                'Drag and Drop a zip ',
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
            multiple=False,
            accept='.zip'
        ),

        dbc.Toast(

            [html.P("File uploaded successfully!", className="mb-0")],
            id="upload-toast",
            header="Success",
            icon="success",
            duration=5000,  # Display duration in milliseconds
            dismissable=True,
            is_open=False,

        ),
        html.Div(id='output-data-upload-zip'),
    ])
