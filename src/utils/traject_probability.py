import pandas as pd

from src.linear_objects.dike_section import DikeSection


def get_updated_beta_df(dike_sections: list[DikeSection], beta_df: pd.DataFrame) -> pd.DataFrame:
    if len(dike_sections) == 0:
        return beta_df

    years = dike_sections[0].years

    for section in dike_sections:

        if not section.in_analyse:  # skip if the section is not reinforced
            continue

        if (
                not section.is_reinforced_veiligheidsrendement
        ):  # skip if the section is not reinforced
            continue
        _active_mechanisms = ["Overflow", "Piping", "StabilityInner"]
        if section.revetment:
            _active_mechanisms.append("Revetment")
        # add a row to the dataframe with the initial assessment of the section
        for mechanism in _active_mechanisms:
            mask = (beta_df["name"] == section.name) & (
                    beta_df["mechanism"] == mechanism
            )
            # replace the row in the dataframe with the betas of the section if both the name and mechanism match

            for year, beta in zip(
                    years, getattr(section, "final_measure_veiligheidsrendement")[mechanism]
            ):
                beta_df.loc[mask, year] = beta

    return beta_df