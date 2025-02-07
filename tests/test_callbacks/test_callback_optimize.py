from contextvars import copy_context
from pathlib import Path

import pytest
import json

optimization_table_31_1 = [
    {'section_col': 'WsNoo_Stab_011600_012000', 'reinforcement_col': True, 'reference_year': 2025,
     'GROUND_IMPROVEMENT': True, 'GROUND_IMPROVEMENT_WITH_STABILITY_SCREEN': True,
     'GEOTEXTILE': True, 'DIAPHRAGM_WALL': True, 'STABILITY_SCREEN': True, 'ANCHORED_SHEETPILE': False,
     'REVETMENT': True,
     'CUSTOM': False},
    {'section_col': 'WsNoo_Stab_012000_014100', 'reinforcement_col': True, 'reference_year': 2025,
     'GROUND_IMPROVEMENT': True, 'GROUND_IMPROVEMENT_WITH_STABILITY_SCREEN': True,
     'GEOTEXTILE': True, 'DIAPHRAGM_WALL': True, 'STABILITY_SCREEN': True, 'ANCHORED_SHEETPILE': False,
     'REVETMENT': True,
     'CUSTOM': False},
    {'section_col': 'WsNoo_Stab_014100_014700', 'reinforcement_col': True, 'reference_year': 2025,
     'GROUND_IMPROVEMENT': True, 'GROUND_IMPROVEMENT_WITH_STABILITY_SCREEN': True,
     'GEOTEXTILE': True, 'DIAPHRAGM_WALL': True, 'STABILITY_SCREEN': True, 'ANCHORED_SHEETPILE': False,
     'REVETMENT': True,
     'CUSTOM': False},
    {'section_col': 'WsNoo_Stab_014700_015400', 'reinforcement_col': True, 'reference_year': 2025,
     'GROUND_IMPROVEMENT': True, 'GROUND_IMPROVEMENT_WITH_STABILITY_SCREEN': True,
     'GEOTEXTILE': True, 'DIAPHRAGM_WALL': True, 'STABILITY_SCREEN': True, 'ANCHORED_SHEETPILE': False,
     'REVETMENT': True,
     'CUSTOM': False},
    {'section_col': 'WsNoo_Stab_015400_016200', 'reinforcement_col': True, 'reference_year': 2025,
     'GROUND_IMPROVEMENT': True, 'GROUND_IMPROVEMENT_WITH_STABILITY_SCREEN': True,
     'GEOTEXTILE': True, 'DIAPHRAGM_WALL': True, 'STABILITY_SCREEN': True, 'ANCHORED_SHEETPILE': False,
     'REVETMENT': True,
     'CUSTOM': False},
    {'section_col': 'WsNoo_Stab_016200_017400', 'reinforcement_col': True, 'reference_year': 2025,
     'GROUND_IMPROVEMENT': True, 'GROUND_IMPROVEMENT_WITH_STABILITY_SCREEN': True,
     'GEOTEXTILE': True, 'DIAPHRAGM_WALL': True, 'STABILITY_SCREEN': True, 'ANCHORED_SHEETPILE': False,
     'REVETMENT': True,
     'CUSTOM': False},
    {'section_col': 'WsNoo_Stab_017400_018000', 'reinforcement_col': True, 'reference_year': 2025,
     'GROUND_IMPROVEMENT': True, 'GROUND_IMPROVEMENT_WITH_STABILITY_SCREEN': True,
     'GEOTEXTILE': True, 'DIAPHRAGM_WALL': True, 'STABILITY_SCREEN': True, 'ANCHORED_SHEETPILE': False,
     'REVETMENT': True,
     'CUSTOM': False}]

