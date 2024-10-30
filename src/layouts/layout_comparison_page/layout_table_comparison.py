import pandas as pd
import dash_ag_grid as dag

from src.component_ids import TABLE_COMPARISON_MEASURES

columnDefs = [
    {"field": "section_name", "sortable": True, 'headerName': 'Sectie', "pinned": True, 'width': 80},
    {
        'headerName': 'Run 1',
        'children': [

            {'field': "run_1_measure", 'headerName': 'Maatregel', "wrapText": True,
             'cellStyle': {"border-left": "2px solid black"},

             },

            {'field': "run_1_dberm", 'headerName': 'Dberm', 'width': 50,
             "cellClassRules": {"bg-danger": 'params.data.run_1_dberm != params.data.run_2_dberm', },},

            {'field': "run_1_dcrest", 'headerName': 'Dcrest', 'width': 50,
             "cellClassRules": {"bg-danger": 'params.data.run_1_dcrest != params.data.run_2_dcrest', }, },
        ],
    },
    {
        'headerName': 'Run 2',
        'children': [
            {'field': "run_2_measure", 'headerName': 'Maatregel', 'cellStyle': {"border-left": "2px solid black"},

             },
            {'field': "run_2_dberm", 'headerName': 'Dberm', 'width': 50,
             "cellClassRules": {"bg-danger": 'params.data.run_1_dberm != params.data.run_2_dberm', }},

            {'field': "run_2_dcrest", 'headerName': 'Dcrest', 'width': 50,
             "cellClassRules": {"bg-danger": 'params.data.run_1_dcrest != params.data.run_2_dcrest', }},
        ]
    }
]

rowClassRules = {
    "bg-danger": 'params.data.run_1_measure != params.data.run_2_measure',
}

df = pd.DataFrame({
    "section_name": [],
    "run_1_measure": [],
    "run_1_dberm": [],
    "run_2_measure": [],
    "run_2_dberm": []
})

table_ag_grid_comparison_measures = dag.AgGrid(
    id=TABLE_COMPARISON_MEASURES,
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
    rowClassRules=rowClassRules,

)
