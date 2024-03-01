from pathlib import Path
import time
from vrtool.defaults.vrtool_config import VrtoolConfig
from vrtool.orm.orm_controllers import open_database

from src.constants import CalcType, ColorBarResultType, Mechanism, SubResultType, ResultType, get_mapbox_token
from src.orm.import_database import get_dike_traject_from_config_ORM, get_name_optimization_runs
from src.orm.importers.dike_traject_importer import DikeTrajectImporter
from src.orm import models as orm_model
from src.plotly_graphs.pf_length_cost import plot_pf_length_cost
from src.plotly_graphs.plotly_maps import plot_dike_traject_reliability_measures_assessment_map, plot_overview_map, \
    plot_dike_traject_reliability_initial_assessment_map
from src.utils.utils import export_to_json

#


# TODO: custom DikeTrajectImporter for the Dashboard
# TODO: this include Importe for each new table and instanticate the classes of the Dashboard.
"""
class User(Model):
    username = TextField()

class Tweet(Model):
    user = ForeignKeyField(User, backref='tweets')
    content = TextField()

# Get all tweets by huey.
query = Tweet.select().where(Tweet.user == user)

# Equivalent to above, using backref:
query = user.tweets

"""

# _vr_config = VrtoolConfig().from_json(Path(__file__).parent.parent / "tests/data/Case_24_3/config.json")
# _vr_config = VrtoolConfig().from_json(Path(r"C:\Users\hauth\bitbucket\VRtoolDashboard\tests\data\TestCase1_38-1_no_housing_testingonly\vr_config.json"))
_vr_config = VrtoolConfig().from_json(Path(
    # r"C:\Users\hauth\bitbucket\VRtoolDashboard\tests\data\Case 7-2\config.json"
    # r"C:\Users\hauth\bitbucket\VRtoolDashboard\tests\data\TestCase1_38-1_no_housing_testingonly\vr_config.json"
     r"C:\Users\hauth\bitbucket\VRtoolDashboard\tests\data\Case_31_1\config.json"
    #  r"C:\Users\hauth\bitbucket\VRtoolDashboard\tests\data\Case_24_3\config.json"
    #  r"C:\Users\hauth\bitbucket\VRtoolDashboard\tests\data\Case_10_3\config.json"
    # r"N:\Projects\11209000\11209353\B. Measurements and calculations\008 - Resultaten Proefvlucht\WDOD\10-3\database_vrtool_0_1_3_no_stix/config.json"
    #  r"N:\Projects\11209000\11209353\B. Measurements and calculations\008 - Resultaten Proefvlucht\WSS\31-1\database_vrtool_0_1_3_aangepast\config.json"
    # r"n:\Projects\11209000\11209353\B. Measurements and calculations\008 - Resultaten Proefvlucht\WSRL\24-3\02_Berekening\config.json"
    # r"N:\Projects\11209000\11209353\B. Measurements and calculations\008 - Resultaten Proefvlucht\WRIJ\47-1\database_vrtool_0_1_3\config.json"
    # r"N:\Projects\11209000\11209353\B. Measurements and calculations\008 - Resultaten Proefvlucht\WRIJ\47-1\database_vrtool_0_1_3\config.json"


))
# _vr_config = VrtoolConfig().from_json(Path(__file__).parent.parent / "tests/data/TestCase1_38-1_no_housing/vr_config.json")
t0 = time.time()
_traject_db = get_dike_traject_from_config_ORM(vr_config=_vr_config, run_is_vr=1, run_id_dsn=2)
data= _traject_db.serialize()
export_to_json(data)
t1 = time.time()
print(f"Time to get dike traject from ORM: {t1 - t0}")
# _fig = plot_overview_map(_traject_db)

# _fig = plot_dike_traject_reliability_initial_assessment_map(_traject_db, 2025, ResultType.RELIABILITY.name,
#                                                             mechanism_type=Mechanism.REVETMENT.name, )
_fig = plot_dike_traject_reliability_measures_assessment_map(_traject_db, 2025,
                                                             result_type=ResultType.RELIABILITY.name,
                                                             calc_type=CalcType.VEILIGHEIDSRENDEMENT.name,
                                                             colorbar_result_type=ColorBarResultType.MEASURE.name,
                                                             mechanism_type=Mechanism.SECTION.name,
                                                             sub_result_type=SubResultType.INVESTMENT_YEAR.name,
                                                             # sub_result_type=SubResultType.BERM_WIDENING.name,
                                                             )

# add token of the mapbox account

# _fig = plot_dike_traject_reliability_measures_assessment_map(_traject_db, 2025, ResultType.RELIABILITY.name,
#                                                              calc_type=CalcType.DOORSNEDE_EISEN.name,
#                                                              colorbar_result_type=ColorBarResultType.MEASURE.name,
#                                                              mechanism_type=Mechanism.SECTION.name,
#                                                              sub_result_type=SubResultType.MEASURE_TYPE.name, )
# _fig = plot_pf_length_cost(_traject_db, 2025, result_type=ResultType.RELIABILITY.name, cost_length_switch="COST")
t2 = time.time()
print(f"Time to plot: {t2 - t1}")

_fig.update_layout(mapbox=dict(accesstoken=get_mapbox_token()))
_fig.show()
