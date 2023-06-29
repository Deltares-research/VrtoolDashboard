from shapely import LineString


class BaseLinearObject:
    coordinates_rd: list[tuple[float, float]]
    trajectory: LineString

    def __init__(self, coordinates_rd: list[tuple[float, float]]):
        self.coordinates_rd = coordinates_rd
        trajectory = LineString(coordinates_rd)

    def coordinates_wgs84(self):
        pass

    def serialize(self):
        pass
