from typing import Optional

from src.linear_objects.base_linear import BaseLinearObject


class DikeSection(BaseLinearObject):
    coordinates_rd: list[tuple[float, float]]  # from parent class
    name: str
    in_analyse: bool
    is_reinforced: bool
    initial_assessment: dict
    final_measure_veiligheidrendement: Optional[dict]
    final_measure_doorsnede: Optional[dict]  # replace dict with a Measure Object

    def __init__(self, name: str, coordinates_rd: list[tuple[float, float]], in_analyse: bool):
        """
        :param name: name of the dike section
        :param coordinates_rd: list of tuples with the coordinates of the dike section in RD coordinates
        :param in_analyse: boolean indicating whether the dike section is in the analysis, i.e. whether its reliability
        is included in the reliability of the dike trajectory.
        """
        super().__init__(coordinates_rd)
        self.name = name
        self.in_analyse = in_analyse
        self.is_reinforced = False
        self.initial_assessment = {}
        self.final_measure_veiligheidrendement = None
        self.final_measure_doorsnede = None


    def serialize(self) -> dict:
        """Serialize the DikeSection object to a dict, in order to be saved in dcc.Store"""
        return {
            'coordinates_rd': self.coordinates_rd,
            'name': self.name,
            'in_analyse': self.in_analyse,
            'is_reinforced': self.is_reinforced,
            'initial_assessment': self.initial_assessment,
            'final_measure_veiligheidrendement': self.final_measure_veiligheidrendement,
            'final_measure_doorsnede': self.final_measure_doorsnede,
        }

    @staticmethod
    def deserialize(data: dict) -> 'DikeSection':
        """Deserialize the DikeSection object from a dict, in order to be loaded from dcc.Store

        :param data: serialized dict with the data of the DikeSection object

        """
        section = DikeSection(name=data['name'], in_analyse=data['in_analyse'], coordinates_rd=data['coordinates_rd'])
        section.initial_assessment = data['initial_assessment']
        section.is_reinforced = data['is_reinforced']
        section.final_measure_veiligheidrendement = data['final_measure_veiligheidrendement']
        section.final_measure = data['final_measure_doorsnede']
        return section

    def set_measure_and_reliabilities_from_csv(self, final_measure_dict: dict,
                                                   all_unzipped_files: dict, calc_type: str):

        if self.name in final_measure_dict.keys():
            self.is_reinforced = True

            # Parse csv of the final measure dataframe and add them to the DikeSection object
            _final_measure = final_measure_dict[self.name]

            # Parse csv of the Section results and add them to the DikeSection object
            _section_measure_betas = all_unzipped_files[f"DV{self.name}_Options_Doorsnede-eisen"]
            _final_measure["years"] = _section_measure_betas.iloc[
                0].dropna().unique()  # select the year for which the calculations were done

            _section_measure_betas = _section_measure_betas.loc[
                (_section_measure_betas.ID == _final_measure["ID"])
                & (_section_measure_betas["yes/no"] == _final_measure["yes/no"])
                & (_section_measure_betas.dcrest == _final_measure["dcrest"])
                & (_section_measure_betas.dberm == _final_measure["dberm"])
                ].squeeze()

            _mechanisms = ['Overflow', 'StabilityInner', 'Piping']
            for mechanism in _mechanisms:
                _final_measure[mechanism] = {key: _section_measure_betas[key] for key in
                                             _section_measure_betas.index if
                                             key.startswith(mechanism)}

            self.__setattr__(f"final_measure_{calc_type}", _final_measure)


