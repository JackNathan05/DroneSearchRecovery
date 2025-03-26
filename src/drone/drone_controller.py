# src/drone/drone_controller.py
import logging
import time
import threading
from typing import Dict, Any, Optional, Tuple, List, Union
from src.drone import dronekit_wrapper as dronekit
from .drone_connection import DroneConnection
from .drone_state import DroneState
from .drone_command import DroneCommand
from .mission_manager import MissionManager
from .parameter_manager import ParameterManager

logger = logging.getLogger(__name__)

class DroneController:
    """Main controller for drone operations"""
    
    def __init__(self):
        """Initialize the drone controller"""
        self.connection = DroneConnection()
        self.state = DroneState()
        self.command = DroneCommand()
        self.mission = MissionManager()
        self.parameters = ParameterManager()
        
        # Register callbacks
        self.connection.register_on_connection(self._on_connect)
        self.connection.register_on_disconnection(self._on_disconnect)
        
        # Status tracking
        self.is_connected = False
        
        # Callback handlers
        self.state_change_callbacks = []
    
    def connect(self, connection_string: str, baud: int = 57600, timeout: int = 30, is_simulation: bool = False) -> bool:
        """Connect to a drone
        
        Args:
            connection_string: Connection string (e.g., 'tcp:127.0.0.1:5760', '/dev/ttyUSB0')
            baud: Baud rate for serial connections
            timeout: Connection timeout in seconds
            is_simulation: Whether this is a simulated connection
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        # Connect to the drone
        if self.connection.connect(connection_string, baud, timeout, is_simulation):
            # Wait for the _on_connect callback to handle integration
            start_time = time.time()
            while not self.is_connected and time.time() - start_time < timeout:
                time.sleep(0.5)
            
            return self.is_connected
        
        return False
    
    def disconnect(self):
        """Disconnect from the drone"""
        if self.is_connected:
            self.connection.disconnect()
    
    def _on_connect(self):
        """Handle connection established"""
        logger.info("Drone connected, initializing components...")
        
        # Set the vehicle in all components
        self.state.set_vehicle(self.connection.vehicle)
        self.command.set_vehicle(self.connection.vehicle)
        self.mission.set_vehicle(self.connection.vehicle)
        self.parameters.set_vehicle(self.connection.vehicle)
        
        # Register state change callback
        self.state.register_state_change_callback(self._on_state_change)
        
        # Update status
        self.is_connected = True
        
        logger.info("Drone controller fully initialized")
    
    def _on_disconnect(self):
        """Handle disconnection"""
        logger.info("Drone disconnected, cleaning up...")
        
        # Clear the vehicle from all components
        self.state.clear_vehicle()
        
        # Update status
        self.is_connected = False
        
        logger.info("Drone controller reset")
    
    def _on_state_change(self, state: Dict[str, Any]):
        """Handle state changes
        
        Args:
            state: New drone state
        """
        # Notify all registered callbacks
        for callback in self.state_change_callbacks:
            try:
                callback(state)
            except Exception as e:
                logger.error(f"Error in state change callback: {str(e)}")
    
    def register_state_change_callback(self, callback):
        """Register a callback for drone state changes
        
        Args:
            callback: Function to call with new state
        """
        if callback not in self.state_change_callbacks:
            self.state_change_callbacks.append(callback)
    
    def unregister_state_change_callback(self, callback):
        """Unregister a state change callback
        
        Args:
            callback: Function to unregister
        """
        if callback in self.state_change_callbacks:
            self.state_change_callbacks.remove(callback)
    
    def get_state(self) -> Dict[str, Any]:
        """Get the current drone state
        
        Returns:
            dict: Current drone state
        """
        return self.state.get_state()
    
    def arm(self) -> bool:
        """Arm the drone
        
        Returns:
            bool: True if armed successfully, False otherwise
        """
        return self.command.arm()
    
    def disarm(self) -> bool:
        """Disarm the drone
        
        Returns:
            bool: True if disarmed successfully, False otherwise
        """
        return self.command.disarm()
    
    def takeoff(self, altitude: float) -> bool:
        """Take off to a specific altitude
        
        Args:
            altitude: Target altitude in meters
            
        Returns:
            bool: True if takeoff successful, False otherwise
        """
        return self.command.takeoff(altitude)
    
    def land(self) -> bool:
        """Land the drone
        
        Returns:
            bool: True if landing initiated successfully, False otherwise
        """
        return self.command.land()
    
    def return_to_launch(self) -> bool:
        """Return to launch location
        
        Returns:
            bool: True if RTL initiated successfully, False otherwise
        """
        return self.command.return_to_launch()
    
    def goto_position(self, lat: float, lon: float, alt: float, ground_speed: Optional[float] = None) -> bool:
        """Go to a specific position
        
        Args:
            lat: Target latitude
            lon: Target longitude
            alt: Target altitude (relative)
            ground_speed: Optional ground speed in m/s
            
        Returns:
            bool: True if command sent successfully, False otherwise
        """
        return self.command.goto_position(lat, lon, alt, ground_speed)
    
    def set_mode(self, mode_name: str) -> bool:
        """Set the flight mode
        
        Args:
            mode_name: Name of the flight mode (e.g., 'GUIDED', 'RTL', 'AUTO')
            
        Returns:
            bool: True if mode set successfully, False otherwise
        """
        return self.command.set_mode(mode_name)
    
    def clear_mission(self) -> bool:
        """Clear the current mission
        
        Returns:
            bool: True if mission cleared successfully, False otherwise
        """
        return self.mission.clear_mission()
    
    def download_mission(self) -> List[Dict[str, Any]]:
        """Download the current mission from the vehicle
        
        Returns:
            list: List of waypoint dictionaries
        """
        return self.mission.download_mission()
    
    def upload_mission(self, waypoints: List[Dict[str, Any]]) -> bool:
        """Upload a mission to the vehicle
        
        Args:
            waypoints: List of waypoint dictionaries
            
        Returns:
            bool: True if mission uploaded successfully, False otherwise
        """
        return self.mission.upload_mission(waypoints)
    
    def create_waypoint_mission(self, waypoints: List[Tuple[float, float, float]], hold_time: float = 0) -> List[Dict[str, Any]]:
        """Create a waypoint mission from a list of coordinates
        
        Args:
            waypoints: List of (latitude, longitude, altitude) tuples
            hold_time: Hold time at each waypoint in seconds
            
        Returns:
            list: List of waypoint dictionaries ready for upload
        """
        return self.mission.create_waypoint_mission(waypoints, hold_time)
    
    def start_mission(self) -> bool:
        """Start the mission
        
        Returns:
            bool: True if mission started successfully, False otherwise
        """
        return self.mission.start_mission()
    
    def get_mission_status(self) -> Dict[str, Any]:
        """Get the current mission status
        
        Returns:
            dict: Mission status information
        """
        return self.mission.get_mission_status()
    
    def get_all_parameters(self) -> Dict[str, Any]:
        """Get all vehicle parameters
        
        Returns:
            dict: Dictionary of parameter names and values
        """
        return self.parameters.get_all_parameters()
    
    def get_parameter(self, param_name: str) -> Optional[Any]:
        """Get a specific parameter value
        
        Args:
            param_name: Parameter name
            
        Returns:
            Any: Parameter value, or None if not found
        """
        return self.parameters.get_parameter(param_name)
    
    def set_parameter(self, param_name: str, value: Any) -> bool:
        """Set a parameter value
        
        Args:
            param_name: Parameter name
            value: Parameter value
            
        Returns:
            bool: True if set successfully, False otherwise
        """
        return self.parameters.set_parameter(param_name, value)