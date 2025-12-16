import pandas as pd
from vrtool.defaults.vrtool_config import VrtoolConfig
from vrtool.orm import models as orm
from vrtool.orm.io.importers.optimization.optimization_step_importer import (
    OptimizationStepImporter,
)
from vrtool.orm.orm_controllers import get_optimization_steps, open_database


def get_optimization_step_with_lowest_total_cost_no_closing(
    vrtool_config: VrtoolConfig, optimization_run_id: int
) -> tuple[orm.OptimizationStep, pd.DataFrame, float]:
    """
    Gets the `OptimizationStep` with the lowest *total* cost.
    The total cost is calculated based on `LCC` and risk.

    Args:
        vrtool_db_path (Path): Sqlite database path.

    Returns:
        orm.OptimizationStep: The `OptimizationStep` instance with the lowest *total* cost
    """

    _results = []
    _optimization_steps = get_optimization_steps_ordered(optimization_run_id)

    for _optimization_step in _optimization_steps:
        _as_df = OptimizationStepImporter.import_optimization_step_results_df(
            _optimization_step
        )
        _cost = _optimization_step.total_lcc + _optimization_step.total_risk
        _results.append((_optimization_step, _as_df, _cost))

    return min(_results, key=lambda results_tuple: results_tuple[2])


def get_optimization_step_with_lowest_total_cost_table_no_closing(
    vrtool_config: VrtoolConfig, optimization_run_id: int
) -> tuple[int, pd.DataFrame, float]:
    """
    Gets the (id) optimization step, all its related betas and the
    total cost of said step.

    Args:
        vrtool_config (VrtoolConfig): Configuration containing connection details.
        optimization_run_id (int): Optimization whose steps need to be analyzed.

    Returns:
        tuple[int, pd.DataFrame, float]: `OptimizationStep.id`, reliability dataframe
        and total cost of said step.
    """
    (
        _optimization_step,
        dataframe_betas,
        total_cost,
    ) = get_optimization_step_with_lowest_total_cost_no_closing(
        vrtool_config, optimization_run_id
    )
    return _optimization_step.get_id(), dataframe_betas, total_cost


def get_optimization_steps_ordered(run_id: int):
    """Return the optimization steps for a given id, ordered by step number"""

    _optimization_steps = sorted(
        get_optimization_steps(run_id), key=lambda step: step.step_number
    )
    return _optimization_steps
