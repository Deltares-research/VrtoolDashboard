from dataclasses import dataclass

from src.linear_objects.base_linear import BaseLinearObject
from src.linear_objects.dike_section import DikeSection

from src.utils.importers import parse_zip_content


@dataclass
class DikeTraject(BaseLinearObject):
    name: str
    dike_sections: list[DikeSection]

    @classmethod
    def from_uploaded_zip(cls, contents: str, zipname: str):
        """ Create a DikeTraject object from the uploaded zip file"""
        _all_unzipped_files = parse_zip_content(contents, zipname)

        # Parse the csv of the final measures of Doorsnede-eisen and Veiligheidsrendement;
        _final_measure_dsn_dict = parse_final_measures_results(_all_unzipped_files,
                                                                     "FinalMeasures_Doorsnede-eisen")
        _final_measure_vr_dict = parse_final_measures_results(_all_unzipped_files, "FinalMeasures_Veiligheidsrendement")

        # Parse the geojson of the dike sections and add the final measures to the dike sections
        _dike_sections = []

        for _, section in _all_unzipped_files['traject_gdf'].iterrows():
            _section = DikeSection(name=section['vaknaam'],
                                   coordinates_rd=section['geometry'],
                                   in_analyse=section['in_analyse'],
                                   )

            if section['vaknaam'] in _final_measure_dsn_dict.keys():
                _section.is_reinforced = True
                _section.final_measure_doorsnede = _final_measure_dsn_dict[section['vaknaam']]
                _section.final_measure_veiligheidrendement = _final_measure_vr_dict[section['vaknaam']]

            _dike_sections.append(_section)

        return cls(name=zipname, dike_sections=_dike_sections)


    def serialize(self) -> dict:
        """Serialize the DikeTraject object to a dict, in order to be saved in dcc.Store"""
        return {
            'name': self.name,
            'dike_sections': [section.serialize() for section in self.dike_sections]
        }

    @staticmethod
    def deserialize(data: dict) -> 'DikeTraject':
        """
        Deserialize the DikeTraject object from a dict, in order to be loaded from dcc.Store
        #TODO: make it classmethod .from_dict()
        :param data: serialized dict with the data of the DikeTraject object
        """
        sections = [DikeSection.deserialize(section_data) for section_data in data['dike_sections']]
        return DikeTraject(name=data['name'], dike_sections=sections)


def parse_final_measures_results(all_unzipped_files: dict, filename: str) -> dict:
    """
    Parse the final measures results from the csv files in the zip file.
    :param all_unzipped_files: dict with all the unzipped files from the zip file
    :param filename: name of the csv file with the final measures results
    :return:
    """
    if filename not in all_unzipped_files.keys():
        raise ValueError(f'The zip file does not contain the required file: {filename}')
    final_measures_df = all_unzipped_files[filename]

    final_measures_df['Section'] = final_measures_df['Section'].str.replace('^DV', '',
                                                                            regex=True)  # remove DV from section names
    final_measures_df.set_index("Section", inplace=True)

    final_measure_dict = final_measures_df[["LCC", 'name']].to_dict(orient='index')
    return final_measure_dict
