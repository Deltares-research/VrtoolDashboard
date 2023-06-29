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
        all_unzipped_files = parse_zip_content(contents, zipname)
        dike_sections = []
        for _, section in all_unzipped_files['traject_gdf'].iterrows():
            print(section['vaknaam'], section['in_analyse'])
            dike_sections.append(DikeSection(name=section['vaknaam'],
                                             coordinates_rd=section['geometry'],
                                             in_analyse=section['in_analyse']))

        return cls(name=zipname, dike_sections=[])
