from dash import dcc

from src.component_ids import SELECT_DIKE_SECTION_FOR_MEASURES_ID

layout_radio_dike_section_selection = dcc.Dropdown(
                id=SELECT_DIKE_SECTION_FOR_MEASURES_ID,
                options=[
                ],
                optionHeight=35,  # height/space between dropdown options
                value='',  # dropdown value selected automatically when page loads
                disabled=False,  # disable dropdown value selection
                multi=False,  # allow multiple dropdown values to be selected
                searchable=True,  # allow user-searching of dropdown values
                search_value='',  # remembers the value searched in dropdown
                clearable=True,  # allow user to removes the selected value
                style={'width': "100%"},
            )