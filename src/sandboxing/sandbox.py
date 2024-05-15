import json
from pathlib import Path

from vrtool.probabilistic_tools.probabilistic_functions import beta_to_pf

from src.callbacks.traject_page.callbacks_tab_content import make_graph_pf_vs_cost
from src.constants import ResultType, CalcType, ColorBarResultType, Mechanism, SubResultType, get_mapbox_token
from src.linear_objects.dike_traject import DikeTraject
from src.plotly_graphs.pf_length_cost import plot_pf_length_cost
from src.plotly_graphs.plotly_maps import plot_dike_traject_reliability_measures_assessment_map, \
    plot_dike_traject_reliability_initial_assessment_map, plot_overview_map, plot_dike_traject_urgency

pf = beta_to_pf(3.87676607842221)
_dike_data = json.load(
    # open(Path(r"C:\Users\hauth\bitbucket\VRtoolDashboard\tests\data\Case_16_1\reference\dike_data_16_1.json")))
    open(Path(
        # r"C:\Users\hauth\bitbucket\VRtoolDashboard\tests\data\Case_38_1_sterker_VZG2\reference\dike_data.json"
        r"C:\Users\hauth\bitbucket\VRtoolDashboard\tests\data\Case_24_3\reference\dike_data_24_3.json"
         # r"C:\Users\hauth\bitbucket\VRtoolDashboard\tests\data\Case_31_1\config.json"
    )))
print(_dike_data)
_dike_traject = DikeTraject.deserialize(_dike_data)

result_type = ResultType.RELIABILITY
cost_length_switch = "COST"
# _fig = plot_overview_map(_dike_traject)
# _fig = plot_pf_length_cost(_dike_traject, 2025, result_type.name, cost_length_switch)

# _fig = plot_dike_traject_reliability_measures_assessment_map(_dike_traject, 2026, result_type.name,
#                                                              calc_type=CalcType.VEILIGHEIDSRENDEMENT.name,
#                                                              colorbar_result_type=ColorBarResultType.MEASURE.name,
#                                                              mechanism_type=Mechanism.SECTION.name,
#                                                              sub_result_type=SubResultType.MEASURE_TYPE.name, )
# #
# _fig = plot_dike_traject_reliability_initial_assessment_map(_dike_traject, 2025, result_type.name,
#                                                             mechanism_type=Mechanism.REVETMENT.name, )

_fig = plot_dike_traject_urgency(_dike_traject, 2025, 10, CalcType.VEILIGHEIDSRENDEMENT.name)
_fig.update_layout(mapbox=dict(accesstoken=get_mapbox_token()))
_fig.show()