optimization_table_38_1 = [
    {'section_col': '2', 'reinforcement_col': True, 'reference_year': 2025, 'GROUND_IMPROVEMENT': True,
     'GROUND_IMPROVEMENT_WITH_STABILITY_SCREEN': True, 'GEOTEXTILE': True, 'DIAPHRAGM_WALL': False,
     'STABILITY_SCREEN': True, 'ANCHORED_SHEETPILE': False, 'REVETMENT': False, 'CUSTOM': False},
    {'section_col': '3', 'reinforcement_col': True, 'reference_year': 2025, 'GROUND_IMPROVEMENT': True,
     'GROUND_IMPROVEMENT_WITH_STABILITY_SCREEN': True, 'GEOTEXTILE': True, 'DIAPHRAGM_WALL': False,
     'STABILITY_SCREEN': True, 'ANCHORED_SHEETPILE': False, 'REVETMENT': False, 'CUSTOM': False},
    {'section_col': '4', 'reinforcement_col': True, 'reference_year': 2025, 'GROUND_IMPROVEMENT': True,
     'GROUND_IMPROVEMENT_WITH_STABILITY_SCREEN': True, 'GEOTEXTILE': True, 'DIAPHRAGM_WALL': False,
     'STABILITY_SCREEN': True, 'ANCHORED_SHEETPILE': False, 'REVETMENT': False, 'CUSTOM': False},
    {'section_col': '5', 'reinforcement_col': True, 'reference_year': 2025, 'GROUND_IMPROVEMENT': True,
     'GROUND_IMPROVEMENT_WITH_STABILITY_SCREEN': True, 'GEOTEXTILE': True, 'DIAPHRAGM_WALL': False,
     'STABILITY_SCREEN': True, 'ANCHORED_SHEETPILE': False, 'REVETMENT': False, 'CUSTOM': False},
    {'section_col': '6', 'reinforcement_col': True, 'reference_year': 2025, 'GROUND_IMPROVEMENT': True,
     'GROUND_IMPROVEMENT_WITH_STABILITY_SCREEN': True, 'GEOTEXTILE': True, 'DIAPHRAGM_WALL': False,
     'STABILITY_SCREEN': True, 'ANCHORED_SHEETPILE': False, 'REVETMENT': False, 'CUSTOM': False},
    {'section_col': '7', 'reinforcement_col': True, 'reference_year': 2025, 'GROUND_IMPROVEMENT': True,
     'GROUND_IMPROVEMENT_WITH_STABILITY_SCREEN': True, 'GEOTEXTILE': True, 'DIAPHRAGM_WALL': False,
     'STABILITY_SCREEN': True, 'ANCHORED_SHEETPILE': False, 'REVETMENT': False, 'CUSTOM': False},
    {'section_col': '8', 'reinforcement_col': True, 'reference_year': 2025, 'GROUND_IMPROVEMENT': True,
     'GROUND_IMPROVEMENT_WITH_STABILITY_SCREEN': True, 'GEOTEXTILE': True, 'DIAPHRAGM_WALL': False,
     'STABILITY_SCREEN': True, 'ANCHORED_SHEETPILE': False, 'REVETMENT': False, 'CUSTOM': False},
    {'section_col': '9', 'reinforcement_col': True, 'reference_year': 2025, 'GROUND_IMPROVEMENT': True,
     'GROUND_IMPROVEMENT_WITH_STABILITY_SCREEN': True, 'GEOTEXTILE': True, 'DIAPHRAGM_WALL': False,
     'STABILITY_SCREEN': True, 'ANCHORED_SHEETPILE': False, 'REVETMENT': False, 'CUSTOM': False},
    {'section_col': '10', 'reinforcement_col': True, 'reference_year': 2025, 'GROUND_IMPROVEMENT': True,
     'GROUND_IMPROVEMENT_WITH_STABILITY_SCREEN': True, 'GEOTEXTILE': True, 'DIAPHRAGM_WALL': False,
     'STABILITY_SCREEN': True, 'ANCHORED_SHEETPILE': False, 'REVETMENT': False, 'CUSTOM': False},
    {'section_col': '11', 'reinforcement_col': True, 'reference_year': 2025, 'GROUND_IMPROVEMENT': True,
     'GROUND_IMPROVEMENT_WITH_STABILITY_SCREEN': True, 'GEOTEXTILE': True, 'DIAPHRAGM_WALL': False,
     'STABILITY_SCREEN': True, 'ANCHORED_SHEETPILE': False, 'REVETMENT': False, 'CUSTOM': False}, ]

# class TestCallbackOptimize:
#
# @pytest.mark.skip(reason="can't test Background callback")
# @pytest.mark.slow
# def test_run_optimize_algorithm(self):
#     """
#     Test if the callback filling the DataTable with the selected traject from the database returns a list.
#     :return:
#     """
#     _dike_data = json.load(
#         open(Path(__file__).parent.parent / 'data/Case_38_1_sterker_VZG2/reference' / 'dike_data.json'))
#     _path_config = Path(__file__).parent.parent / 'data/TestCase1_38-1_no_housing_testingonly' / 'vr_config.json'
#
#     # load json:
#     with open(_path_config, 'r') as f:
#         decoded = f.read()
#         _vr_config = json.loads(decoded)
#
#     def run_callback():
#         return run_optimize_algorithm(
#             set_progress=None,
#             n_clicks=1,
#             optimization_run_name="nametest",
#             stored_data=_dike_data,
#             vr_config=_vr_config,
#             traject_optimization_table=optimization_table_1,
#         )
#
#     ctx = copy_context()
#     output = ctx.run(run_callback)
