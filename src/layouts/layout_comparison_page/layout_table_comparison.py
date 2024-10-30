import pandas as pd
import dash_ag_grid as dag

from src.component_ids import TABLE_COMPARISON_MEASURES

# df = pd.read_csv(
#     "https://raw.githubusercontent.com/plotly/datasets/master/iris.csv"
# )

columnDefs = [
    {"field": "section_name", "sortable": True, 'headerName': 'Sectie', "pinned": True, 'width': 80},
    {
        'headerName': 'Run 1',
        'children': [

            {'field': "run_1_measure", 'headerName': 'Maatregel', "wrapText": True,
             'cellStyle': {"border-left": "2px solid black"},

             # "cellClassRules": {"bg-danger": 'params.data.run_1_measure == params.data.run_2_measure'},
             },

            {'field': "run_1_dberm", 'headerName': 'Dberm', 'width': 50,
             # "cellClassRules": {"bg-danger": 'params.data.run_1_dberm == params.data.run_2_dberm',},

             },
        ],
    },
    {
        'headerName': 'Run 2',
        'children': [
            {'field': "run_2_measure", 'headerName': 'Maatregel', 'cellStyle': {"border-left": "2px solid black"},
             # "cellClassRules": {"bg-danger": 'params.data.run_1_measure == params.data.run_2_measure'},

             },
            {'field': "run_2_dberm", 'headerName': 'Dberm', 'width': 50,
             # "cellClassRules": {"bg-danger": 'params.data.run_1_dberm == params.data.run_2_dberm',}

             },
        ]
    }
]

# rowClassRules = {
#     "bg-danger": 'params.data.run_1_measure != params.data.eeee',
#     # "bg-danger": 'params.data.run_1_dberm == params.data.run_2_dberm',
#     # "mediumaquamarine": 'params.data.run_1_dberm == params.data.run_2_dberm',
# }

rowClassRules = {
    "bg-danger": 'console.log(params.data.run_1_measure, params.data.run_2_measure) || params.data.run_1_measure != params.data.run_2_measure',
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
    # defaultColDef={"filter": True},
    defaultColDef={"resizable": True,
                   "wrapHeaderText": True,
                   "autoHeaderHeight": True, },
    columnDefs=columnDefs,
    columnSize="sizeToFit",
    dashGridOptions={"animateRows": False},
    style={'height': 900, },
    # className="ag-theme-quartz",
    # className="ag-theme-alpine",
    className="ag-theme-balham",
    rowClassRules=rowClassRules,

)
