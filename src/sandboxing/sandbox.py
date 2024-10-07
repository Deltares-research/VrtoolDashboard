from pathlib import Path
from shutil import rmtree


from vrtool.api import run_step_optimization, ApiRunWorkflows
from vrtool.common.enums import MechanismEnum
from vrtool.defaults.vrtool_config import VrtoolConfig
from vrtool.orm.orm_controllers import export_results_safety_assessment, get_dike_traject, clear_assessment_results, \
    export_results_optimization, clear_measure_results, clear_optimization_results

# ====== IMPORTANT ======== #
# The initial stix must be pre-processed before using them with the prototype. They need to be executed blankly first
# otherwise the serialization will fail.

# 1. Define input and output directories..

_input_model = Path(
    # r"C:\Users\hauth\OneDrive - Stichting Deltares\Documents\tempo\RESULTS"
    "/tests/data/TestCase1_38-1_no_housing"
)
_results_dir = Path(
    r"C:\Users\hauth\OneDrive - Stichting Deltares\Documents\tempo\RESULTS\res"
)
if _results_dir.exists():
    rmtree(_results_dir)

# 2. Define the configuration to use.
_vr_config = VrtoolConfig()
_vr_config.input_directory = _input_model
_vr_config.excluded_mechanisms = [MechanismEnum.REVETMENT, MechanismEnum.HYDRAULIC_STRUCTURES]
_vr_config.output_directory = _input_model / "results"
_vr_config.externals = (
        Path(__file__).parent.parent / "externals/D-Stability 2022.01.2/bin"
)
_vr_config.traject = "38-1"

_vr_config.input_database_name = "vrtool_input.db"

api = ApiRunWorkflows(vrtool_config=_vr_config)

# clear_assessment_results(_vr_config)
# clear_measure_results(_vr_config)
# clear_optimization_results(_vr_config)

# api.run_all()
#
# selected_measures = [(i, 0) for i in range(1, 1631)]  # 652, 649 should work 648 should not
#
# results_optimization = api.run_optimization(selected_measures)
# export_results_optimization(results_optimization, [1, 2])

