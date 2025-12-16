from enum import Enum
from pathlib import Path

REFERENCE_YEAR = 2025  # Reference year for the reliability analysis


class CalcType(Enum):
    DOORSNEDE_EISEN = "Doorsnede-Eisen"
    VEILIGHEIDSRENDEMENT = "Veiligheidsrendement"


class ResultType(Enum):
    RELIABILITY = "Betrouwbaarheid"
    PROBABILITY = "Faalkans"
    COST = "Kosten"
    MEASURE = "Maatregel"
    INTERPRETATION_CLASS = "Duidingsklassen"
    DISTANCE_TO_NORM = "Factor afstand tot norm"
    RISK = "Risico"
    RISK_FACTOR = "Risico factor"


class SubResultType(Enum):
    ABSOLUTE = "Absoluut"
    DIFFERENCE = "Verschil vr - dsn"
    RATIO = "Verhouding vr / dsn"
    MEASURE_TYPE = "Maatregeltype"
    BERM_WIDENING = "Bermverbreding"
    CREST_HIGHTENING = "Kruinverhoging"
    INVESTMENT_YEAR = "Investeringsjaar"


class ColorBarResultType(Enum):
    RELIABILITY = "Betrouwbaarheid"
    COST = "Kosten"
    MEASURE = "Maatregel"


class Mechanism(Enum):
    STABILITY = "Stabiliteit"
    PIPING = "Piping"
    OVERFLOW = "Overslag"
    SECTION = "Sectie"
    REVETMENT = "Bekleding"


class Measures(Enum):
    GROUND_IMPROVEMENT = "Grondversterking"
    GROUND_IMPROVEMENT_WITH_STABILITY_SCREEN = "Grondversterking met stabiliteitsscherm"
    STABILITY_SCREEN = "Stabiliteitsscherm"
    GEOTEXTILE = "Verticale Pipingoplossing"
    DIAPHRAGM_WALL = "Zelfkerende constructie"
    ANCHORED_SHEETPILE = "Verankerde damwand"
    REVETMENT = "Bekleding"
    CUSTOM = "Custom"


class GreedyOPtimizationCriteria(Enum):
    ECONOMIC_OPTIMAL = "Economisch optimaal (standaard)"
    TARGET_PF = "Faalkans"


class ProgramDefinitionMapType(Enum):
    SIMPLE = "Trajecten"
    PROJECTS = "Projecten"
    ASSESSMENT_PROBABILITIES = "Faalkans 2025"
    VEILIGHEIDSRENDEMENT_INDEX = "VR index"


conversion_dict_measure_names = {
    "GROUND_IMPROVEMENT": "Soil reinforcement",
    "GROUND_IMPROVEMENT_WITH_STABILITY_SCREEN": "Soil reinforcement with stability screen",
    "GEOTEXTILE": "Vertical Piping Solution",
    "DIAPHRAGM_WALL": "Diaphragm Wall",
    "STABILITY_SCREEN": "Stability Screen",
    "ANCHORED_SHEETPILE": "Anchored sheetpile",
    "REVETMENT": "Revetment",
    "CUSTOM": "Custom",
}

# PROJECTS_COLOR_SEQUENCE = ['rgb(214, 244, 134)',
#                            'rgb(79, 204, 40)',
#                            'rgb(84, 47, 106)',
#                            'rgb(15, 119, 142)',
#                            'rgb(190, 246, 250)',
#                            'rgb(32, 176, 13)',
#                            'rgb(46, 21, 211)',
#                            'rgb(192, 106, 84)',
#                            'rgb(148, 242, 52)',
#                            'rgb(67, 217, 250)']

import plotly.express as px

PROJECTS_COLOR_SEQUENCE = (
    px.colors.qualitative.Pastel + px.colors.qualitative.Prism
)  # this is 22 colors
CLASSIC_PLOTLY_COLOR_SEQUENCE = px.colors.qualitative.Plotly
