from shapely import LineString


def serialize_linestring(linestring: LineString):
    return list(linestring.coords)
