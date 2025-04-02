import logging
from geopy.distance import distance
from math import radians
from PyQt5.QtCore import QPointF

logger = logging.getLogger(__name__)


def extract_active_shape_bounds(drawn_shapes):
    """
    Extracts the boundary (as a list of lat/lon tuples) from the most recently added shape.
    Supports polygons and circles.

    Parameters:
        drawn_shapes (list): A list of dictionaries representing drawn shapes with keys:
            - 'type': 'polygon' or 'circle'
            - 'coordinates': list of [lat, lon] for polygons
            - 'center': [lat, lon] for circles
            - 'radius': in meters, for circles

    Returns:
        list of (lat, lon): Boundary points
    """
    if not drawn_shapes:
        logger.warning("No shapes available to extract boundary from.")
        return []

    shape = drawn_shapes[-1]
    shape_type = shape.get('type')
    coords = shape.get('coordinates', [])

    # Detect special circle format: 'polygon' with a single [lat, lon, radius]
    if shape_type == 'polygon' and len(coords) == 1 and len(coords[0]) == 3:
        lat, lon, radius = coords[0]
        logger.debug("Detected circle-as-polygon format. Converting to circle polygon.")
        return _generate_circle_polygon((lat, lon), radius)

    elif shape_type == 'polygon':
        return [tuple(c[:2]) for c in coords]  # Trim to (lat, lon) if more values exist

    logger.error(f"Unsupported or malformed shape type: {shape_type}")
    return []


def _generate_circle_polygon(center, radius_m, num_points=36):
    """
    Approximate a circle with a polygon by generating points along its circumference.

    Parameters:
        center (list or tuple): [lat, lon]
        radius_m (float): radius in meters
        num_points (int): number of points to generate

    Returns:
        list of (lat, lon): Approximated polygon coordinates
    """
    lat, lon = center
    points = []

    for angle in range(0, 360, int(360 / num_points)):
        point = distance(meters=radius_m).destination((lat, lon), angle)
        points.append((point.latitude, point.longitude))

    logger.debug(f"Generated {len(points)} points for circle approximation.")
    return points
