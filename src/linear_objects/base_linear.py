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

    def shift_trajectory_sideways(self, distance: int, side: str):
        self.trajectory_rd = self.trajectory_rd.parallel_offset(distance, side)
        if isinstance(self.trajectory_rd, LineString):
            self.coordinates_rd = list(self.trajectory_rd.coords)
        else:
            # assuming only 2 LineStrings are returned
            self.coordinates_rd = (list(self.trajectory_rd.parallel_offset(100, side).geoms[0].coords) +
                                   list(self.trajectory_rd.parallel_offset(100, side).geoms[1].coords))