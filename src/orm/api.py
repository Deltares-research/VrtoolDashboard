def get_optimization_step_with_lowest_total_cost(
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
    # _connected_db = open_database(vrtool_config.input_database_path)
    # logging.info(
    #     "Openned connection to retrieve 'OptimizationStep' with lowest total cost."
    # )

    _results = []
    for _optimization_step in get_optimization_steps(optimization_run_id):
        _as_df = OptimizationStepImporter.import_optimization_step_results_df(
            _optimization_step
        )
        _cost = _optimization_step.total_lcc + _optimization_step.total_risk
        _results.append((_optimization_step, _as_df, _cost))

    # _connected_db.close()
    # logging.info(
    #     "Closed connection after retrieval of lowest total cost 'OptimizationStep'."
    # )

    return min(_results, key=lambda results_tuple: results_tuple[2])