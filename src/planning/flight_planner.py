# src/planning/flight_planner.py
import math
import logging
from typing import List, Tuple, Dict, Any, Optional
import numpy as np
from geopy.distance import geodesic
from shapely.geometry import Point, Polygon

logger = logging.getLogger(__name__)

class FlightPlanner:
    """Plans flight paths for search operations"""
    
    def __init__(self):
        """Initialize the flight planner"""
        # Default drone parameters
        self.default_params = {
            'altitude': 50.0,           # meters
            'speed': 5.0,               # m/s
            'camera_fov_w': 70.0,       # degrees
            'camera_fov_h': 50.0,       # degrees
            'overlap': 20.0,            # percent
            'min_distance': 5.0,        # meters between waypoints
            'max_distance': 100.0,      # meters between waypoints
            'camera_angle': 90.0,       # degrees (90 = straight down)
        }
    
    @staticmethod
    def calculate_ground_coverage(altitude: float, fov_w: float, fov_h: float, camera_angle: float = 90.0) -> Tuple[float, float]:
        """Calculate ground coverage dimensions based on altitude and field of view
        
        Args:
            altitude: Flight altitude in meters
            fov_w: Camera horizontal field of view in degrees
            fov_h: Camera vertical field of view in degrees
            camera_angle: Camera angle in degrees (90 = straight down)
            
        Returns:
            tuple: (width, height) of ground coverage in meters
        """
        # Convert field of view to radians
        fov_w_rad = math.radians(fov_w)
        fov_h_rad = math.radians(fov_h)
        
        # Convert camera angle to radians (0 = horizontal, 90 = straight down)
        camera_angle_rad = math.radians(camera_angle)
        
        # Calculate effective altitude (distance from camera to ground along camera axis)
        if camera_angle_rad >= math.pi/2:  # 90 degrees or more (downward)
            effective_altitude = altitude / math.sin(camera_angle_rad)
        else:
            # Camera is looking upward or horizontal, no ground coverage
            return 0.0, 0.0
        
        # Calculate ground coverage
        width = 2 * effective_altitude * math.tan(fov_w_rad / 2)
        height = 2 * effective_altitude * math.tan(fov_h_rad / 2)
        
        return width, height
    
    @staticmethod
    def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate the great circle distance between two points in meters
        
        Args:
            lat1: Latitude of point 1 in degrees
            lon1: Longitude of point 1 in degrees
            lat2: Latitude of point 2 in degrees
            lon2: Longitude of point 2 in degrees
            
        Returns:
            float: Distance in meters
        """
        return geodesic((lat1, lon1), (lat2, lon2)).meters
    
    @staticmethod
    def _destination_point(lat: float, lon: float, bearing: float, distance: float) -> Tuple[float, float]:
        """Calculate a destination point given starting point, bearing and distance
        
        Args:
            lat: Starting latitude in degrees
            lon: Starting longitude in degrees
            bearing: Bearing in degrees (0 = north, 90 = east)
            distance: Distance in meters
            
        Returns:
            tuple: (latitude, longitude) of destination point
        """
        # Use geopy's geodesic calculation
        start = (lat, lon)
        destination = geodesic(meters=distance).destination(start, bearing)
        return destination.latitude, destination.longitude
    
    def plan_grid_search(self, boundary: List[Tuple[float, float]], params: Optional[Dict[str, Any]] = None) -> List[Tuple[float, float]]:
        """Plan a grid search pattern for a given boundary
        
        Args:
            boundary: List of (lat, lon) tuples defining search area boundary
            params: Optional parameter overrides
            
        Returns:
            list: List of (lat, lon) waypoints for the search pattern
        """
        # Use default parameters with overrides
        p = self.default_params.copy()
        if params:
            p.update(params)
        
        # Convert boundary to shapely polygon for operations
        polygon = Polygon(boundary)
        
        # Get bounding box
        minx, miny, maxx, maxy = polygon.bounds
        
        # Calculate coverage width and track spacing based on altitude, fov, and overlap
        coverage_width, _ = self.calculate_ground_coverage(
            p['altitude'], p['camera_fov_w'], p['camera_fov_h'], p['camera_angle']
        )
        
        # Calculate track spacing with overlap
        track_spacing = coverage_width * (1 - p['overlap'] / 100.0)
        
        # Determine optimal grid orientation (align with longest edge)
        width = geodesic((miny, minx), (miny, maxx)).meters
        height = geodesic((miny, minx), (maxy, minx)).meters
        
        # Determine grid orientation
        is_horizontal = width > height
        
        # Calculate number of tracks and waypoint spacing
        if is_horizontal:
            # Tracks run east-west
            num_tracks = max(2, int(math.ceil(height / track_spacing)))
            track_length = width
            track_spacing_deg = (maxy - miny) / (num_tracks - 1)
            
            # Calculate initial corner points
            corners = [
                (miny, minx),  # SW
                (miny, maxx),  # SE
                (maxy, maxx),  # NE
                (maxy, minx)   # NW
            ]
            
            # Determine track direction
            forward = True
        else:
            # Tracks run north-south
            num_tracks = max(2, int(math.ceil(width / track_spacing)))
            track_length = height
            track_spacing_deg = (maxx - minx) / (num_tracks - 1)
            
            # Calculate initial corner points
            corners = [
                (miny, minx),  # SW
                (maxy, minx),  # NW
                (maxy, maxx),  # NE
                (miny, maxx)   # SE
            ]
            
            # Determine track direction
            forward = True
        
        # Calculate waypoint spacing
        num_waypoints = max(2, int(track_length / p['max_distance']))
        waypoint_spacing = track_length / (num_waypoints - 1)
        
        # Generate waypoints
        waypoints = []
        
        if is_horizontal:
            # Tracks run east-west
            for i in range(num_tracks):
                track_lat = miny + i * track_spacing_deg
                
                if forward:
                    start_lon, end_lon = minx, maxx
                else:
                    start_lon, end_lon = maxx, minx
                
                # Generate waypoints along track
                for j in range(num_waypoints):
                    progress = j / (num_waypoints - 1)
                    lon = start_lon + progress * (end_lon - start_lon)
                    
                    # Check if waypoint is inside polygon
                    if polygon.contains(Point(lon, track_lat)):
                        waypoints.append((track_lat, lon))
                
                # Alternate direction
                forward = not forward
        else:
            # Tracks run north-south
            for i in range(num_tracks):
                track_lon = minx + i * track_spacing_deg
                
                if forward:
                    start_lat, end_lat = miny, maxy
                else:
                    start_lat, end_lat = maxy, miny
                
                # Generate waypoints along track
                for j in range(num_waypoints):
                    progress = j / (num_waypoints - 1)
                    lat = start_lat + progress * (end_lat - start_lat)
                    
                    # Check if waypoint is inside polygon
                    if polygon.contains(Point(track_lon, lat)):
                        waypoints.append((lat, track_lon))
                
                # Alternate direction
                forward = not forward
        
        return waypoints
    
    def plan_spiral_search(self, center: Tuple[float, float], radius: float, params: Optional[Dict[str, Any]] = None) -> List[Tuple[float, float]]:
        """Plan a spiral search pattern from a center point
        
        Args:
            center: (lat, lon) center point
            radius: Search radius in meters
            params: Optional parameter overrides
            
        Returns:
            list: List of (lat, lon) waypoints for the search pattern
        """
        # Use default parameters with overrides
        p = self.default_params.copy()
        if params:
            p.update(params)
        
        # Calculate coverage width and track spacing based on altitude, fov, and overlap
        coverage_width, _ = self.calculate_ground_coverage(
            p['altitude'], p['camera_fov_w'], p['camera_fov_h'], p['camera_angle']
        )
        
        # Calculate spiral spacing with overlap
        spacing = coverage_width * (1 - p['overlap'] / 100.0)
        
        # Limit waypoint spacing
        waypoint_angle_step = math.degrees(p['min_distance'] / radius)
        
        # Calculate number of loops and total angle based on radius and spacing
        num_loops = math.ceil(radius / spacing)
        total_angle = num_loops * 2 * math.pi
        
        # Calculate number of waypoints
        circumference = 2 * math.pi * radius
        num_waypoints = min(1000, max(10, int(circumference / p['min_distance'])))
        
        # Generate points on spiral
        waypoints = [center]  # Start at center
        
        for i in range(1, num_waypoints):
            # Calculate spiral parameters
            progress = i / (num_waypoints - 1)
            current_angle = total_angle * progress
            current_radius = radius * progress
            
            # Calculate bearing (0 = north, clockwise)
            bearing = math.degrees(current_angle) % 360
            
            # Calculate point at this radius and angle
            lat, lon = self._destination_point(
                center[0], center[1], bearing, current_radius
            )
            
            waypoints.append((lat, lon))
        
        return waypoints
    
    def plan_contour_search(self, boundary: List[Tuple[float, float]], contour_lines: List[float], params: Optional[Dict[str, Any]] = None) -> List[Tuple[float, float]]:
        """Plan a contour-following search pattern
        
        Args:
            boundary: List of (lat, lon) tuples defining search area boundary
            contour_lines: List of elevation contour lines to follow (in meters)
            params: Optional parameter overrides
            
        Returns:
            list: List of (lat, lon) waypoints for the search pattern
        """
        # Note: This is a simplified implementation that assumes contour lines are provided
        # In a real implementation, you would need to integrate with a terrain elevation model
        
        # Use default parameters with overrides
        p = self.default_params.copy()
        if params:
            p.update(params)
        
        # Convert boundary to polygon
        polygon = Polygon(boundary)
        
        # Process each contour line
        waypoints = []
        
        for elevation in contour_lines:
            # For this simplified implementation, we generate a spiral at the centroid of the polygon
            # In a real implementation, you would generate points along actual contour lines
            
            # Get polygon centroid
            centroid = polygon.centroid
            center = (centroid.y, centroid.x)
            
            # Calculate a radius based on polygon area
            radius = math.sqrt(polygon.area) * 0.5
            
            # Generate waypoints along this "contour"
            contour_points = self.plan_spiral_search(center, radius, params)
            
            # Add elevation as a third component (for 3D visualization)
            contour_points = [(lat, lon, elevation) for lat, lon in contour_points]
            
            # Add to overall waypoint list
            waypoints.extend(contour_points)
        
        return waypoints
    
    def estimate_flight_time(self, waypoints: List[Tuple[float, float]], speed: float) -> float:
        """Estimate flight time for a mission
        
        Args:
            waypoints: List of (lat, lon) waypoints
            speed: Ground speed in m/s
            
        Returns:
            float: Estimated flight time in seconds
        """
        if len(waypoints) < 2:
            return 0
        
        # Calculate total distance
        total_distance = 0
        for i in range(1, len(waypoints)):
            prev = waypoints[i-1]
            curr = waypoints[i]
            
            distance = self._haversine_distance(prev[0], prev[1], curr[0], curr[1])
            total_distance += distance
        
        # Estimate time
        time_seconds = total_distance / speed
        
        return time_seconds