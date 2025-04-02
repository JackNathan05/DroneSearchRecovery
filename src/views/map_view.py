# src/views/map_view.py
import os
import logging
import traceback
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QDoubleSpinBox,
    QGroupBox, QFormLayout, QSplitter, QCheckBox
)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from src.mapping.map_generator import generate_folium_map
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QTimer
from PyQt6.QtWebChannel import QWebChannel
from pathlib import Path
from src.planning.flight_planner import FlightPlanner
from src.utils.shape_utils import extract_active_shape_bounds
from PyQt5 import QtWebChannel
from src.mapping.map_manager import MapManager

logger = logging.getLogger(__name__)

class CoordinateBridge(QObject):
    coordinate_received = pyqtSignal(float, float)
    hover_coordinates = pyqtSignal(float, float)

    def __init__(self, map_manager, update_callback):
        super().__init__()
        self.map_manager = map_manager
        self.update_callback = update_callback

    @pyqtSlot(float, float)
    def send_coordinates(self, lat, lon):
        self.coordinate_received.emit(lat, lon)

    @pyqtSlot(float, float)
    def send_hover_coordinates(self, lat, lon):
        self.hover_coordinates.emit(lat, lon)

    @pyqtSlot(str)
    def receiveShape(self, shape_json):
        self.map_manager.handle_shape_update(shape_json)
        self.update_callback()

