from typing import Optional

from pandas import DataFrame

from src.linear_objects.base_linear import BaseLinearObject


class DikeSection(BaseLinearObject):
    coordinates_rd: list[tuple[float, float]]  # from parent class
    name: str
    length: float
    in_analyse: bool
    is_reinforced_veiligheidsrendement: bool
    is_reinforced_doorsnede: bool
    initial_assessment: Optional[dict]
    final_measure_veiligheidsrendement: Optional[dict]
    final_measure_doorsnede: Optional[dict]  # replace dict with a Measure Object
    years: list[int]  # Years for which a reliability result is available (both for initial and measures)

    def __init__(self, name: str, coordinates_rd: list[tuple[float, float]], in_analyse: int):
        """
        :param name: name of the dike section
        :param coordinates_rd: list of tuples with the coordinates of the dike section in RD coordinates
        :param in_analyse: boolean indicating whether the dike section is in the analysis, i.e. whether its reliability
        is included in the reliability of the dike trajectory.
        """
        super().__init__(coordinates_rd)
        self.name = str(name)
        self.in_analyse = True if in_analyse == 1 else False
        self.length = -999
        self.is_reinforced_veiligheidsrendement = False
        self.is_reinforced_doorsnede = False
        self.initial_assessment = None
        self.final_measure_veiligheidsrendement = None
        self.final_measure_doorsnede = None
        self.years = []

    def serialize(self) -> dict:
        """Serialize the DikeSection object to a dict, in order to be saved in dcc.Store"""
        return {
            'coordinates_rd': self.coordinates_rd,
            'name': self.name,
            'length': self.length,
            'in_analyse': self.in_analyse,
            'is_reinforced_veiligheidsrendement': self.is_reinforced_veiligheidsrendement,
            'is_reinforced_doorsnede': self.is_reinforced_doorsnede,
            'initial_assessment': self.initial_assessment,
            'final_measure_veiligheidsrendement': self.final_measure_veiligheidsrendement,
            'final_measure_doorsnede': self.final_measure_doorsnede,
            'years': self.years
        }

    @staticmethod
    def deserialize(data: dict) -> 'DikeSection':
        """Deserialize the DikeSection object from a dict, in order to be loaded from dcc.Store

        :param data: serialized dict with the data of the DikeSection object

        """
        section = DikeSection(name=data['name'], in_analyse=data['in_analyse'], coordinates_rd=data['coordinates_rd'])
        section.length = data['length']
        section.initial_assessment = data['initial_assessment']
        section.is_reinforced_doorsnede = data['is_reinforced_veiligheidsrendement']
        section.is_reinforced_veiligheidsrendement = data['is_reinforced_doorsnede']
        section.final_measure_veiligheidsrendement = data['final_measure_veiligheidsrendement']
        section.final_measure_doorsnede = data['final_measure_doorsnede']
        section.years = data['years']
        return section

    def set_measure_and_reliabilities_from_csv(self, _measure_dict: dict,
                                                   all_unzipped_files: dict, calc_type: str) -> None:
        """
        Set the measure to the dike section object and set its corresponding reliabilities for all mechanisms for all
        the years for which the calculations were done.

        :param _measure_dict: measure dictionary parsed and filtered from a TakenMeasures.csv or FinalMeasures.csv
        :param all_unzipped_files: dictionary with all the unzipped files from the zip file
        :param calc_type: type of calculation, either "doorsnede" or "veiligheidsrendement

        """

        if self.name in _measure_dict.keys():
            _mechanisms = ["Overflow", "StabilityInner", "Piping", "Section"]
            # Parse csv of the (optimal) measure dataframe and add them to the DikeSection object
            _final_measure = _measure_dict[self.name]
            if _final_measure["name"] == "No measure":
                #set to No measure with initial assessment for betas
                for mechanism in _mechanisms:
                    _final_measure[mechanism] = self.initial_assessment[mechanism]
                self.__setattr__(f"final_measure_{calc_type}", _final_measure)
                return

            if calc_type == "doorsnede":
                self.is_reinforced_doorsnede = True
            elif calc_type == 'veiligheidsrendement':
                self.is_reinforced_veiligheidsrendement = True

            _option = "Doorsnede-eisen" if calc_type == "doorsnede" else "Veiligheidsrendement"

            # Parse csv of the Section results and add them to the DikeSection object
            _section_measure_betas = all_unzipped_files[f"{self.name}_Options_{_option}"]
            self.years = _section_measure_betas.iloc[
                0].dropna().unique()  # select the year for which the calculations were done
            _section_measure_betas = _section_measure_betas.loc[
                (_section_measure_betas.ID == _final_measure["ID"])
                & (_section_measure_betas["yes/no"] == _final_measure["yes/no"])
                & (_section_measure_betas.dcrest == _final_measure["dcrest"])
                & (_section_measure_betas.dberm == _final_measure["dberm"])
                ].squeeze()

            for mechanism in _mechanisms:
                _final_measure[mechanism] = [_section_measure_betas[key] for key in
                                             _section_measure_betas.index if
                                             key.startswith(mechanism)]
            self.__setattr__(f"final_measure_{calc_type}", _final_measure)

    def set_initial_assessment_from_csv(self, initial_assessment_df: DataFrame) -> None:
        """
        Set the initial assessment of the dike section object from the initial assessment dataframe.
        Also set the length of the section because it is only available in the initial assessment dataframe.
        :param initial_assessment_df: Dataframe containing the initial reliability of all dike sections for all
        mechanisms for all years.
        :return:
        """
        _section_initial_betas_df = initial_assessment_df.loc[initial_assessment_df["name"] == f"{self.name}"].squeeze()
        if not _section_initial_betas_df.empty:  # if df is empty, then section is not reinforced and skipped.
            _initial_assessment_dict = {}
            _mechanisms = ["Overflow", "StabilityInner", "Piping", "Section"]
            _years = _section_initial_betas_df.columns[2:-1].tolist()  # last column is Length and should be removed
            for mechanism in _mechanisms:
                _initial_assessment_dict[mechanism] = _section_initial_betas_df[_section_initial_betas_df["mechanism"] == mechanism].iloc[:, 2:-1].values.tolist()[0]
            self.__setattr__(f"initial_assessment", _initial_assessment_dict)
            self.__setattr__(f"length", _section_initial_betas_df["Length"].iloc[0])

