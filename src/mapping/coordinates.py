# src/mapping/coordinates.py
import math
import pyproj
from typing import List, Tuple, Optional

def wgs84_to_utm(lat: float, lon: float) -> Tuple[float, float, int]:
    """Convert WGS84 coordinates to UTM
    
    Args:
        lat: Latitude in degrees
        lon: Longitude in degrees
        
    Returns:
        tuple: (easting, northing, zone) in meters
    """
    # Determine UTM zone
    zone = math.floor((lon + 180) / 6) + 1
    
    # Create projections
    wgs84 = pyproj.CRS.from_epsg(4326)  # WGS84
    utm = pyproj.CRS.from_epsg(32600 + zone)  # UTM zones are 32601-32660
    
    # Create transformer
    transformer = pyproj.Transformer.from_crs(wgs84, utm, always_xy=True)
    
    # Transform coordinates
    easting, northing = transformer.transform(lon, lat)
    
    return easting, northing, zone

def utm_to_wgs84(easting: float, northing: float, zone: int, northern: bool = True) -> Tuple[float, float]:
    """Convert UTM coordinates to WGS84
    
    Args:
        easting: UTM easting in meters
        northing: UTM northing in meters
        zone: UTM zone number
        northern: Whether in northern hemisphere (True) or southern (False)
        
    Returns:
        tuple: (latitude, longitude) in degrees
    """
    # Create projections
    utm = pyproj.CRS.from_epsg(32600 + zone)  # UTM zones are 32601-32660
    wgs84 = pyproj.CRS.from_epsg(4326)  # WGS84
    
    # Create transformer
    transformer = pyproj.Transformer.from_crs(utm, wgs84, always_xy=True)
    
    # Transform coordinates
    lon, lat = transformer.transform(easting, northing)
    
    return lat, lon

def bearing_between_points(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate bearing from point 1 to point 2
    
    Args:
        lat1: Latitude of point 1 in degrees
        lon1: Longitude of point 1 in degrees
        lat2: Latitude of point 2 in degrees
        lon2: Longitude of point 2 in degrees
        
    Returns:
        float: Bearing in degrees (0 = north, clockwise)
    """
    # Convert to radians
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)
    
    # Calculate bearing
    y = math.sin(lon2 - lon1) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(lon2 - lon1)
    bearing = math.atan2(y, x)
    
    # Convert to degrees
    bearing = math.degrees(bearing)
    
    # Normalize to 0-360
    bearing = (bearing + 360) % 360
    
    return bearing