
def import_optimization_runs_name(orm_model) -> list[str]:
    """
    Returns a list of the names of the optimization runs in the database

    :return: list of names of the optimization runs in the database
    """

    if orm_model.OptimizationRun.select().exists():
        _optimization_runs = orm_model.OptimizationRun.select()
        _names = [run.name for run in _optimization_runs]

        return _names
    else:
        return []