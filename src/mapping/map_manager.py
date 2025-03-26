# src/mapping/map_manager.py
import logging
import numpy as np
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
import pyqtgraph as pg

logger = logging.getLogger(__name__)

class MapManager:
    """Manages the map display and interactions"""
    
    def __init__(self, default_location=(40.071374, -105.229195), default_zoom=0.01):
        """Initialize the map manager
        
        Args:
            default_location: (lat, lon) default center point
            default_zoom: Default zoom level (smaller is more zoomed out)
        """
        self.default_location = default_location
        self.default_zoom = default_zoom
        self.current_location = default_location
        self.current_zoom = default_zoom
        
        # Create plot widget
        self.plot_widget = pg.PlotWidget()
        self.plot = self.plot_widget.getPlotItem()
        
        # Configure axis labels
        self.plot.setLabel('bottom', 'Longitude')
        self.plot.setLabel('left', 'Latitude')
        
        # Set aspect ratio to ~1 to prevent distortion
        self.plot.setAspectLocked(True)
        
        # Track map features
        self.markers = {}
        self.polygons = {}
        self.polylines = {}
        self.circles = {}
        
        # Add background grid
        self.add_grid()
        
        # Set initial view
        self.update_view()
    
    def add_grid(self):
        """Add a grid to the map for reference"""
        # Create grid lines
        grid_x = np.linspace(-180, 180, 37)  # Every 10 degrees longitude
        grid_y = np.linspace(-90, 90, 19)    # Every 10 degrees latitude
        
        # Add vertical grid lines
        for x in grid_x:
            line = pg.InfiniteLine(pos=x, angle=90, pen=pg.mkPen(color='#CCCCCC', width=1))
            self.plot.addItem(line)
        
        # Add horizontal grid lines
        for y in grid_y:
            line = pg.InfiniteLine(pos=y, angle=0, pen=pg.mkPen(color='#CCCCCC', width=1))
            self.plot.addItem(line)
    
    def update_view(self):
        """Update the view to show the current center and zoom level"""
        # Set the visible range based on the center coordinates and zoom level
        x_range = [self.current_location[1] - self.current_zoom, 
                  self.current_location[1] + self.current_zoom]
        y_range = [self.current_location[0] - self.current_zoom, 
                  self.current_location[0] + self.current_zoom]
        
        self.plot.setXRange(*x_range)
        self.plot.setYRange(*y_range)
    
    def reset_map(self):
        """Reset the map to default state"""
        # Clear all items
        self.plot.clear()
        
        # Re-add grid
        self.add_grid()
        
        # Reset location and zoom
        self.current_location = self.default_location
        self.current_zoom = self.default_zoom
        
        # Update view
        self.update_view()
        
        # Clear feature collections
        self.markers = {}
        self.polygons = {}
        self.polylines = {}
        self.circles = {}
    
    def add_marker(self, location, popup=None, icon=None, name=None):
        """Add a marker to the map
        
        Args:
            location: (lat, lon) tuple
            popup: Optional popup text
            icon: Optional icon configuration (not used in this implementation)
            name: Optional name for later reference
            
        Returns:
            str: Marker name
        """
        if name is None:
            name = f"marker_{len(self.markers)}"
        
        # Create scatter point for marker
        marker = pg.ScatterPlotItem()
        
        # Add a single point (longitude, latitude)
        marker.addPoints([location[1]], [location[0]], 
                         symbol='o', 
                         size=10, 
                         brush=pg.mkBrush('#3388ff'), 
                         pen=pg.mkPen('w'))
        
        # Add to plot
        self.plot.addItem(marker)
        
        # Store marker info
        marker_info = {
            'item': marker,
            'lat': location[0],
            'lon': location[1],
            'popup': popup
        }
        
        # Add text label if popup is provided
        if popup:
            text = pg.TextItem(popup, anchor=(0.5, 1.5))
            text.setPos(location[1], location[0])
            self.plot.addItem(text)
            marker_info['text'] = text
        
        # Store for reference
        self.markers[name] = marker_info
        
        return name
    
    def add_waypoint(self, location, index, altitude=None, name=None):
        """Add a waypoint marker with custom styling
        
        Args:
            location: (lat, lon) tuple
            index: Waypoint index/number
            altitude: Optional altitude in meters
            name: Optional name for later reference
            
        Returns:
            str: Waypoint name
        """
        if name is None:
            name = f"waypoint_{len(self.markers)}"
        
        # Create popup content
        popup_content = f"Waypoint {index}<br>Lat: {location[0]:.6f}<br>Lon: {location[1]:.6f}"
        if altitude is not None:
            popup_content += f"<br>Alt: {altitude:.1f}m"
        
        # Create marker
        waypoint = pg.ScatterPlotItem()
        waypoint.addPoints([location[1]], [location[0]], 
                          symbol='o', 
                          size=12, 
                          brush=pg.mkBrush('#4A90E2'), 
                          pen=pg.mkPen('w', width=2))
        
        # Add to plot
        self.plot.addItem(waypoint)
        
        # Add text label for waypoint number
        text = pg.TextItem(str(index), anchor=(0.5, 0.5), color='white')
        text.setPos(location[1], location[0])
        self.plot.addItem(text)
        
        # Store marker info
        marker_info = {
            'item': waypoint,
            'text': text,
            'lat': location[0],
            'lon': location[1],
            'index': index,
            'altitude': altitude,
            'popup': popup_content
        }
        
        # Store for reference
        self.markers[name] = marker_info
        
        return name
    
    def add_polygon(self, locations, color='blue', fill=True, popup=None, name=None):
        """Add a polygon to the map
        
        Args:
            locations: List of (lat, lon) points
            color: Polygon color
            fill: Whether to fill the polygon
            popup: Optional popup text
            name: Optional name for later reference
            
        Returns:
            str: Polygon name
        """
        if name is None:
            name = f"polygon_{len(self.polygons)}"
        
        if len(locations) < 3:
            logger.warning("Polygon needs at least 3 points")
            return None
        
        # Convert color name to hex if needed
        if color == 'blue':
            color = '#3388ff'
        
        # Extract lon/lat points
        points = np.array(locations)
        lats, lons = points[:, 0], points[:, 1]
        
        # Create polygon
        polygon = pg.PlotDataItem(lons, lats, 
                                 pen=pg.mkPen(color=color, width=2))
        
        # Add fill if requested
        if fill:
            fill_poly = pg.FillBetweenItem(
                polygon, 
                pg.PlotDataItem([lons[0]], [lats[0]]),  # Dummy curve for filling
                brush=pg.mkBrush(color=color, alpha=50)
            )
            self.plot.addItem(fill_poly)
        
        # Add to plot
        self.plot.addItem(polygon)
        
        # Store polygon info
        polygon_info = {
            'item': polygon,
            'fill_item': fill_poly if fill else None,
            'points': locations,
            'color': color,
            'popup': popup
        }
        
        # Add text label if popup is provided
        if popup:
            # Calculate center of polygon
            center_lat = sum(lats) / len(lats)
            center_lon = sum(lons) / len(lons)
            
            text = pg.TextItem(popup, anchor=(0.5, 0.5))
            text.setPos(center_lon, center_lat)
            self.plot.addItem(text)
            polygon_info['text'] = text
        
        # Store for reference
        self.polygons[name] = polygon_info
        
        return name
    
    def add_circle(self, location, radius, color='blue', fill=True, popup=None, name=None):
        """Add a circle to the map
        
        Args:
            location: (lat, lon) center point
            radius: Radius in meters (approximated in this implementation)
            color: Circle color
            fill: Whether to fill the circle
            popup: Optional popup text
            name: Optional name for later reference
            
        Returns:
            str: Circle name
        """
        if name is None:
            name = f"circle_{len(self.circles)}"
        
        # Convert color name to hex if needed
        if color == 'blue':
            color = '#3388ff'
        
        # Create a circle by approximating with points
        # This is a rough approximation based on a constant 
        # for converting degrees to meters near the equator
        # A proper implementation would use the haversine formula
        degree_radius = radius / 111000  # Approximate conversion from meters to degrees
        
        # Generate circle points
        theta = np.linspace(0, 2*np.pi, 100)
        circle_x = location[1] + degree_radius * np.cos(theta)
        circle_y = location[0] + degree_radius * np.sin(theta)
        
        # Create circle
        circle = pg.PlotDataItem(circle_x, circle_y, 
                              pen=pg.mkPen(color=color, width=2))
        
        # Add fill if requested
        fill_item = None
        if fill:
            # Create a polygon for filling
            fill_poly = pg.PlotCurveItem(circle_x, circle_y, 
                                      pen=pg.mkPen(None),
                                      brush=pg.mkBrush(color=color, alpha=50))
            self.plot.addItem(fill_poly)
            fill_item = fill_poly
        
        # Add to plot
        self.plot.addItem(circle)
        
        # Store circle info
        circle_info = {
            'item': circle,
            'fill_item': fill_item,
            'center': location,
            'radius': radius,
            'color': color,
            'popup': popup
        }
        
        # Add text label if popup is provided
        if popup:
            text = pg.TextItem(popup, anchor=(0.5, 0.5))
            text.setPos(location[1], location[0])
            self.plot.addItem(text)
            circle_info['text'] = text
        
        # Store for reference
        self.circles[name] = circle_info
        
        return name
    
    def add_polyline(self, locations, color='blue', weight=3, popup=None, name=None, arrows=False):
        """Add a polyline to the map
        
        Args:
            locations: List of (lat, lon) points
            color: Line color
            weight: Line weight
            popup: Optional popup text
            name: Optional name for later reference
            arrows: Whether to show direction arrows (not implemented in this version)
            
        Returns:
            str: Polyline name
        """
        if name is None:
            name = f"polyline_{len(self.polylines)}"
        
        if len(locations) < 2:
            logger.warning("Polyline needs at least 2 points")
            return None
        
        # Convert color name to hex if needed
        if color == 'blue':
            color = '#3388ff'
        
        # Extract lon/lat points
        points = np.array(locations)
        lats, lons = points[:, 0], points[:, 1]
        
        # Create polyline
        polyline = pg.PlotDataItem(lons, lats, 
                                 pen=pg.mkPen(color=color, width=weight))
        
        # Add to plot
        self.plot.addItem(polyline)
        
        # Store polyline info
        polyline_info = {
            'item': polyline,
            'points': locations,
            'color': color,
            'weight': weight,
            'popup': popup
        }
        
        # Add text label if popup is provided
        if popup:
            # Place label near the middle of the line
            mid_index = len(locations) // 2
            text = pg.TextItem(popup, anchor=(0.5, 0))
            text.setPos(locations[mid_index][1], locations[mid_index][0])
            self.plot.addItem(text)
            polyline_info['text'] = text
        
        # Store for reference
        self.polylines[name] = polyline_info
        
        return name
    
    def add_flight_path(self, waypoints, altitudes=None, name=None):
        """Add a flight path with waypoints and connecting lines
        
        Args:
            waypoints: List of (lat, lon) points
            altitudes: Optional list of altitudes
            name: Optional base name for elements
            
        Returns:
            tuple: (line_name, list of waypoint names)
        """
        if name is None:
            name = f"path_{len(self.polylines)}"
        
        # Create line for the path
        line_name = self.add_polyline(
            locations=waypoints,
            color='#FF7E47',  # Orange from our color scheme
            weight=4,
            arrows=True,
            name=f"{name}_line"
        )
        
        # Add waypoint markers
        waypoint_names = []
        for i, point in enumerate(waypoints):
            alt = altitudes[i] if altitudes and i < len(altitudes) else None
            wp_name = self.add_waypoint(
                location=point,
                index=i,
                altitude=alt,
                name=f"{name}_wp_{i}"
            )
            waypoint_names.append(wp_name)
        
        return line_name, waypoint_names
    
    def add_search_area(self, boundary, color='#4A90E2', name=None):
        """Add a search area boundary
        
        Args:
            boundary: List of (lat, lon) points forming a polygon
            color: Area color
            name: Optional name for later reference
            
        Returns:
            str: Polygon name
        """
        if name is None:
            name = f"search_area_{len(self.polygons)}"
        
        # Calculate area (approximate)
        from geopy.distance import geodesic
        
        def calculate_area(points):
            """Calculate approximate area of a polygon on Earth's surface"""
            if len(points) < 3:
                return 0
            
            # Use the shoelace formula with geodesic distances
            area = 0
            for i in range(len(points)):
                j = (i + 1) % len(points)
                # Convert to cartesian coordinates (approximate for small areas)
                x1, y1 = points[i][1], points[i][0]  # lon, lat
                x2, y2 = points[j][1], points[j][0]  # lon, lat
                area += x1 * y2 - x2 * y1
            
            # Convert to square meters (very approximate)
            # This is a simplification - for more accurate calculations, 
            # use a proper GIS library like Shapely with appropriate projections
            avg_lat = sum(p[0] for p in points) / len(points)
            avg_lon = sum(p[1] for p in points) / len(points)
            
            # Approximate conversion factors
            lat_m = geodesic((avg_lat, avg_lon), (avg_lat + 0.001, avg_lon)).meters / 0.001
            lon_m = geodesic((avg_lat, avg_lon), (avg_lat, avg_lon + 0.001)).meters / 0.001
            
            return abs(area) * lat_m * lon_m / 2
        
        area = calculate_area(boundary)
        area_str = f"{area/10000:.2f} hectares" if area >= 10000 else f"{area:.0f} sq meters"
        
        # Create pop-up with area information
        popup = f"Search Area<br>Area: {area_str}"
        
        # Add polygon
        return self.add_polygon(
            locations=boundary,
            color=color,
            fill=True,
            popup=popup,
            name=name
        )
    
    def clear_feature(self, name):
        """Remove a specific feature from the map
        
        Args:
            name: Feature name
            
        Returns:
            bool: True if found and removed
        """
        # Check markers
        if name in self.markers:
            marker_info = self.markers[name]
            self.plot.removeItem(marker_info['item'])
            if 'text' in marker_info:
                self.plot.removeItem(marker_info['text'])
            del self.markers[name]
            return True
        
        # Check polygons
        if name in self.polygons:
            polygon_info = self.polygons[name]
            self.plot.removeItem(polygon_info['item'])
            if polygon_info['fill_item'] is not None:
                self.plot.removeItem(polygon_info['fill_item'])
            if 'text' in polygon_info:
                self.plot.removeItem(polygon_info['text'])
            del self.polygons[name]
            return True
        
        # Check polylines
        if name in self.polylines:
            polyline_info = self.polylines[name]
            self.plot.removeItem(polyline_info['item'])
            if 'text' in polyline_info:
                self.plot.removeItem(polyline_info['text'])
            del self.polylines[name]
            return True
        
        # Check circles
        if name in self.circles:
            circle_info = self.circles[name]
            self.plot.removeItem(circle_info['item'])
            if circle_info['fill_item'] is not None:
                self.plot.removeItem(circle_info['fill_item'])
            if 'text' in circle_info:
                self.plot.removeItem(circle_info['text'])
            del self.circles[name]
            return True
        
        return False
    
    def clear_all_features(self):
        """Clear all features from the map"""
        self.reset_map()


