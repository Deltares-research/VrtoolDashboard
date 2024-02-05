from typing import Iterator

import numpy as np
from peewee import JOIN

from vrtool.orm.models import Mechanism, MechanismPerSection, ComputationScenario, MeasurePerSection, Measure, \
    OptimizationStep, OptimizationRun, OptimizationStepResultMechanism, OptimizationStepResultSection, \
    OptimizationSelectedMeasure, OptimizationType, MeasureResult, MeasureResultParameter, MeasureResultSection, \
    StandardMeasure, MeasureType
from vrtool.probabilistic_tools.combin_functions import CombinFunctions
from vrtool.probabilistic_tools.probabilistic_functions import beta_to_pf, pf_to_beta

from src.orm import models as orm



def _get_final_measure_betas(optimization_steps: OptimizationStep, active_mechanisms: list[str]) -> dict:
    _final_measure = {}
    _dict_probabilities = {}

    if optimization_steps.count() == 1:

        # for mechanism_per_section in mechanisms_per_section:
        for mechanism in active_mechanisms:
            _final_measure[mechanism] = [row.beta for row in
                                         _get_mechanism_beta(optimization_steps[0], mechanism)]
        # Add section betas as well:
        _final_measure["Section"] = [row.beta for row in _get_section_betas(optimization_steps[0])]

        return _final_measure


    elif optimization_steps.count() in [2, 3]:
        _final_measure = _get_final_measure_combined_betas(optimization_steps, active_mechanisms)

        return _final_measure
    elif optimization_steps.count() > 3:
        raise ValueError("No more than 2 measure results is allowed")
    else:
        raise ValueError("No measure results found")


def _get_mechanism_beta(optimization_step: OptimizationStep, mechanism: str) -> Iterator[
    orm.OptimizationStepResultMechanism]:
    """
    Get the beta values for a mechanism for a given optimization step
    :param optimization_step: optimization step for which the betas are retrieved
    :param mechanism: string name of the mechanism
    :return:

    """
    _query = (OptimizationStepResultMechanism
              .select(OptimizationStepResultMechanism.beta)
              .join(MechanismPerSection, JOIN.INNER,
                    on=(OptimizationStepResultMechanism.mechanism_per_section == MechanismPerSection.id))
              .join(Mechanism, JOIN.INNER,
                    on=(MechanismPerSection.mechanism_id == Mechanism.id))
              .where((Mechanism.name == mechanism) & (
            OptimizationStepResultMechanism.optimization_step_id == optimization_step.id)))

    return _query


def _get_section_betas(optimization_step: OptimizationStep) -> Iterator[orm.OptimizationStepResultSection]:
    """
    Get the beta values for the section for a given optimization step
    :param optimization_step:  optimization step for which the betas are retrieved
    :return:
    """
    _query = (OptimizationStepResultSection
              .select(OptimizationStepResultSection.beta)
              .where(OptimizationStepResultSection.optimization_step_id == optimization_step.id))
    return _query


