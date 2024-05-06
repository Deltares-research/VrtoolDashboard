import json
from pathlib import Path
import time
from vrtool.defaults.vrtool_config import VrtoolConfig
from vrtool.orm.orm_controllers import open_database

from src.constants import CalcType, ColorBarResultType, Mechanism, SubResultType, ResultType, get_mapbox_token
from src.linear_objects.dike_traject import DikeTraject
from src.orm.import_database import get_all_measure_results, get_dike_traject_from_config_ORM, \
    get_name_optimization_runs
from src.orm.importers.dike_traject_importer import DikeTrajectImporter
from src.orm import models as orm_model
from src.plotly_graphs.measure_comparison_graph import plot_measure_results_graph
from src.plotly_graphs.pf_length_cost import plot_pf_length_cost
from src.plotly_graphs.plotly_maps import plot_dike_traject_reliability_measures_assessment_map, plot_overview_map, \
    plot_dike_traject_reliability_initial_assessment_map
from src.utils.utils import export_to_json

# _vr_config = VrtoolConfig().from_json(Path(__file__).parent.parent / "tests/data/Case_24_3/config.json")
# _vr_config = VrtoolConfig().from_json(Path(r"C:\Users\hauth\bitbucket\VRtoolDashboard\tests\data\TestCase1_38-1_no_housing_testingonly\vr_config.json"))
_vr_config = VrtoolConfig().from_json(Path(
    r"C:\Users\hauth\bitbucket\VRtoolDashboard\tests\data\38-1 base river case\config.json"))
# _vr_config = VrtoolConfig().from_json(Path(__file__).parent.parent / "tests/data/TestCase1_38-1_no_housing/vr_config.json")
t0 = time.time()
section_name = "2"
mechanism = Mechanism.SECTION
_meas_results, _vr_steps, _dsn_steps = get_all_measure_results(_vr_config, section_name, mechanism, run_id_vr=1,
                                                               run_id_dsn=2)

# _dike_data = json.load(
#     open(Path(
#         r"C:\Users\hauth\bitbucket\VRtoolDashboard\tests\data\TestCase1_38-1_no_housing\reference\dike_traject_data.json"
#         # r"C:\Users\hauth\bitbucket\VRtoolDashboard\tests\data\Case_38_1\reference\data.json"
#     )))
# _dike_traject = DikeTraject.deserialize(_dike_data)
# #
# # _dike_traject = get_dike_traject_from_config_ORM(vr_config=_vr_config, run_is_vr=1, run_id_dsn=2)
#
# _section = _dike_traject.get_section(section_name)

fig = plot_measure_results_graph(_meas_results, _vr_steps, _dsn_steps, mechanism, section_name)
fig.show()
