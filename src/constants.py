from enum import Enum

REFERENCE_YEAR = 2025  # Reference year for the reliability analysis
ONDERGRENS = 1. / 10000
SIGNALERING = 1. / 30000

class CalcType(Enum):
    DOORSNEDE_EISEN = "Doorsnede-Eisen"
    VEILIGHEIDRENDEMENT = "Veiligheidsrendement"


class ResultType(Enum):
    RELIABILITY = "Betrouwbaarheid"
    PROBABILITY = "Faalkans"
    COST = "Kost"
    MEASURE = "Maatregel"


class SubResultType(Enum):
    ABSOLUTE = "Absoluut"
    DIFFERENCE = "Verschil vr - dsn"
    RATIO = "Verhouding vr / dsn"

class ColorBarResultType(Enum):
    RELIABILITY = "Betrouwbaarheid"
    COST = "Kost"
    MEASURE = "Maatregel"



class Mechanism(Enum):
    STABILITY = "Stabiliteit"
    PIPING = "Piping"
    OVERFLOW = "Overslag"
    SECTION = "Sectie"