def _get_final_measure_combined_betas(optimization_steps: OptimizationStep, active_mechanisms: list[str]) -> dict:
    """
    Combine the mechanism probabilities from a Combinable+Partial measure set. And compute the section betas.
    :param optimization_steps:
    :return:
    """
    _final_measure = {}
    _dict_probabilities = {}

    # find which optimization step is the soil reinforcement or vzg or revetment
    soil_reinforcement_step, vzg_step, revetment_step, diaphram_wall_step, stability_screen_step = None, None, None, None, None
    for optimization_step in optimization_steps:
        _measure_type = _get_mesure_type_from_optimization_step(optimization_step)
        if _measure_type.name in ["Soil reinforcement", "Soil reinforcement with stability screen"]:
            soil_reinforcement_step = optimization_step
        elif _measure_type.name in ["Vertical Geotextile"]:
            vzg_step = optimization_step
        elif _measure_type.name in ["Revetment"]:
            revetment_step = optimization_step
        elif _measure_type.name in ["Diaphragm Wall"]:
            diaphram_wall_step = optimization_step
        elif _measure_type.name in ["Stability Screen"]:
            stability_screen_step = optimization_step

    # Assign the mechanism betas according to the right optimization step(s):
    for mechanism in active_mechanisms:

        if mechanism == "Stability Screen" and stability_screen_step is not None:
            _betas = np.array([row.beta for row in
                               _get_mechanism_beta(stability_screen_step, mechanism)])
            _final_measure[mechanism] = _betas
            _dict_probabilities[mechanism] = beta_to_pf(_betas)
            continue

        if diaphram_wall_step is not None and mechanism != "Revetment":
            _betas = np.array([row.beta for row in
                               _get_mechanism_beta(diaphram_wall_step, mechanism)])
            _final_measure[mechanism] = _betas
            _dict_probabilities[mechanism] = beta_to_pf(_betas)
            continue

        if revetment_step is not None and mechanism != "Revetment" and vzg_step is None and soil_reinforcement_step is None:
            _betas = np.array([row.beta for row in
                               _get_mechanism_beta(revetment_step, mechanism)])
            _final_measure[mechanism] = _betas
            _dict_probabilities[mechanism] = beta_to_pf(_betas)
            continue

        if mechanism == "Revetment" and revetment_step is not None:
            _betas_revetment = np.array(
                [row.beta for row in _get_mechanism_beta(revetment_step, mechanism)])
            _final_measure[mechanism] = _betas_revetment
            _dict_probabilities[mechanism] = beta_to_pf(_betas_revetment)
            continue  # don't need to go further

        if mechanism == "Piping" and vzg_step is not None and soil_reinforcement_step is not None:
            _pf_solution_failure, _pf_with_solution = _get_vzg_parameters()
            _betas_soil_reinforcement = np.array(
                [row.beta for row in _get_mechanism_beta(soil_reinforcement_step, mechanism)])
            _pf_soil_reinforcement = beta_to_pf(_betas_soil_reinforcement)
            _pf_combined_solutions = _pf_solution_failure * _pf_soil_reinforcement + (
                    1 - _pf_solution_failure) * _pf_with_solution
            _beta_combined_solutions = pf_to_beta(_pf_combined_solutions)
            _final_measure[mechanism] = _beta_combined_solutions
            _dict_probabilities[mechanism] = _pf_combined_solutions
            continue

        if vzg_step is not None and soil_reinforcement_step is not None:
            _betas_soil_reinforcement = np.array([row.beta for row in
                                                  _get_mechanism_beta(soil_reinforcement_step, mechanism)])
            _betas_vzg = np.array([row.beta for row in
                                   _get_mechanism_beta(vzg_step, mechanism)])

            _beta_combined_solutions = np.maximum(
                _betas_soil_reinforcement,
                _betas_vzg
            )
            _final_measure[mechanism] = _beta_combined_solutions
            _pf_combined_solutions = beta_to_pf(_beta_combined_solutions)
            _dict_probabilities[mechanism] = _pf_combined_solutions
            continue

        if vzg_step is not None and soil_reinforcement_step is None:
            _betas = np.array([row.beta for row in _get_mechanism_beta(vzg_step, mechanism)])
            _final_measure[mechanism] = _betas
            _dict_probabilities[mechanism] = beta_to_pf(_betas)
            continue

        if soil_reinforcement_step is not None and vzg_step is None:
            _betas = np.array([row.beta for row in
                               _get_mechanism_beta(soil_reinforcement_step, mechanism)])
            _final_measure[mechanism] = _betas
            _dict_probabilities[mechanism] = beta_to_pf(_betas)
            continue

        # raise ValueError("Error, configuration to be implemented")

    section = CombinFunctions.combine_probabilities(_dict_probabilities, tuple(_dict_probabilities.keys()))

    # Add section betas as well: You need to redo product of betas here:

    _final_measure["Section"] = [pf_to_beta(pf_section) for pf_section in section]

    return _final_measure


def _get_vzg_parameters() -> tuple[float, float]:
    _vzg_params = (StandardMeasure.select(StandardMeasure.prob_of_solution_failure,
                                          StandardMeasure.failure_probability_with_solution)
    .join(Measure)
    .join(MeasureType)
    .where(
        (Measure.combinable_type_id == 3) &
        (MeasureType.name == "Vertical Geotextile")

    )
    ).get()

    return _vzg_params.prob_of_solution_failure, _vzg_params.failure_probability_with_solution


def _get_mesure_type_from_optimization_step(optimization_step: OptimizationStep) -> MeasureType:
    """
    Get the measure type from the optimization step
    :param optimization_step:
    :return:
    """
    measure = _get_single_measure(optimization_step)

    measure_type = MeasureType.get(MeasureType.id == measure.measure_type_id)

    return measure_type


def _get_single_measure(optimization_step: OptimizationStep) -> Measure:
    """Return the measure associated with a given single optimization step"""

    measure = (Measure
               .select()
               .join(MeasurePerSection)
               .join(MeasureResult)
               .join(OptimizationSelectedMeasure)
               .where(OptimizationSelectedMeasure.id == optimization_step.optimization_selected_measure_id)
               .get())

    return measure
