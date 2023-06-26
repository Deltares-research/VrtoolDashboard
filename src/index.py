from dash import html, dcc

from app import app

from components.navigation_bar import Navbar

# Define the index page layout
app.layout = html.Div([
    dcc.Location(id='url', pathname='welcome', refresh=False),
    Navbar()
])

# Run the app on localhost:8050
if __name__ == '__main__':
    app.run_server(debug=True)
