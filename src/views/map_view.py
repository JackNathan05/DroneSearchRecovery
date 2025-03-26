# src/views/map_view.py
import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QComboBox, QSpinBox, QDoubleSpinBox,
    QGroupBox, QFormLayout, QCheckBox, QFrame, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QSize
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel

from src.mapping.map_manager import MapWidget
from src.planning.flight_planner import FlightPlanner
from src.mapping.map_manager import MapWidget

logger = logging.getLogger(__name__)

class MapViewWidget(QWidget):
    """Widget for displaying map and flight planning controls"""
    
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.flight_planner = FlightPlanner()
        self.boundary_points = []
        self.current_search_pattern = "grid"
        self.current_boundary_name = None
        self.current_path_name = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface"""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel for controls
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 10, 10, 10)
        
        # Mission title
        self.mission_title = QLabel("Flight Planning")
        self.mission_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1E3A8A;")
        left_layout.addWidget(self.mission_title)
        
        # Control panels
        left_layout.addWidget(self.create_drawing_controls())
        left_layout.addWidget(self.create_flight_controls())
        left_layout.addWidget(self.create_camera_controls())
        
        # Add spacer at bottom
        left_layout.addStretch()
        
        # Right panel for map
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create map widget
        self.map_widget = MapViewWidget()
        self.map_widget.map_clicked.connect(self.handle_map_click)
        right_layout.addWidget(self.map_widget)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        
        # Set initial sizes (1:3 ratio)
        splitter.setSizes([300, 900])
        
        main_layout.addWidget(splitter)
    
    def create_drawing_controls(self):
        """Create boundary drawing controls"""
        group_box = QGroupBox("Boundary Definition")
        layout = QVBoxLayout(group_box)
        
        # Drawing mode controls
        drawing_layout = QHBoxLayout()
        
        self.drawing_mode_combo = QComboBox()
        self.drawing_mode_combo.addItems(["Polygon", "Circle"])
        drawing_layout.addWidget(QLabel("Mode:"))
        drawing_layout.addWidget(self.drawing_mode_combo)
        
        layout.addLayout(drawing_layout)
        
        # Buttons for drawing operations
        button_layout = QHBoxLayout()
        
        self.start_drawing_btn = QPushButton("Start Drawing")
        self.start_drawing_btn.clicked.connect(self.start_drawing)
        button_layout.addWidget(self.start_drawing_btn)
        
        self.clear_drawing_btn = QPushButton("Clear")
        self.clear_drawing_btn.clicked.connect(self.clear_drawing)
        self.clear_drawing_btn.setEnabled(False)
        button_layout.addWidget(self.clear_drawing_btn)
        
        layout.addLayout(button_layout)
        
        # Drawing status
        self.drawing_status = QLabel("Click 'Start Drawing' to define search area")
        self.drawing_status.setWordWrap(True)
        layout.addWidget(self.drawing_status)
        
        return group_box
    
    def create_flight_controls(self):
        """Create flight planning controls"""
        group_box = QGroupBox("Flight Planning")
        layout = QVBoxLayout(group_box)
        
        # Pattern selection
        pattern_layout = QHBoxLayout()
        
        self.pattern_combo = QComboBox()
        self.pattern_combo.addItems(["Grid", "Spiral", "Contour"])
        self.pattern_combo.currentTextChanged.connect(self.on_pattern_changed)
        pattern_layout.addWidget(QLabel("Pattern:"))
        pattern_layout.addWidget(self.pattern_combo)
        
        layout.addLayout(pattern_layout)
        
        # Flight parameters form
        param_form = QFormLayout()
        
        self.altitude_spin = QDoubleSpinBox()
        self.altitude_spin.setRange(10, 400)
        self.altitude_spin.setValue(50)
        self.altitude_spin.setSuffix(" m")
        param_form.addRow("Altitude:", self.altitude_spin)
        
        self.speed_spin = QDoubleSpinBox()
        self.speed_spin.setRange(1, 20)
        self.speed_spin.setValue(5)
        self.speed_spin.setSuffix(" m/s")
        param_form.addRow("Speed:", self.speed_spin)
        
        self.overlap_spin = QDoubleSpinBox()
        self.overlap_spin.setRange(0, 90)
        self.overlap_spin.setValue(20)
        self.overlap_spin.setSuffix(" %")
        param_form.addRow("Overlap:", self.overlap_spin)
        
        layout.addLayout(param_form)
        
        # Buttons for flight planning
        button_layout = QHBoxLayout()
        
        self.plan_flight_btn = QPushButton("Plan Flight")
        self.plan_flight_btn.clicked.connect(self.plan_flight)
        self.plan_flight_btn.setEnabled(False)
        button_layout.addWidget(self.plan_flight_btn)
        
        self.clear_plan_btn = QPushButton("Clear Plan")
        self.clear_plan_btn.clicked.connect(self.clear_flight_plan)
        self.clear_plan_btn.setEnabled(False)
        button_layout.addWidget(self.clear_plan_btn)
        
        layout.addLayout(button_layout)
        
        # Flight statistics
        self.flight_stats = QLabel("No flight plan")
        self.flight_stats.setWordWrap(True)
        layout.addWidget(self.flight_stats)
        
        return group_box
    
    def create_camera_controls(self):
        """Create camera parameter controls"""
        group_box = QGroupBox("Camera Parameters")
        layout = QFormLayout(group_box)
        
        self.camera_fov_w_spin = QDoubleSpinBox()
        self.camera_fov_w_spin.setRange(10, 180)
        self.camera_fov_w_spin.setValue(70)
        self.camera_fov_w_spin.setSuffix(" °")
        layout.addRow("Horizontal FOV:", self.camera_fov_w_spin)
        
        self.camera_fov_h_spin = QDoubleSpinBox()
        self.camera_fov_h_spin.setRange(10, 180)
        self.camera_fov_h_spin.setValue(50)
        self.camera_fov_h_spin.setSuffix(" °")
        layout.addRow("Vertical FOV:", self.camera_fov_h_spin)
        
        self.camera_angle_spin = QDoubleSpinBox()
        self.camera_angle_spin.setRange(0, 180)
        self.camera_angle_spin.setValue(90)
        self.camera_angle_spin.setSuffix(" °")
        layout.addRow("Camera Angle:", self.camera_angle_spin)
        
        # Add display for current coverage
        self.coverage_label = QLabel("Coverage: --- × --- m")
        layout.addRow("Ground Coverage:", self.coverage_label)
        
        # Update camera coverage when parameters change
        self.altitude_spin.valueChanged.connect(self.update_camera_coverage)
        self.camera_fov_w_spin.valueChanged.connect(self.update_camera_coverage)
        self.camera_fov_h_spin.valueChanged.connect(self.update_camera_coverage)
        self.camera_angle_spin.valueChanged.connect(self.update_camera_coverage)
        
        # Initial update
        self.update_camera_coverage()
        
        return group_box
    
    def update_camera_coverage(self):
        """Update camera coverage display"""
        # Get parameters
        altitude = self.altitude_spin.value()
        fov_w = self.camera_fov_w_spin.value()
        fov_h = self.camera_fov_h_spin.value()
        camera_angle = self.camera_angle_spin.value()
        
        # Calculate coverage
        width, height = self.flight_planner.calculate_ground_coverage(
            altitude, fov_w, fov_h, camera_angle
        )
        
        # Update display
        self.coverage_label.setText(f"Coverage: {width:.1f} × {height:.1f} m")
    
    def start_drawing(self):
        """Start boundary drawing mode"""
        self.boundary_points = []
        drawing_mode = self.drawing_mode_combo.currentText().lower()
        
        if drawing_mode == "polygon":
            self.drawing_status.setText("Click on map to add boundary points. Double-click to finish.")
            # Enable drawing mode in map
            # For now, we'll simulate with manual clicks
        elif drawing_mode == "circle":
            self.drawing_status.setText("Click on map to set center point, then click again to set radius.")
            # Enable circle drawing mode
        
        # Update button states
        self.start_drawing_btn.setEnabled(False)
        self.clear_drawing_btn.setEnabled(True)
        self.drawing_mode_combo.setEnabled(False)
    
    def clear_drawing(self):
        """Clear the current boundary drawing"""
        self.boundary_points = []
        self.drawing_status.setText("Drawing cleared. Click 'Start Drawing' to start again.")
        
        # Clear boundary from map
        if self.current_boundary_name:
            self.map_widget.map_manager.clear_feature(self.current_boundary_name)
            self.current_boundary_name = None
        
        # Update button states
        self.start_drawing_btn.setEnabled(True)
        self.clear_drawing_btn.setEnabled(False)
        self.drawing_mode_combo.setEnabled(True)
        self.plan_flight_btn.setEnabled(False)
    
    def handle_map_click(self, lat, lon):
        """Handle map click events
        
        Args:
            lat: Latitude of click
            lon: Longitude of click
        """
        if not self.start_drawing_btn.isEnabled():
            # In drawing mode
            drawing_mode = self.drawing_mode_combo.currentText().lower()
            
            if drawing_mode == "polygon":
                # Add point to boundary
                self.boundary_points.append((lat, lon))
                count = len(self.boundary_points)
                
                # Update display
                if count == 1:
                    # First point, show marker
                    self.map_widget.map_manager.add_marker(
                        location=(lat, lon),
                        popup="Start point"
                    )
                elif count >= 3:
                    # Three or more points, show/update polygon
                    if self.current_boundary_name:
                        self.map_widget.map_manager.clear_feature(self.current_boundary_name)
                    
                    self.current_boundary_name = self.map_widget.map_manager.add_polygon(
                        locations=self.boundary_points,
                        color="#4A90E2",
                        fill=True,
                        popup="Search Area"
                    )
                    
                    # Refresh map
                    self.map_widget.update_map()
                
                self.drawing_status.setText(f"Added point {count}. Click to add more or double-click to finish.")
                
                # Check if we should finish (for now, let's say 5+ points is enough)
                if count >= 3:
                    # For this demo version, let's assume we're done after a reasonable number of points
                    self.drawing_status.setText(f"Boundary with {count} points created. Ready to plan flight.")
                    self.start_drawing_btn.setEnabled(True)
                    self.plan_flight_btn.setEnabled(True)
                    
                    # Convert final polygon to search area
                    if self.current_boundary_name:
                        self.map_widget.map_manager.clear_feature(self.current_boundary_name)
                    
                    self.current_boundary_name = self.map_widget.map_manager.add_search_area(
                        boundary=self.boundary_points,
                        color="#4A90E2",
                        name="search_area"
                    )
                    
                    # Refresh map
                    self.map_widget.update_map()
            
            elif drawing_mode == "circle":
                # Circle drawing (center and radius)
                if len(self.boundary_points) == 0:
                    # First click sets center
                    self.boundary_points.append((lat, lon))
                    self.map_widget.map_manager.add_marker(
                        location=(lat, lon),
                        popup="Circle center"
                    )
                    self.drawing_status.setText("Center point set. Click again to set radius.")
                    
                    # Refresh map
                    self.map_widget.update_map()
                elif len(self.boundary_points) == 1:
                    # Second click sets radius
                    from geopy.distance import geodesic
                    center = self.boundary_points[0]
                    radius = geodesic(center, (lat, lon)).meters
                    
                    # Create circle
                    if self.current_boundary_name:
                        self.map_widget.map_manager.clear_feature(self.current_boundary_name)
                    
                    self.current_boundary_name = self.map_widget.map_manager.add_circle(
                        location=center,
                        radius=radius,
                        color="#4A90E2",
                        fill=True,
                        popup=f"Search Area<br>Radius: {radius:.1f} m"
                    )
                    
                    # Store the circle parameters
                    self.boundary_points = [center, radius]
                    
                    # Refresh map
                    self.map_widget.update_map()
                    
                    # Update status and buttons
                    self.drawing_status.setText(f"Circle with radius {radius:.1f} m created. Ready to plan flight.")
                    self.start_drawing_btn.setEnabled(True)
                    self.plan_flight_btn.setEnabled(True)
    
    def on_pattern_changed(self, pattern):
        """Handle pattern selection changes
        
        Args:
            pattern: New pattern name
        """
        self.current_search_pattern = pattern.lower()
    
    def plan_flight(self):
        """Generate a flight plan based on current settings"""
        # Get parameters
        altitude = self.altitude_spin.value()
        speed = self.speed_spin.value()
        overlap = self.overlap_spin.value()
        fov_w = self.camera_fov_w_spin.value()
        fov_h = self.camera_fov_h_spin.value()
        camera_angle = self.camera_angle_spin.value()
        
        # Prepare parameters
        params = {
            'altitude': altitude,
            'speed': speed,
            'overlap': overlap,
            'camera_fov_w': fov_w,
            'camera_fov_h': fov_h,
            'camera_angle': camera_angle
        }
        
        # Generate waypoints based on pattern
        waypoints = []
        pattern = self.current_search_pattern
        
        try:
            if pattern == "grid":
                if not self.boundary_points or len(self.boundary_points) < 3:
                    self.flight_stats.setText("Error: Need at least 3 boundary points for grid pattern")
                    return
                
                # Generate grid pattern
                waypoints = self.flight_planner.plan_grid_search(self.boundary_points, params)
            
            elif pattern == "spiral":
                if not self.boundary_points or len(self.boundary_points) < 2:
                    self.flight_stats.setText("Error: Need center and radius for spiral pattern")
                    return
                
                if isinstance(self.boundary_points[1], (int, float)):
                    # Circle mode: center point and radius
                    center = self.boundary_points[0]
                    radius = self.boundary_points[1]
                else:
                    # Calculate center from polygon
                    lat_sum = sum(p[0] for p in self.boundary_points)
                    lon_sum = sum(p[1] for p in self.boundary_points)
                    center = (lat_sum / len(self.boundary_points), lon_sum / len(self.boundary_points))
                    
                    # Estimate radius as average distance from center to points
                    from geopy.distance import geodesic
                    radius = sum(geodesic(center, p).meters for p in self.boundary_points) / len(self.boundary_points)
                
                # Generate spiral pattern
                waypoints = self.flight_planner.plan_spiral_search(center, radius, params)
            
            elif pattern == "contour":
                if not self.boundary_points or len(self.boundary_points) < 3:
                    self.flight_stats.setText("Error: Need at least 3 boundary points for contour pattern")
                    return
                
                # For demo, use a few simple contour lines
                contour_lines = [altitude - 20, altitude, altitude + 20]
                
                # Generate contour pattern
                waypoints = self.flight_planner.plan_contour_search(self.boundary_points, contour_lines, params)
        
        except Exception as e:
            self.flight_stats.setText(f"Error planning flight: {str(e)}")
            logger.error(f"Error planning flight: {str(e)}")
            return
        
        # Check if we got waypoints
        if not waypoints:
            self.flight_stats.setText("Error: Failed to generate waypoints")
            return
        
        # Calculate flight statistics
        num_waypoints = len(waypoints)
        flight_time_seconds = self.flight_planner.estimate_flight_time(waypoints, speed)
        flight_time_minutes = flight_time_seconds / 60
        
        # Update display
        stats_text = (
            f"Flight Plan: {pattern.title()} pattern\n"
            f"Waypoints: {num_waypoints}\n"
            f"Est. Flight Time: {flight_time_minutes:.1f} minutes"
        )
        self.flight_stats.setText(stats_text)
        
        # Display flight path on map
        if self.current_path_name:
            # Clear old path
            line_name, wp_names = self.current_path_name
            self.map_widget.map_manager.clear_feature(line_name)
            for wp_name in wp_names:
                self.map_widget.map_manager.clear_feature(wp_name)
        
        # Add new path
        self.current_path_name = self.map_widget.map_manager.add_flight_path(
            waypoints=waypoints,
            altitudes=[altitude] * len(waypoints),
            name=f"path_{pattern}"
        )
        
        # Refresh map
        self.map_widget.update_map()
        
        # Update button states
        self.clear_plan_btn.setEnabled(True)
    
    def clear_flight_plan(self):
        """Clear the current flight plan"""
        if self.current_path_name:
            # Clear path from map
            line_name, wp_names = self.current_path_name
            self.map_widget.map_manager.clear_feature(line_name)
            for wp_name in wp_names:
                self.map_widget.map_manager.clear_feature(wp_name)
            self.current_path_name = None
            
            # Refresh map
            self.map_widget.update_map()
        
        # Reset status
        self.flight_stats.setText("No flight plan")
        
        # Update button state
        self.clear_plan_btn.setEnabled(False)