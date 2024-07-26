from bisect import bisect_right
from typing import Optional

import numpy as np
import pandas as pd
from peewee import JOIN, ModelBase, DoesNotExist
from vrtool.orm.io.importers.optimization.optimization_step_importer import (
    OptimizationStepImporter,
)
from vrtool.orm.io.importers.orm_importer_protocol import OrmImporterProtocol
from vrtool.orm.models import (
    OptimizationStep,
    SectionData,
    MeasurePerSection,
    MeasureResult,
    OptimizationSelectedMeasure,
    Measure,
    MeasureResultParameter,
)

from src.constants import REFERENCE_YEAR, GreedyOPtimizationCriteria
from src.linear_objects.dike_section import DikeSection
from src.linear_objects.dike_traject import (
    DikeTraject,
    get_initial_assessment_df,
    get_traject_prob,
)
from src.orm.importers.importer_utils import (
    _get_single_measure,
    _get_investment_year,
    _get_combined_measure_name,
    _get_combined_measure_investment_year,
    _get_measure_parameters, _get_single_measure_type, _get_combined_measure_type,
)
from src.orm.importers.optimization_step_importer import (
    _get_section_lcc,
    _get_final_measure_betas,
)
from src.orm.orm_controller_custom import get_optimization_steps_ordered
from src.utils.utils import beta_to_pf, pf_to_beta


