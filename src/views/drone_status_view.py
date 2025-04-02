# src/views/drone_status_view.py
import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem, QFrame,
    QComboBox, QDoubleSpinBox, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from src.drone.drone_controller import DroneController
from src.drone.drone_simulator import DroneSimulator

logger = logging.getLogger(__name__)

class DroneStatusWidget(QWidget):
    """Widget for drone status display and control"""
    
    def __init__(self, main_window=None):
        super().__init__()
        self.drone_controller = DroneController()
        self.drone_simulator = DroneSimulator()
        self.simulator_running = False
        self.main_window = main_window
        
        self.setup_ui()
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(500)  # Update every 500ms
    
    def setup_ui(self):
        """Set up the user interface"""
        main_layout = QVBoxLayout(self)
        
        # Connection section
        connection_frame = QFrame()
        connection_frame.setFrameShape(QFrame.Shape.StyledPanel)
        connection_frame.setStyleSheet("background-color: #F0F0F0; border-radius: 5px; padding: 10px;")
        connection_layout = QVBoxLayout(connection_frame)

        self.home_button = QPushButton("← Home")
        self.home_button.setStyleSheet("font-weight: bold; background-color: #E5E7EB;")
        self.home_button.clicked.connect(lambda: self.main_window.go_to_home())
        connection_layout.addWidget(self.home_button)
        
        # Connection title
        connection_title = QLabel("Drone Connection")
        connection_title.setStyleSheet("font-size: 14px; font-weight: bold;")
        connection_layout.addWidget(connection_title)
        
        # Connection controls
        conn_controls_layout = QHBoxLayout()
        
        # Simulator controls
        self.simulator_btn = QPushButton("Start Simulator")
        self.simulator_btn.clicked.connect(self.toggle_simulator)
        conn_controls_layout.addWidget(self.simulator_btn)
        
        # Connection controls
        self.connect_btn = QPushButton("Connect to Drone")
        self.connect_btn.clicked.connect(self.connect_to_drone)
        conn_controls_layout.addWidget(self.connect_btn)
        
        self.disconnect_btn = QPushButton("Disconnect")
        self.disconnect_btn.clicked.connect(self.disconnect_from_drone)
        self.disconnect_btn.setEnabled(False)
        conn_controls_layout.addWidget(self.disconnect_btn)
        
        connection_layout.addLayout(conn_controls_layout)
        
        # Connection status
        self.connection_status = QLabel("Not Connected")
        self.connection_status.setStyleSheet("color: red;")
        connection_layout.addWidget(self.connection_status)
        
        main_layout.addWidget(connection_frame)
        
        # Status section
        status_frame = QFrame()
        status_frame.setFrameShape(QFrame.Shape.StyledPanel)
        status_frame.setStyleSheet("background-color: #F0F0F0; border-radius: 5px; padding: 10px;")
        status_layout = QVBoxLayout(status_frame)
        
        # Status title
        status_title = QLabel("Drone Status")
        status_title.setStyleSheet("font-size: 14px; font-weight: bold;")
        status_layout.addWidget(status_title)
        
        # Status table
        self.status_table = QTableWidget(0, 2)
        self.status_table.setHorizontalHeaderLabels(["Parameter", "Value"])
        self.status_table.horizontalHeader().setStretchLastSection(True)
        self.status_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        status_layout.addWidget(self.status_table)
        
        main_layout.addWidget(status_frame)
        
        # Commands section
        commands_frame = QFrame()
        commands_frame.setFrameShape(QFrame.Shape.StyledPanel)
        commands_frame.setStyleSheet("background-color: #F0F0F0; border-radius: 5px; padding: 10px;")
        commands_layout = QVBoxLayout(commands_frame)
        
        # Commands title
        commands_title = QLabel("Drone Commands")
        commands_title.setStyleSheet("font-size: 14px; font-weight: bold;")
        commands_layout.addWidget(commands_title)
        
        # Command buttons
        cmd_buttons_layout = QHBoxLayout()
        
        # Mode selection
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["GUIDED", "AUTO", "RTL", "LAND"])
        mode_layout.addWidget(self.mode_combo)
        self.set_mode_btn = QPushButton("Set Mode")
        self.set_mode_btn.clicked.connect(self.set_mode)
        mode_layout.addWidget(self.set_mode_btn)
        cmd_buttons_layout.addLayout(mode_layout)
        
        # Arm/Disarm
        self.arm_btn = QPushButton("Arm")
        self.arm_btn.clicked.connect(self.arm)
        cmd_buttons_layout.addWidget(self.arm_btn)
        
        self.disarm_btn = QPushButton("Disarm")
        self.disarm_btn.clicked.connect(self.disarm)
        cmd_buttons_layout.addWidget(self.disarm_btn)
        
        commands_layout.addLayout(cmd_buttons_layout)
        
        # Flight commands
        flight_cmd_layout = QHBoxLayout()
        
        # Takeoff
        takeoff_layout = QHBoxLayout()
        takeoff_layout.addWidget(QLabel("Altitude:"))
        self.altitude_spin = QDoubleSpinBox()
        self.altitude_spin.setRange(1, 100)
        self.altitude_spin.setValue(10)
        self.altitude_spin.setSuffix(" m")
        takeoff_layout.addWidget(self.altitude_spin)
        self.takeoff_btn = QPushButton("Takeoff")
        self.takeoff_btn.clicked.connect(self.takeoff)
        takeoff_layout.addWidget(self.takeoff_btn)
        flight_cmd_layout.addLayout(takeoff_layout)
        
        # RTL and Land
        self.rtl_btn = QPushButton("Return to Launch")
        self.rtl_btn.clicked.connect(self.return_to_launch)
        flight_cmd_layout.addWidget(self.rtl_btn)
        
        self.land_btn = QPushButton("Land")
        self.land_btn.clicked.connect(self.land)
        flight_cmd_layout.addWidget(self.land_btn)
        
        commands_layout.addLayout(flight_cmd_layout)
        
        main_layout.addWidget(commands_frame)
        
        # Disable command buttons initially
        self.enable_command_buttons(False)
    
    def toggle_simulator(self):
        """Toggle simulator on/off"""
        if not self.simulator_running:
            # Start simulator
            if self.drone_simulator.start():
                self.simulator_running = True
                self.simulator_btn.setText("Stop Simulator")
                QMessageBox.information(self, "Simulator", "Drone simulator started successfully")
            else:
                QMessageBox.warning(self, "Simulator Error", "Failed to start simulator. Make sure DroneKit-SITL is installed.")
        else:
            # Stop simulator
            self.drone_simulator.stop()
            self.simulator_running = False
            self.simulator_btn.setText("Start Simulator")
            QMessageBox.information(self, "Simulator", "Drone simulator stopped")
    
    def connect_to_drone(self):
        """Connect to the drone/simulator"""
        # Use simulator connection string
        if self.drone_controller.connect("tcp:127.0.0.1:5760", is_simulation=True):
            self.connection_status.setText("Connected")
            self.connection_status.setStyleSheet("color: green; font-weight: bold;")
            self.connect_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)
            self.enable_command_buttons(True)
            self.drone_controller.register_state_change_callback(self.handle_state_change)
            QMessageBox.information(self, "Connection", "Connected to drone successfully")
        else:
            QMessageBox.warning(self, "Connection Error", "Failed to connect to drone. Check that simulator is running.")
    
    def disconnect_from_drone(self):
        """Disconnect from the drone"""
        self.drone_controller.disconnect()
        self.connection_status.setText("Not Connected")
        self.connection_status.setStyleSheet("color: red;")
        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)
        self.enable_command_buttons(False)
        self.clear_status_table()
        QMessageBox.information(self, "Disconnection", "Disconnected from drone")
    
    def enable_command_buttons(self, enabled):
        """Enable or disable command buttons"""
        self.set_mode_btn.setEnabled(enabled)
        self.arm_btn.setEnabled(enabled)
        self.disarm_btn.setEnabled(enabled)
        self.takeoff_btn.setEnabled(enabled)
        self.rtl_btn.setEnabled(enabled)
        self.land_btn.setEnabled(enabled)
    
    def handle_state_change(self, state):
        """Handle drone state changes"""
        # This will be called automatically when drone state changes
        # Status will be updated by the update_timer
        pass
    
    def update_status(self):
        """Update status display"""
        if not self.drone_controller.is_connected:
            return
        
        # Get current state
        state = self.drone_controller.get_state()
        
        # Update status table
        self.update_status_table(state)
    
    def update_status_table(self, state):
        """Update the status table with current state"""
        # Clear table
        self.status_table.setRowCount(0)
        
        # Add state items
        row = 0
        for key, value in state.items():
            self.status_table.insertRow(row)
            self.status_table.setItem(row, 0, QTableWidgetItem(key))
            
            # Format value based on type
            if isinstance(value, float):
                if key in ["latitude", "longitude"]:
                    value_str = f"{value:.6f}"
                else:
                    value_str = f"{value:.2f}"
            else:
                value_str = str(value)
            
            self.status_table.setItem(row, 1, QTableWidgetItem(value_str))
            row += 1
    
    def clear_status_table(self):
        """Clear the status table"""
        self.status_table.setRowCount(0)
    
    def set_mode(self):
        """Set flight mode"""
        mode = self.mode_combo.currentText()
        if self.drone_controller.set_mode(mode):
            QMessageBox.information(self, "Mode Change", f"Mode changed to {mode}")
        else:
            QMessageBox.warning(self, "Mode Change Error", f"Failed to change mode to {mode}")
    
    def arm(self):
        """Arm the drone"""
        if self.drone_controller.arm():
            QMessageBox.information(self, "Arm", "Drone armed successfully")
        else:
            QMessageBox.warning(self, "Arm Error", "Failed to arm drone")
    
    def disarm(self):
        """Disarm the drone"""
        if self.drone_controller.disarm():
            QMessageBox.information(self, "Disarm", "Drone disarmed successfully")
        else:
            QMessageBox.warning(self, "Disarm Error", "Failed to disarm drone")
    
    def takeoff(self):
        """Take off to specified altitude"""
        altitude = self.altitude_spin.value()
        if self.drone_controller.takeoff(altitude):
            QMessageBox.information(self, "Takeoff", f"Taking off to {altitude}m")
        else:
            QMessageBox.warning(self, "Takeoff Error", "Failed to take off")
    
    def return_to_launch(self):
        """Return to launch"""
        if self.drone_controller.return_to_launch():
            QMessageBox.information(self, "RTL", "Returning to launch point")
        else:
            QMessageBox.warning(self, "RTL Error", "Failed to initiate return to launch")
    
    def land(self):
        """Land the drone"""
        if self.drone_controller.land():
            QMessageBox.information(self, "Land", "Landing drone")
        else:
            QMessageBox.warning(self, "Land Error", "Failed to initiate landing")