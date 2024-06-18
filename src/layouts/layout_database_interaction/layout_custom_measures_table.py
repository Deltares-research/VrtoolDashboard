from dash import html, dcc

custom_measure_tab_layout = html.Div([
    # add text
    dcc.Markdown(
        '''
        Met de onderstaande tabel, kunt u custom maatregelen aan de database toevoegen.

        Geef een naam voor de optimizatie run en klik op de knop "Optimize" om de optimalisatie te starten.
        '''
    )
])
