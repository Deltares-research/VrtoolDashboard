import copy
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pathlib import Path
import numpy as np
from scipy.stats import norm
from peewee import fn
from collections import defaultdict
from vrtool.orm.models import *
from vrtool.orm.orm_controllers import open_database
from vrtool.common.enums import MechanismEnum
# from postprocessing.database_analytics import *
# from postprocessing.database_access_functions import *
# from postprocessing.generate_output import *

def get_overview_of_runs(db_path):
    """Get an overview of the optimization runs in the database.

    Args:
    db_path: str, path to the database

    Returns:
    list of dicts, each dict contains the run id, run name, optimization type, and the discount rate
    """

    with open_database(db_path).connection_context():
        optimization_types = OptimizationRun.select(OptimizationRun, OptimizationType.name.alias('optimization_type_name')).join(
            OptimizationType,  on=(OptimizationRun.optimization_type_id == OptimizationType.id))

        return list(optimization_types.dicts()) #desired output like this? TODO
sns.set(style="whitegrid")
colors = sns.color_palette("colorblind", 10)


database_path = Path(r"C:\Users\hauth\bitbucket\VRtoolDashboard\tests\data\TestCase1_38-1_no_housing\vrtool_input.db")
run_list = get_overview_of_runs(database_path)
print(pd.DataFrame(run_list))

#
# optimization_steps = {run['name']: get_optimization_steps_for_run_id(database_path, run['id']) for run in run_list}
# # add total cost as sum of total_lcc and total_risk in each step
# considered_tc_steps = defaultdict(int)
#
# #
# considered_tc_steps = {run: get_minimal_tc_step(steps) if (run_list[count]['optimization_type_name'] == 'VEILIGHEIDSRENDEMENT') else len(steps)-1 for count, (run, steps) in enumerate(optimization_steps.items())}