class TrajectSolutionRunImporter(OrmImporterProtocol):
    run_id_dsn: int  # run_id of the OptimizationRun for Doorsnede Eisen
    run_id_vr: int  # run_id of the OptimizationRun for Veiligheidsrendement
    assessment_time: list[int]
    greedy_optimization_criteria: str
    greedy_criteria_year: Optional[int]
    greedy_criteria_beta: Optional[float]
    economic_optimal_final_step_id: int
    final_step: int  # this is the step number of the last optimization step (either from the economic optimal or
    # the target beta/year, this needs to be returned to DikeTraject object)

    def __init__(
            self,
            dike_traject: DikeTraject,
            run_id_vr: int,
            run_id_dsn: int,
            greedy_optimization_criteria: str,
            greedy_criteria_year: Optional[int] = None,
            greedy_criteria_beta: Optional[float] = None,
            assessment_years: list[int] = None,
    ):
        self.dike_traject = dike_traject
        self.dike_section_mapping = {
            section.name: section for section in dike_traject.dike_sections
        }
        self.assessment_time = assessment_years
        self.run_id_dsn = run_id_dsn
        self.run_id_vr = run_id_vr
        self.greedy_optimization_criteria = greedy_optimization_criteria
        self.greedy_criteria_year = greedy_criteria_year
        self.greedy_criteria_beta = greedy_criteria_beta
        self.set_economic_optimal_final_step_id()

    def import_orm(self):
        """Import the final measures for both Veiligheidsrendement and Doorsnede"""
        self.get_final_measure_vr()
        self.get_final_measure_dsn()
        self.dike_traject.final_step_number = self.final_step

    def set_economic_optimal_final_step_id(self):
        """Get the final step id of the optimization run.
        The final step in this case is the step with the lowest total cost.

        :return: The id of the final step
        """

        _results = []
        try:
            _optimization_steps = get_optimization_steps_ordered(self.run_id_vr)
        except DoesNotExist:
            print("Warning: No optimization steps found for run_id: {self.run_id_vr}")
            return

        for _optimization_step in _optimization_steps:
            _as_df = OptimizationStepImporter.import_optimization_step_results_df(
                _optimization_step
            )
            _cost = _optimization_step.total_lcc + _optimization_step.total_risk
            _results.append((_optimization_step, _as_df, _cost))

        _step_id, _, _ = min(_results, key=lambda results_tuple: results_tuple[2])
        self.__setattr__("economic_optimal_final_step_id", _step_id.id)

    def get_final_measure_dsn(self):
        """
        Process the solution obtained for Doorsnede-eisen . In particular, this function:
            - gets and assigns the reinforcement order to the traject
            - import the final measure (beta, lcc, params, ...) for each dike section

        """

        try:
            _optimization_steps = get_optimization_steps_ordered(self.run_id_dsn)

        except DoesNotExist:
            print(f"No optimization steps found for run_id: {self.run_id_dsn}")
            return

        _iterated_step_number = []
        _ordered_reinforced_sections = []
        for _optimization_step in _optimization_steps:

            section = (
                SectionData.select()
                .join(MeasurePerSection)
                .join(MeasureResult)
                .join(OptimizationSelectedMeasure)
                .where(
                    OptimizationSelectedMeasure.id
                    == _optimization_step.optimization_selected_measure_id
                )
            ).get()

            # find corresponding section in dike_section
            dike_section: DikeSection = self.dike_section_mapping[section.section_name]

            # With this if statement, we avoid getting the combined measures multiple times
            if _optimization_step.step_number not in _iterated_step_number:
                _iterated_step_number.append(_optimization_step.step_number)

                _optimum_section_optimization_steps = (
                    OptimizationStep.select()
                    .join(OptimizationSelectedMeasure)
                    .where(
                        (
                                OptimizationSelectedMeasure.optimization_run
                                == self.run_id_dsn
                        )
                        & (
                                OptimizationStep.step_number
                                == _optimization_step.step_number
                        )
                    )
                )
                # 3. Get all information into a dict based on the optimum optimization steps.

                _step_measure = self._get_measure(
                    _optimum_section_optimization_steps,
                    active_mechanisms=dike_section.active_mechanisms,
                    assessment_time=self.assessment_time,
                )
                _step_measure["LCC"] = dike_section.final_measure_doorsnede["LCC"] = (
                    _get_section_lcc(_optimization_step)
                )
                dike_section.final_measure_doorsnede = _step_measure

                # 5. Append the reinforcement order dsn:
                self._get_reinforced_section_order(
                    _optimization_step, _ordered_reinforced_sections
                )
        self.dike_traject.reinforcement_order_dsn = _ordered_reinforced_sections

    def get_final_measure_vr(self):
        """
        Process the solution obtained for GreedyOptimization (veiligheidsrendement). In particular, this function:
            - gets and assigns the reinforcement order to the traject
            - import all the greedy steps and calculate the traject probability of failure (traject faalkans)
            - import the final measure (beta, lcc, params, ...) for each dike section

        """

        try:
            _optimization_steps = get_optimization_steps_ordered(self.run_id_vr)

        except DoesNotExist:
            return

        # 0. Initialize vars
        _previous_step_number = None
        _beta_df = get_initial_assessment_df(list(self.dike_section_mapping.values()))
        _traject_pf, _ = get_traject_prob(_beta_df)
        _greedy_steps_res = [{"pf": _traject_pf[0].tolist(), "LCC": 0}]
        _ordered_reinforced_sections = []

        _recorded__previous_section_LCC = {}

        for _optimization_step in _optimization_steps:
            _step_number = _optimization_step.step_number

            # For combined steps sharing the same step number, skip the step if it has already been processed
            if _previous_step_number == _step_number:
                continue

            section = (
                SectionData.select()
                .join(MeasurePerSection)
                .join(MeasureResult)
                .join(OptimizationSelectedMeasure)
                .where(
                    OptimizationSelectedMeasure.id
                    == _optimization_step.optimization_selected_measure_id
                )
            ).get()

            # find corresponding section in dike_section
            dike_section: DikeSection = self.dike_section_mapping[section.section_name]

            # 2. Get all steps sharing the same step number (=combined steps)
            _optimum_section_optimization_steps = (
                OptimizationStep.select()
                .join(OptimizationSelectedMeasure)
                .where(
                    (OptimizationSelectedMeasure.optimization_run == self.run_id_vr)
                    & (OptimizationStep.step_number == _optimization_step.step_number)
                )
            )

            # 3. Get all information into a dict based on the optimum optimization steps.
            _step_measure = self._get_measure(
                _optimum_section_optimization_steps,
                active_mechanisms=dike_section.active_mechanisms,
                assessment_time=self.assessment_time,
            )
            _step_measure["LCC"] = _get_section_lcc(_optimization_step)

            dike_section.final_measure_veiligheidsrendement = _step_measure

            # 4. Calculate the traject probability of failure for the current step
            self._add_greedy_step(
                dike_section,
                _optimization_step,
                _beta_df,
                _greedy_steps_res,
                _step_measure,
                _recorded__previous_section_LCC,
            )

            # 5. Append the reinforcement order vr:
            self._get_reinforced_section_order(
                _optimization_step, _ordered_reinforced_sections
            )

            status_step = self.continue_next_step(
                _optimization_step, _greedy_steps_res[-1]["pf"]
            )
            _previous_step_number = _step_number
            _recorded__previous_section_LCC[dike_section.name] = _step_measure["LCC"]

            if status_step == False:
                _the_final_step = _optimization_step.step_number
                self.__setattr__("final_step", _the_final_step)
                break

        self.dike_traject.greedy_steps = _greedy_steps_res
        self.dike_traject.reinforcement_order_vr = _ordered_reinforced_sections

    def continue_next_step(
            self, optimization_step: OptimizationStep, traject_pf: list[float]
    ) -> bool:
        """
        This function determines whether the next OptimizationStep should be imported/processed or not.
            - If criteria is Economic Optimal, the loop should be stop when the id of the economic optimal is reached
            (id previously determined at the step of lowest Total Cost).
            - If criteria is determined for a tuple beta/year. the loop stops when the traject faalkans reaches the
            specified reliability beta for a specified year.

        :param optimization_step: optimization step to be iterated from the osm table
        :param traject_pf: list of the traject faalkans for all years computed for the current optimization step

        :return: True if the next optimization step should be processed. False otherwise.

        """

        if (
                self.greedy_optimization_criteria
                == GreedyOPtimizationCriteria.ECONOMIC_OPTIMAL.name
        ):
            if optimization_step.id + 1 > self.economic_optimal_final_step_id:
                return False
            return True

        elif (
                self.greedy_optimization_criteria
                == GreedyOPtimizationCriteria.TARGET_PF.name
        ):

            _year_step_index = (
                    bisect_right(
                        self.assessment_time, self.greedy_criteria_year - REFERENCE_YEAR
                    )
                    - 1
            )
            pf_traject_stop = traject_pf[_year_step_index]
            beta_traject_stop = pf_to_beta(pf_traject_stop)
            if beta_traject_stop > self.greedy_criteria_beta:
                return False
            return True

    def _add_greedy_step(
            self,
            dike_section: DikeSection,
            optimization_step: OptimizationStep,
            _beta_df: pd.DataFrame,
            greedy_steps_res: list[dict],
            step_measure: dict,
            recorded__previous_section_LCC: dict[str, float],
    ):
        """
        Add the results of the step to the list greedy_steps_list

        :param dike_section:
        :param optimization_step: optimization step to be iterated from the osm table
        :param _beta_df: dataframe with beta of all mechanism and all sections. The dataframe is modified in place here!
        :param greedy_steps_res: result list to be appended. Element have the following structure:
        :param step_measure: current state of the measure dictionary. it contains the beta for the considered
        mechanisms
        :param recorded__previous_section_LCC: dictionary that stores the previous LCC of the section. This is needed
        because the LCC stored in the database is the accumulated LCC for the measure of the section. To retrieve the
        incremental increase from the step, it is required to keep the LCC of the previous step of the same section.
        {"LCC": xxx, "pf": [X,Y,Z]}

        """
        for mechanism in dike_section.active_mechanisms:
            mask = (_beta_df["name"] == dike_section.name) & (
                    _beta_df["mechanism"] == mechanism
            )

            for year, beta in zip(dike_section.years, step_measure[mechanism]):
                _beta_df.loc[mask, year] = beta

        # Calculate traject faalkans
        _reinforced_traject_pf, _ = get_traject_prob(_beta_df)

        # Get step LCC:
        LCC = _get_section_lcc(optimization_step) - recorded__previous_section_LCC.get(
            dike_section.name, 0
        )
        greedy_steps_res.append({"pf": _reinforced_traject_pf[0].tolist(), "LCC": LCC})

    def _get_reinforced_section_order(
            self, optimization_step: OptimizationStep, section_ordered_list: list[str]
    ):
        """Add in place the section name to the list of reinforced sections if it is not already in the list."""
        optimization_selected_measure = OptimizationSelectedMeasure.get(
            OptimizationSelectedMeasure.id
            == optimization_step.optimization_selected_measure_id
        )
        measure_result = MeasureResult.get(
            MeasureResult.id == optimization_selected_measure.measure_result_id
        )
        measure_per_section = MeasurePerSection.get(
            MeasurePerSection.id == measure_result.measure_per_section_id
        )
        section = SectionData.get(SectionData.id == measure_per_section.section_id)
        if section.section_name not in section_ordered_list:
            section_ordered_list.append(section.section_name)

    @staticmethod
    def _get_measure(optimization_steps, active_mechanisms: list, assessment_time) -> dict:
        """
        Retrieve from the database the information related to the selected optimization steps: betas, name, measure
        paramaters.
        :param optimization_steps:
        :return: dictionary with the followings keys: "name", "LCC", "Piping", "StabilityInner", "Overflow", "Revetment"
        , "Section"
        """

        # Get the betas for the measure:
        _final_measure = _get_final_measure_betas(optimization_steps, active_mechanisms, assessment_time)

        # Get the extra information measure name and the corresponding parameter values for the most (combined or not) optimal step
        if optimization_steps.count() == 1:
            _final_measure["name"] = _get_single_measure(optimization_steps[0]).name
            _final_measure["investment_year"] = [
                _get_investment_year(optimization_steps[0])
            ]
            _final_measure["type"] = [_get_single_measure_type(optimization_steps[0]).name]

        elif optimization_steps.count() in [2, 3]:
            _final_measure["name"] = _get_combined_measure_name(optimization_steps)
            _year_1 = _get_investment_year(optimization_steps[0])
            _year_2 = _get_investment_year(optimization_steps[1])
            _final_measure["investment_year"] = _get_combined_measure_investment_year(
                optimization_steps
            )
            _final_measure["type"] = _get_combined_measure_type(optimization_steps)

        else:
            raise ValueError(
                f"Unexpected number of optimum steps: {optimization_steps.count()}"
            )
        _final_measure.update(_get_measure_parameters(optimization_steps))
        return _final_measure
