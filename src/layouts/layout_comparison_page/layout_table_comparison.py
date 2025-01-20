import pandas as pd
import dash_ag_grid as dag

from src.component_ids import TABLE_COMPARISON_MEASURES

# color_higlight = "bg-danger"
color_higlight = "mediumaquamarine"
columnDefs = [
    {"field": "section_name", "sortable": True, 'headerName': 'Dijkvak', "pinned": True, 'width': 100},
    {"field": "section_length", 'headerName': 'L (m)', 'width': 55},
    {
        'headerName': 'Run 1',
        'children': [

            {'field': "run_1_measure", 'headerName': 'Maatregel', "wrapText": True,
             'cellStyle': {"border-left": "2px solid black"},

             },

            {'field': "run_1_dberm", 'headerName': 'Dberm', 'width': 70,
             "cellStyle": {"styleConditions": [
                 {"style": {"backgroundColor": color_higlight},
                  "condition": 'params.data.run_1_dberm != params.data.run_2_dberm'},
             ]},

             },

            {'field': "run_1_dcrest", 'headerName': 'Dcrest', 'width': 60,
             "cellStyle": {"styleConditions": [
                 {"style": {"backgroundColor": color_higlight},
                  "condition": 'params.data.run_1_dcrest != params.data.run_2_dcrest'},
             ]},

             },

            {'field': "run_1_Lscreen", 'headerName': 'LScherm', 'width': 60,
             "cellStyle": {"styleConditions": [
                 {"style": {"backgroundColor": color_higlight},
                  "condition": 'params.data.run_1_Lscreen != params.data.run_2_Lscreen'},
             ]},

             },

            {
            "field": "run_1_cost", "headerName": "Kosten (M€)", "width": 60,
            }

        ],
    },
    {
        'headerName': 'Run 2',
        'children': [
            {'field': "run_2_measure", 'headerName': 'Maatregel', 'cellStyle': {"border-left": "2px solid black"},

             },
            {'field': "run_2_dberm", 'headerName': 'Dberm', 'width': 60,
             "cellStyle": {"styleConditions": [
                 {"style": {"backgroundColor": color_higlight},
                  "condition": 'params.data.run_1_dberm != params.data.run_2_dberm'},
             ]},

             },

            {'field': "run_2_dcrest", 'headerName': 'Dcrest', 'width': 60,
             "cellStyle": {"styleConditions": [
                 {"style": {"backgroundColor": color_higlight},
                  "condition": 'params.data.run_1_dcrest != params.data.run_2_dcrest'},
             ]},

             },

            {'field': "run_2_Lscreen", 'headerName': 'LScherm', 'width': 60,
             "cellStyle": {"styleConditions": [
                 {"style": {"backgroundColor": color_higlight},
                  "condition": 'params.data.run_1_Lscreen != params.data.run_2_Lscreen'},
             ]},

             },
            {
                "field": "run_2_cost", "headerName": "Kosten (M€)", "width": 60,
            }
        ]
    }
]

getRowStyle = {
    "styleConditions": [
        {
            "condition": 'params.data.run_1_measure != params.data.run_2_measure',
            "style": {"backgroundColor": "grey", "color": "white"},
        },
    ]
}

df = pd.DataFrame({
    "section_name": [],
    "section_length": [],
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
    getRowStyle=getRowStyle,

)
