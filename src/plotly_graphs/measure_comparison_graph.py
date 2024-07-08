import numpy as np
import plotly.graph_objects as go
from pandas import DataFrame

from src.constants import CalcType, Mechanism


def plot_measure_results_graph(
        measure_results: DataFrame,
        vr_steps: list[dict],
        dsn_steps: list[dict],
        mechanism: Mechanism,
        section_name: str,
        year_index: int,
) -> go.Figure:
    """
    Make the plot Beta vs cost comparing all the measures for a dike section.
    
    :param measure_results: Dataframe containing the data (beta,LCC) for all the filtered measures from a dijkvak
    :param vr_steps: list of all the step measures for GreedyOptimization (veiligheidsrendement)
    :param dsn_steps: the single step measure for Doorsnede-eis.
    :param mechanism: Mechanism for which to display the beta.
    :param section_name: name of the section
    :param year_index: year index for the measures. Betas are stored in a list, to retrieve the correct beta for the selected year with th slider, it is necessary to provide the year index.
    :return: 
    """ ""
    fig = go.Figure()

    # Add traces for the measures (uncombined)
    custom = np.stack(
        (
            measure_results["measure"],
            measure_results.get("dberm", None),
            measure_results.get("dcrest", None),
            measure_results.get("measure_result_id", None)  # keep this for the clickData event
        ),
        axis=-1,
    )

    fig.add_trace(
        go.Scatter(
            name="Maatregelen",
            x=measure_results["LCC"] / 1e6,
            y=measure_results["beta"],
            customdata=custom,
            mode="markers",
            marker=dict(
                size=8,
                color="black",
            ),
            hovertemplate="<b>%{customdata[0]}</b><br><br>"
                          + "Dberm: %{customdata[1]}m<br>"
                          + "Dcrest: %{customdata[2]}m<br>"
                          + "Beta: %{y:.2f}<br>"
                          + "LCC: €%{x:.2f} mln<br>",
        )
    )

    # # Add traces for the final measures
    add_trace_run_results(
        fig, dsn_steps, CalcType.DOORSNEDE_EISEN, mechanism, year_index
    )
    add_trace_run_results(
        fig, vr_steps, CalcType.VEILIGHEIDSRENDEMENT, mechanism, year_index
    )

    ## Update layout
    fig.update_layout(
        title=f"Maatregelen dijkvak {section_name} {mechanism}",
        xaxis_title="Kost (mln €)",
        yaxis_title="Beta",
        template="ggplot2",
    )

    return fig


def add_trace_run_results(
        fig: go.Figure,
        step_measures: list[dict],
        calc_type: CalcType,
        mechanism: Mechanism,
        year_index: int,
):
    """
    Add traces for the provided step_measures (either Veiligheidsrendement or doorsnede)
    :param fig:
    :param step_measures:
    :param calc_type:
    :param mechanism:
    :param year_index:
    :return:
    """

    for step_number, taken_measure in enumerate(step_measures):

        # add to custom data the measure_results_ids as a concatenated string "54 + 535 + 23" so that the data can be
        # retrieved in the clickData event
        concatenated_ids = " + ".join(map(str, taken_measure["measure_results_ids"]))
        custom_data = np.stack((concatenated_ids,), axis=-1)


        if taken_measure["name"] == "Geen maatregel":
            hover_extra = ""
        else:
            hover_extra = (
                    f"Dberm: {taken_measure.get('dberm', None)}m<br>"
                    + f"Dcrest: {taken_measure.get('dcrest', None)}m<br>"
            )

        if calc_type == CalcType.VEILIGHEIDSRENDEMENT:
            name = "Veiligheidsrendement"
            color = "green" if step_number != len(step_measures) - 1 else "red"

            legendgroup = "Veiligheidsrendement"
        elif calc_type == CalcType.DOORSNEDE_EISEN:
            name = "Doorsnede"
            color = "blue"
            legendgroup = "Doorsnede"
        else:
            raise ValueError(f"CalcType {calc_type} not recognized")

        if mechanism.upper() == Mechanism.SECTION.name:
            mech_key = "Section"
        elif mechanism.upper() == Mechanism.STABILITY.name:
            mech_key = "StabilityInner"
        elif mechanism.upper() == Mechanism.PIPING.name:
            mech_key = "Piping"
        elif mechanism.upper() == Mechanism.OVERFLOW.name:
            mech_key = "Overflow"
        elif mechanism.upper() == Mechanism.REVETMENT.name:
            mech_key = "Revetment"
        else:
            raise NotImplementedError(f"Mechanism {mechanism} not implemented")
        fig.add_trace(
            go.Scatter(
                name=name,
                legendgroup=legendgroup,
                showlegend=True if step_number == 0 else False,
                x=[taken_measure["cost"] / 1e6],
                y=[taken_measure[mech_key][year_index]],
                customdata=custom_data,
                mode="markers",
                marker=dict(
                    size=10 if step_number == len(step_measures) - 1 else 8,
                    color=color,
                    symbol=(
                        "diamond" if step_number == len(step_measures) - 1 else "circle"
                    ),
                ),
                hovertemplate=f"<b>Stap {step_number} {taken_measure['name']}</b><br><br>"
                              + f"Investment year: {taken_measure['investment_year']}<br>"
                              + "Beta: %{y:.2f}<br>"
                              + "Cost: €%{x:.2f} mln<br>"
                              + hover_extra,
            )
        )

        fig.add_annotation(
            text=f"{step_number}",
            x=taken_measure["cost"] / 1e6,
            y=taken_measure[mech_key][year_index],
        )
