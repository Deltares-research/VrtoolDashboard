from dash import html, dcc
import dash_bootstrap_components as dbc



def make_collapsing_menu(menu_name: str, inner_layouts: list, collapse_id: id, is_open: bool = True) -> html.Div:
    """
    Make a standard collasping menu with a download button and a list of inner layouts
    :param inner_layouts:
    :return:
    """
    layout = html.Div(

        [
            html.Hr(style={"margin": "0px"}),
            dbc.Button(
                html.Strong(f"{menu_name}"),
                id=f"collapse_button_{collapse_id}",
                outline=False,
                color='white',
                n_clicks=0,
                style={"margin-top": "0px"},
            ),
            dbc.Collapse(
                dbc.Card(dbc.CardBody(
                    inner_layouts,
                )),
                id=f"collapse_{collapse_id}",
                is_open=is_open,
            ),
        ]
    )
    return layout
