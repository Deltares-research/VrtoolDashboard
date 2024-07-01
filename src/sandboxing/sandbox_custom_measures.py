from pathlib import Path

from vrtool.common.enums import CombinableTypeEnum, MechanismEnum
from vrtool.defaults.vrtool_config import VrtoolConfig
from vrtool.orm.orm_controllers import add_custom_measures

custom_measure_list_1 = [
    {"MEASURE_NAME": "rocky 2", "COMBINABLE_TYPE": CombinableTypeEnum.FULL.name, "SECTION_NAME": "7",
     "MECHANISM_NAME": MechanismEnum.OVERFLOW.name, "TIME": 20, "COST": 1000, "BETA": 6.6},
    {"MEASURE_NAME": "rocky 2", "COMBINABLE_TYPE": CombinableTypeEnum.FULL.name, "SECTION_NAME": "7",
     "MECHANISM_NAME": MechanismEnum.OVERFLOW.name, "TIME": 0, "COST": 1000, "BETA": 5.0},
]

custon = [{'MEASURE_NAME': 'Test2345', 'COMBINABLE_TYPE': 'FULL', 'SECTION_NAME': '7', 'MECHANISM_NAME': 'Stabiliteit',
           'TIME': 0.0, 'COST': 100.0, 'BETA': 4.5},
          {'MEASURE_NAME': 'Rock', 'COMBINABLE_TYPE': 'FULL', 'SECTION_NAME': '7', 'MECHANISM_NAME': 'Piping',
           'TIME': 0.0, 'COST': 2000.0, 'BETA': 3.5}]

_vr_config = VrtoolConfig()
_vr_config.traject = '38-1'
_vr_config.input_directory = Path(
    r"C:/Users/hauth/OneDrive - Stichting Deltares/Documents/tempo/VRM/test_custom_measures")
_vr_config.output_directory = Path(
    "C:/Users/hauth/OneDrive - Stichting Deltares/Documents/tempo/VRM/test_custom_measures/results")
_vr_config.input_database_name = "vrtool_input.db"
_vr_config.excluded_mechanisms = [MechanismEnum.REVETMENT, MechanismEnum.HYDRAULIC_STRUCTURES]

# 2. Run test
_added_measures = add_custom_measures(
    _vr_config, custom_measure_list_1
)
