def to_million_euros(cost: float) -> float:
    """Converts a cost in euros to millions of euros"""
    return round(cost / 1e6, 2)