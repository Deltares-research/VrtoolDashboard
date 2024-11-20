import pandas as pd
import dash_ag_grid as dag

from src.component_ids import TABLE_ORDER_COMPARISON_MEASURES

color_higlight = "mediumaquamarine"
columnDefs = [
    {
        'headerName': 'Run 1',
        'children': [

            {"field": "run_1_section_name", "sortable": False, 'headerName': 'Sectie', 'width': 100},

            {'field': "run_1_measure", 'headerName': 'Maatregel', "wrapText": True},

        ],
    },
    {
        'headerName': 'Run 2',
        'children': [
            {"field": "run_2_section_name", "sortable": False, 'headerName': 'Sectie', 'width': 100,
             'cellStyle': {"border-left": "2px solid black"}, },

            {'field': "run_2_measure", 'headerName': 'Maatregel'},

        ]
    }
]

df = pd.DataFrame({

})

table_ag_grid_order_measures = dag.AgGrid(
    id=TABLE_ORDER_COMPARISON_MEASURES,
    rowData=df.to_dict("records"),
    defaultColDef={"resizable": True,
                   "wrapHeaderText": True,
                   "autoHeaderHeight": True,
                   "filter": True},
    columnDefs=columnDefs,
    columnSize="sizeToFit",
    dashGridOptions={"animateRows": False},
    style={'height': 900, },
    # className="ag-theme-quartz", ugly
    # className="ag-theme-alpine", default
    className="ag-theme-balham",

)
