from vrtool.orm.models import OptimizationStep, OptimizationSelectedMeasure, Measure, MeasurePerSection, MeasureResult, \
    MeasureResultParameter, MeasureResultSection

from src.orm.importers.optimization_step_importer import _get_final_measure_betas
from src.utils.utils import beta_to_pf


def _get_investment_year(optimization_step: OptimizationStep) -> int:
    """
    Get the investment year of the optimization step.
    :param optimization_step: optimization step for which the investment year is retrieved.
    :return: investment year
    """
    _selected_optimization_measure = OptimizationSelectedMeasure.select().where(
        OptimizationSelectedMeasure.id == optimization_step.optimization_selected_measure_id).get()

    return _selected_optimization_measure.investment_year


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


def _get_combined_measure_name(optimization_step: OptimizationStep) -> str:
    if optimization_step.count() == 2:
        name = _get_single_measure(optimization_step[0]).name + " + " + _get_single_measure(
            optimization_step[1]).name
    elif optimization_step.count() == 3:
        name = _get_single_measure(optimization_step[0]).name + " + " + _get_single_measure(
            optimization_step[1]).name + " + " + _get_single_measure(optimization_step[2]).name
    else:
        raise ValueError()

    return name


def _get_investment_year(optimization_step: OptimizationStep) -> int:
    """
    Get the investment year of the optimization step.
    :param optimization_step: optimization step for which the investment year is retrieved.
    :return: investment year
    """
    _selected_optimization_measure = OptimizationSelectedMeasure.select().where(
        OptimizationSelectedMeasure.id == optimization_step.optimization_selected_measure_id).get()

    return _selected_optimization_measure.investment_year


def _get_combined_measure_investment_year(optimization_step: OptimizationStep) -> list[int]:
    if optimization_step.count() == 2:
        _year_1 = _get_investment_year(optimization_step[0])
        _year_2 = _get_investment_year(optimization_step[1])
        return [_year_1, _year_2]
    elif optimization_step.count() == 3:
        _year_1 = _get_investment_year(optimization_step[0])
        _year_2 = _get_investment_year(optimization_step[1])
        _year_3 = _get_investment_year(optimization_step[2])
        return [_year_1, _year_2, _year_3]

def _get_measure_cost(optimization_steps: OptimizationStep) -> float:

    cost = 0
    for optimum_step in optimization_steps:
        optimum_selected_measure = OptimizationSelectedMeasure.get(
            OptimizationSelectedMeasure.id == optimum_step.optimization_selected_measure_id)
        measure_result = MeasureResult.get(MeasureResult.id == optimum_selected_measure.measure_result_id)
        cost += MeasureResultSection.get(MeasureResultSection.measure_result == measure_result).cost
    return cost

def _get_measure_parameters(optimization_steps: OptimizationStep) -> dict:
    _params = {}

    for optimum_step in optimization_steps:

        optimum_selected_measure = OptimizationSelectedMeasure.get(
            OptimizationSelectedMeasure.id == optimum_step.optimization_selected_measure_id)
        measure_result = MeasureResult.get(MeasureResult.id == optimum_selected_measure.measure_result_id)

        params_dberm = MeasureResultParameter.select().where(
            (MeasureResultParameter.measure_result_id == measure_result.id) &
            (MeasureResultParameter.name == "DBERM")
        )
        params_dcrest = MeasureResultParameter.select().where(
            (MeasureResultParameter.measure_result_id == measure_result.id) &
            (MeasureResultParameter.name == "DCREST")
        )

        params_beta_target = MeasureResultParameter.select().where(
            (MeasureResultParameter.measure_result_id == measure_result.id) &
            (MeasureResultParameter.name == "BETA_TARGET")
        )
        params_transition_level = MeasureResultParameter.select().where(
            (MeasureResultParameter.measure_result_id == measure_result.id) &
            (MeasureResultParameter.name == "TRANSITION_LEVEL")
        )

        if _params.get('dberm') is None and params_dberm.count() > 0:
            _params['dberm'] = params_dberm[0].value
        if _params.get('dcrest') is None and params_dcrest.count() > 0:
            _params['dcrest'] = params_dcrest[0].value
        if _params.get('beta_target') is None and params_beta_target.count() > 0:
            _params['beta_target'] = params_beta_target[0].value
        if _params.get('transition_level') is None and params_transition_level.count() > 0:
            _params['transition_level'] = params_transition_level[0].value

        _params['pf_target_ratio'] = None
        _params['diff_transition_level'] = None

        # get the ratio of beta target and diff transition level when relevant
        if params_beta_target.count() > 0:
            _measure_per_section_id = MeasurePerSection.get(
                MeasurePerSection.id == measure_result.measure_per_section_id).id

            # get the measure result which has the same measure_per_section as the applied measure but with the
            # lowest beta target (this is the initial revetment measure)
            _ini_measure_result = MeasureResult.select().where(
                MeasureResult.measure_per_section_id == _measure_per_section_id).order_by(MeasureResult.id.asc())

            # Get the initial revetment parameters:
            ini_beta_target = MeasureResultParameter.select().where(
                (MeasureResultParameter.measure_result_id == _ini_measure_result) &
                (MeasureResultParameter.name == "BETA_TARGET")
            )
            ini_transition_level = MeasureResultParameter.select().where(
                (MeasureResultParameter.measure_result_id == _ini_measure_result) &
                (MeasureResultParameter.name == "TRANSITION_LEVEL")
            )

            _params['pf_target_ratio'] = round(
                beta_to_pf(ini_beta_target[0].value) / beta_to_pf(_params['beta_target']), 1)
            _params["diff_transition_level"] = _params['transition_level'] - ini_transition_level[0].value

    return _params


def _get_measure(optimization_steps, active_mechanisms: list) -> dict:
    """
    Retrieve from the database the information related to the selected optimization steps: betas, name, measure
    paramaters.
    :param optimization_steps:
    :return: dictionary with the followings keys: "name", "LCC", "Piping", "StabilityInner", "Overflow", "Revetment"
    , "Section"
    """
    # Get the betas for the measure:
    _final_measure = _get_final_measure_betas(optimization_steps, active_mechanisms)

    # Get the extra information measure name and the corresponding parameter values for the most (combined or not) optimal step
    if optimization_steps.count() == 1:
        _final_measure["name"] = _get_single_measure(optimization_steps[0]).name
        _final_measure['investment_year'] = [_get_investment_year(optimization_steps[0])]

    elif optimization_steps.count() in [2, 3]:
        _final_measure["name"] = _get_combined_measure_name(optimization_steps)
        _year_1 = _get_investment_year(optimization_steps[0])
        _year_2 = _get_investment_year(optimization_steps[1])
        _final_measure['investment_year'] = _get_combined_measure_investment_year(optimization_steps)

    else:
        raise ValueError(f"Unexpected number of optimum steps: {optimization_steps.count()}")
    _final_measure.update(_get_measure_parameters(optimization_steps))
    return _final_measure