class MapWidget(QWidget):
    """QWidget for displaying a map in the UI"""
    
    # Signal emitted when map is clicked
    map_clicked = pyqtSignal(float, float)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Create map manager
        self.map_manager = MapManager()
        
        # Create layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Add plot widget to layout
        self.layout.addWidget(self.map_manager.plot_widget)
        
        # Connect click event
        proxy = pg.SignalProxy(
            self.map_manager.plot.scene().sigMouseClicked, 
            rateLimit=60, 
            slot=self.on_map_click
        )
    
    def update_map(self):
        """Update the map display"""
        self.map_manager.update_view()
    
    def on_map_click(self, event):
        """Handle map click events
        
        Args:
            event: PyQtGraph mouse click event
        """
        # Get the mouse event
        mouse_event = event[0]
        
        # Only handle left-click events
        if mouse_event.button() == Qt.MouseButton.LeftButton:
            # Convert click position to lat/lon
            position = mouse_event.scenePos()
            map_point = self.map_manager.plot.vb.mapSceneToView(position)
            
            # Get lat/lon (note the order: lon=x, lat=y)
            lon, lat = map_point.x(), map_point.y()
            
            # Emit the map_clicked signal
            self.map_clicked.emit(lat, lon)
            
            logger.debug(f"Map clicked at lat={lat}, lon={lon}")