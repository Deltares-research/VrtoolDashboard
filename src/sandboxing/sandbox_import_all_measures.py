import json
import time
from pathlib import Path

from vrtool.defaults.vrtool_config import VrtoolConfig
from vrtool.orm.orm_controllers import open_database

from src.callbacks.traject_page.callbacks_tab_content import (
    get_mechanism_name_ORM,
    make_graph_measure_results_comparison,
)
from src.constants import CalcType, ColorBarResultType, Mechanism
from src.orm import models as orm_model
from src.orm.import_database import (
    get_all_measure_results,
    get_dike_traject_from_config_ORM,
    get_name_optimization_runs,
)
from src.orm.importers.dike_traject_importer import DikeTrajectImporter
from src.plotly_graphs.measure_comparison_graph import plot_measure_results_graph
from src.plotly_graphs.pf_length_cost import plot_pf_length_cost
from src.plotly_graphs.plotly_maps import (
    plot_dike_traject_reliability_initial_assessment_map,
    plot_dike_traject_reliability_measures_assessment_map,
    plot_overview_map,
)
from src.utils.utils import export_to_json

# _vr_config = VrtoolConfig().from_json(Path(__file__).parent.parent / "tests/data/Case_24_3/config.json")
# _vr_config = VrtoolConfig().from_json(Path(r"C:\Users\hauth\bitbucket\VRtoolDashboard\tests\data\TestCase1_38-1_no_housing_testingonly\vr_config.json"))
_vr_config = VrtoolConfig().from_json(
    Path(
        # r"C:\Users\hauth\OneDrive - Stichting Deltares\Documents\tempo\VRM\figure_DPI\config.json"
        # r"C:\Users\hauth\OneDrive - Stichting Deltares\Desktop\projects\VRTools\database\24-3\config.json"
        # r"C:\Users\hauth\OneDrive - Stichting Deltares\Documents\tempo\VRM\eduard_debug\optimized_results\optimized_results\config.json"
        # r"C:\Users\hauth\OneDrive - Stichting Deltares\Documents\tempo\VRM\test_lisa_24_07\config.json"
        r"C:\Users\hauth\OneDrive - Stichting Deltares\Documents\tempo\VRM\test_stephan_6_august\config.json"
    )
)
# _vr_config = VrtoolConfig().from_json(Path(__file__).parent.parent / "tests/data/TestCase1_38-1_no_housing/vr_config.json")
t0 = time.time()
section_name = "1"
mechanism = Mechanism.SECTION.name
mechanism = get_mechanism_name_ORM(mechanism)
_meas_results, _vr_steps, _dsn_steps = get_all_measure_results(
    _vr_config,
    section_name,
    mechanism,
    run_id_vr=1,
    run_id_dsn=2,
    time=0,
    active_mechanisms=["Piping", "Overflow", "StabilityInner", "Revetment"],
)

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

fig = plot_measure_results_graph(
    _meas_results, _vr_steps, _dsn_steps, mechanism, section_name, year_index=0
)

# fig =  make_graph_measure_results_comparison()
fig.show()
