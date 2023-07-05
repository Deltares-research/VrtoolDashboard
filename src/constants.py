from enum import Enum

REFERENCE_YEAR = 2025  #  Reference year for the reliability analysis





class CalcType(Enum):
    DOORSNEDE_EISEN = "Doorsnede-Eisen"
    VEILIGHEIDRENDEMENT = "Veiligheidsrendement"


class ResultType(Enum):
    RELIABILITY = "Betrouwbaarheid"
    PROBABILITY = "Faalkans"
    COST = "Kost"
    MEASURE = "Maatregel"