class MapViewWidget(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.flight_planner = FlightPlanner()
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Map View")
        self.resize(1200, 800)
        main_layout = QHBoxLayout(self)

        # Sidebar panel
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 10, 10, 10)

        self.home_button = QPushButton("← Home")
        self.home_button.setStyleSheet("font-weight: bold; background-color: #E5E7EB;")
        self.home_button.clicked.connect(lambda: self.main_window.go_to_home())
        left_layout.addWidget(self.home_button)

        self.coord_label = QLabel("Click on map to show coordinates")
        left_layout.addWidget(self.coord_label)

        self.mission_title = QLabel("Flight Planning")
        self.mission_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1E3A8A;")
        left_layout.addWidget(self.mission_title)

        # Header with mission title and back button
        header_layout = QHBoxLayout()
        
        # Add camera controls only for now
        left_layout.addWidget(self.create_camera_controls())
        left_layout.addStretch()

        # Generate map
        map_path = generate_folium_map(None, speed_mps=self.speed_spin)
        full_path = Path(map_path).resolve().as_uri()
        QTimer.singleShot(500, lambda: self.webview.setUrl(QUrl(full_path)))
        print("[DEBUG] Loading map into webview from:", full_path)

        # Map panel
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        self.webview = QWebEngineView()

        self.map_manager = MapManager(self)
        self.bridge = CoordinateBridge(self.map_manager, self.update_map)

        self.channel = QWebChannel()
        self.channel.registerObject("coordinateBridge", self.bridge)
        self.webview.page().setWebChannel(self.channel)

        self.bridge.coordinate_received.connect(self.update_coordinate_display)
        self.bridge.hover_coordinates.connect(self.update_hover_display)
        self.channel.registerObject("mapBridge", self.bridge)
        self.bridge.map_manager = self.map_manager

        # ✅ Enable local content to access remote JS (fixes Leaflet 'L is not defined' error)
        from PyQt6.QtWebEngineCore import QWebEngineSettings
        self.webview.settings().setAttribute(
            QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True
        )

        self.webview.load(QUrl.fromLocalFile(map_path))
        right_layout.addWidget(self.webview)

        # Split layout
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 900])

        main_layout.addWidget(splitter)

    def setup_web_channel(self):
        channel = QWebChannel()
        channel.registerObject("mapBridge", self.map_manager)
        self.webview.page().setWebChannel(channel)

    def create_camera_controls(self):
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

        self.altitude_spin = QDoubleSpinBox()
        self.altitude_spin.setRange(10, 400)
        self.altitude_spin.setValue(50)
        self.altitude_spin.setSuffix(" m")
        layout.addRow("Altitude:", self.altitude_spin)

        self.speed_spin = QDoubleSpinBox()
        self.speed_spin.setRange(0.1, 20.0)
        self.speed_spin.setSingleStep(0.1)
        self.speed_spin.setValue(5.0)
        self.speed_spin.setSuffix(" m/s")
        layout.addRow("Flight Speed:", self.speed_spin)

        self.front_overlap_input = QDoubleSpinBox()
        self.front_overlap_input.setRange(0, 100)
        self.front_overlap_input.setSingleStep(5)
        self.front_overlap_input.setValue(70.0)  # Default to 70%
        self.front_overlap_input.setSuffix(" %")
        layout.addRow("Front Overlap (%):", self.front_overlap_input)

        self.side_overlap_input = QDoubleSpinBox()
        self.side_overlap_input.setRange(0, 100)
        self.side_overlap_input.setSingleStep(5)
        self.side_overlap_input.setValue(60.0)  # Default to 60%
        self.side_overlap_input.setSuffix(" %")
        layout.addRow("Side Overlap (%):", self.side_overlap_input)

        self.pattern_dropdown = QComboBox()
        self.pattern_dropdown.addItems(["Grid", "Spiral"])
        layout.addRow("Search pattern:", self.pattern_dropdown)

        self.contouring_checkbox = QCheckBox()
        #self.contouring_checkbox.objectName("Terain contouring?")
        layout.addRow("Terain contouring? ", self.contouring_checkbox)

        self.coverage_label = QLabel("Coverage: --- × --- m")
        layout.addRow("Ground Coverage:", self.coverage_label)

        self.altitude_spin.valueChanged.connect(self.update_camera_coverage)
        self.camera_fov_w_spin.valueChanged.connect(self.update_camera_coverage)
        self.camera_fov_h_spin.valueChanged.connect(self.update_camera_coverage)
        self.camera_angle_spin.valueChanged.connect(self.update_camera_coverage)
        self.front_overlap_input.valueChanged.connect(self.update_camera_coverage)
        self.side_overlap_input.valueChanged.connect(self.update_camera_coverage)

        self.altitude_spin.valueChanged.connect(self.update_map)
        self.camera_fov_w_spin.valueChanged.connect(self.update_map)
        self.camera_fov_h_spin.valueChanged.connect(self.update_map)
        self.camera_angle_spin.valueChanged.connect(self.update_map)
        self.speed_spin.valueChanged.connect(self.update_map)
        self.front_overlap_input.valueChanged.connect(self.update_map)
        self.side_overlap_input.valueChanged.connect(self.update_map)
        self.pattern_dropdown.currentTextChanged.connect(self.update_map)
        self.contouring_checkbox.stateChanged.connect(self.update_map)

        self.update_camera_coverage()
        return group_box

    def update_camera_coverage(self):
        self.alt = self.altitude_spin.value()
        self.fov_w = self.camera_fov_w_spin.value()
        self.fov_h = self.camera_fov_h_spin.value()
        self.angle = self.camera_angle_spin.value()
        self.overlap_f = self.front_overlap_input.value()
        self.overlap_s = self.side_overlap_input.value()

        width = 2 * self.alt * (self.fov_w / 2) / 57.3  # simplified trig
        height = 2 * self.alt * (self.fov_h / 2) / 57.3
        self.coverage_label.setText(f"Coverage: {width:.1f} × {height:.1f} m")

    def update_map(self):
        try:
            logger.info("Updating map with current mission settings...")

            params = {
                "altitude": self.alt,
                "w_fov": self.fov_w,
                "h_fov": self.fov_h,
                "angle": self.angle,
                "f_overlap": self.overlap_s,
                "s_overlap": self.overlap_s,
                "speed": self.speed_spin,
                "contour": self.contouring_checkbox.isChecked()
            }

            # 2. Get drawn shapes from map and extract active boundary
            logger.info("Updating map with current mission settings...")
            drawn_shapes = self.map_manager.get_drawn_shapes()
            logger.debug(f"Drawn shapes retrieved: {drawn_shapes}")
            boundary = extract_active_shape_bounds(drawn_shapes)
            if boundary is None:
                logger.warning("No active shape found for flight planning.")
                return 

            # 3. Generate waypoints
            if self.pattern_dropdown.currentText() == "Spiral":
                waypoints = self.flight_planner.plan_spiral_search(boundary, params)
            else:
                waypoints = self.flight_planner.plan_grid_search(boundary, params)
            print("[DEBUG] Generated waypoints:", waypoints)

            # 4. Rebuild map and display
            logger.info(f"WAYPOINTS GENERATED: {waypoints}")
            logger.info(f"PARAMS: {params}")
            map_path = generate_folium_map(waypoints, speed_mps=self.speed_spin.value(), altitude = self.altitude_spin.value())
            full_path = Path(map_path).resolve().as_uri()
            QTimer.singleShot(500, lambda: self.webview.setUrl(QUrl(full_path)))

        except Exception as e:
            logger.error(f"Error updating map: {e}")
            traceback.print_exc()

    def update_coordinate_display(self, lat, lon):
        self.coord_label.setText(f"Lat: {lat:.5f}, Lon: {lon:.5f}")
    
    def update_hover_display(self, lat, lon):
            self.coord_label.setText(f"Hover: {lat:.5f}, {lon:.5f}")