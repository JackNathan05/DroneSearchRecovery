from shapely.geometry import Polygon, LineString, MultiLineString
from geopy.distance import geodesic
import logging
import math
from typing import List, Tuple, Dict

logger = logging.getLogger(__name__)

class FlightPlanner:
    def __init__(self):
        pass

    def should_rotate_grid(self, polygon: Polygon) -> bool:
        bounds = polygon.bounds  # (min_x, min_y, max_x, max_y)
        mid_y = (bounds[1] + bounds[3]) / 2
        mid_x = (bounds[0] + bounds[2]) / 2

        # Horizontal midline (to detect top/bottom concavity)
        h_line = LineString([(bounds[0], mid_y), (bounds[2], mid_y)])
        h_inter = polygon.intersection(h_line)
        h_coverage = h_inter.length if not h_inter.is_empty else 0

        # Vertical midline (to detect left/right concavity)
        v_line = LineString([(mid_x, bounds[1]), (mid_x, bounds[3])])
        v_inter = polygon.intersection(v_line)
        v_coverage = v_inter.length if not v_inter.is_empty else 0

        # Lower coverage = more concave = better to rotate
        return h_coverage < v_coverage

    def plan_grid_search(self, boundary, params):

        # Fallback/default values
        altitude = params.get("altitude")
        w_fov = params.get("w_fov")
        h_fov = params.get("h_fov")
        angle = params.get("angle")
        front_overlap = params.get("f_overlap") / 100.0
        side_overlap = params.get("s_overlap") / 100.0

        # Convert degrees to radians
        h_fov_rad = math.radians(h_fov)
        w_fov_rad = math.radians(w_fov)
        angle_rad = math.radians(angle)

        # Projected front/back coverage based on tilt (from vertical)
        # Uses basic trigonometry to estimate how far the camera sees along the ground
        front_coverage = 2 * altitude * math.tan(h_fov_rad / 2) / math.cos(angle_rad)
        side_coverage = 2 * altitude * math.tan(w_fov_rad / 2)

        # Apply overlaps
        front_spacing = front_coverage * (1 - front_overlap)
        side_spacing = side_coverage * (1 - side_overlap)

        try:
            polygon = Polygon([(lon, lat) for lat, lon in boundary])
        except ValueError as e:
            logger.error(f"Failed to build polygon: {e}")
            return []

        rotate = self.should_rotate_grid(polygon)

        min_x, min_y, max_x, max_y = polygon.bounds

        width_m = geodesic((min_y, min_x), (min_y, max_x)).meters
        height_m = geodesic((min_y, min_x), (max_y, min_x)).meters

        cols = int(width_m // side_spacing)
        rows = int(height_m // front_spacing)

        logger.info(f"Grid size: {cols} cols x {rows} rows (rotated: {rotate})")

        waypoints = []

        range_limit = cols if rotate else rows
        for i in range(range_limit + 1):
            ratio = i / range_limit if range_limit else 0

            if rotate:
                x = min_x + (max_x - min_x) * ratio
                line = LineString([(x, min_y), (x, max_y)])
            else:
                y = min_y + (max_y - min_y) * ratio
                line = LineString([(min_x, y), (max_x, y)])

            clipped = polygon.intersection(line)

            if clipped.is_empty:
                continue

            segments = []
            if isinstance(clipped, MultiLineString):
                for seg in clipped.geoms:
                    segments.extend(seg.coords)
            elif isinstance(clipped, LineString):
                segments = clipped.coords
            else:
                continue

            row_waypoints = [(y, x) for x, y in segments]
            if i % 2 == 1:
                row_waypoints.reverse()

            waypoints.extend(row_waypoints)

        logger.info(f"Generated {len(waypoints)} waypoints for clipped grid.")
        logger.debug(f"Front spacing: {front_spacing:.2f} m, Side spacing: {side_spacing:.2f} m")
        return waypoints
    
    def plan_spiral_search(self, boundary: List[Tuple[float, float]], params: Dict) -> List[Tuple[float, float]]:
        from shapely.geometry import Polygon, Point

        if not boundary or len(boundary) < 3:
            return []

        lats, lons = zip(*boundary)  # This is correct if boundary is (lat, lon)
        center_lat = sum(lats) / len(lats)
        center_lon = sum(lons) / len(lons)
        print(f"[DEBUG] Corrected center_lat: {center_lat}, center_lon: {center_lon}")

        # Spiral parameters
        spacing_m = self._calculate_spacing(params)
        print(f"[DEBUG] boundary: {boundary}")
        print(f"[DEBUG] center_lat: {center_lat}, center_lon: {center_lon}")
        max_radius = self._max_distance_to_edge(center_lat, center_lon, boundary)
        angle_step = 45  # degrees between waypoints
        print(f"[DEBUG] spiral spacing_m: {spacing_m:.2f}m, max_radius: {max_radius:.2f}m")

        waypoints = []
        angle = 0
        radius = spacing_m

        polygon = Polygon([(lon, lat) for lat, lon in boundary])  # shapely expects (x, y)
        while radius <= max_radius:
            lat, lon = self._move_in_direction(center_lat, center_lon, radius, angle)
            if polygon.contains(Point(lon, lat)):
                waypoints.append((lat, lon))
            angle += angle_step
            if angle >= 360:
                angle -= 360
                radius += spacing_m

        return waypoints

    def _calculate_spacing(self, params: Dict) -> float:
        altitude = params.get('altitude', 50)
        h_fov = params.get('h_fov', 70)
        angle = params.get('angle', 90)
        f_overlap = params.get('f_overlap', 60)  # default 60% forward overlap

        # Convert to radians
        h_fov_rad = math.radians(h_fov)
        angle_rad = math.radians(angle)

        # Effective altitude from ground point of view (slant projection)
        effective_alt = altitude / math.cos(angle_rad)

        # Width of ground covered at that tilt
        ground_width = 2 * effective_alt * math.tan(h_fov_rad / 2)

        # Adjust for overlap
        spacing = ground_width * (1 - f_overlap / 100)

        print(f"[DEBUG] spacing with angle: {spacing:.2f}m (alt: {altitude}, angle: {angle}, h_fov: {h_fov})")
        return spacing

    def _max_distance_to_edge(self, lat: float, lon: float, boundary: List[Tuple[float, float]]) -> float:
        """Calculates max distance from center to any point in boundary."""
        distances = []
        for pt in boundary:
            try:
                pt_lat, pt_lon = pt  # pt is (lat, lon)  # [lon, lat] → (lat, lon)
                if -90 <= pt[0] <= 90 and -180 <= pt[1] <= 180:
                    dist = geodesic((lat, lon), (pt_lat, pt_lon)).meters
                    distances.append(dist)
                else:
                    print(f"[DEBUG] Skipping out-of-bounds pt: {pt}")
            except Exception as e:
                print(f"[DEBUG] Error parsing pt {pt}: {e}")
        return max(distances) if distances else 0

    def _move_in_direction(self, lat: float, lon: float, distance_m: float, bearing_deg: float) -> Tuple[float, float]:
        from geopy.distance import distance
        from geopy import Point
        origin = Point(lat, lon)
        destination = distance(meters=distance_m).destination(origin, bearing_deg)
        return destination.latitude, destination.longitude