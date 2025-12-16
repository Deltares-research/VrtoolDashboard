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
from src.linear_objects.dike_traject import DikeTraject
from src.orm import models as orm_model
from src.orm.import_database import (
    get_all_custom_measures,
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
        r"C:\Users\hauth\bitbucket\VRtoolDashboard\tests\data\38-1 custom measures\config.json"
    )
)
# _vr_config = VrtoolConfig().from_json(Path(__file__).parent.parent / "tests/data/TestCase1_38-1_no_housing/vr_config.json")
t0 = time.time()
section_name = "1"
mechanism = Mechanism.PIPING.name
mechanism = get_mechanism_name_ORM(mechanism)
res = get_all_custom_measures(_vr_config)
