from enum import Enum
from pathlib import Path

REFERENCE_YEAR = 2025  # Reference year for the reliability analysis
ONDERGRENS = 1. / 10000
SIGNALERING = 1. / 30000


class CalcType(Enum):
    DOORSNEDE_EISEN = "Doorsnede-Eisen"
    VEILIGHEIDSRENDEMENT = "Veiligheidsrendement"


class ResultType(Enum):
    RELIABILITY = "Betrouwbaarheid"
    PROBABILITY = "Faalkans"
    COST = "Kosten"
    MEASURE = "Maatregel"


class SubResultType(Enum):
    ABSOLUTE = "Absoluut"
    DIFFERENCE = "Verschil vr - dsn"
    RATIO = "Verhouding vr / dsn"
    MEASURE_TYPE = "Maatregeltype"
    BERM_WIDENING = "Bermverbreding"
    CREST_HIGHTENING = "Kruinverhoging"


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


def get_mapbox_token() -> str:
    with open(Path(__file__).parent / "assets" / "mapbox_token.txt") as f:
        return f.read()
