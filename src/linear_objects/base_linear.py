from shapely import LineString


class BaseLinearObject:
    coordinates_rd: list[tuple[float, float]]
    trajectory_rd: LineString

    def __init__(self, coordinates_rd: list[tuple[float, float]]):
        self.coordinates_rd = coordinates_rd
        self.trajectory_rd = LineString(coordinates_rd)

    def coordinates_wgs84(self):
        pass

    def serialize(self):
        pass
