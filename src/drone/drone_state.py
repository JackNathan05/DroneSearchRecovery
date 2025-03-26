# src/drone/drone_state.py
import logging
import time
import threading
from typing import Dict, Any, Optional, Callable, List
from src.drone import dronekit_wrapper as dronekit
from dronekit import Vehicle, LocationGlobal, LocationGlobalRelative, VehicleMode

logger = logging.getLogger(__name__)

class DroneState:
    """Maintains the current state of the drone"""
    
    def __init__(self, vehicle: Optional[Vehicle] = None):
        """Initialize with an optional vehicle
        
        Args:
            vehicle: DroneKit Vehicle object
        """
        self.vehicle = vehicle
        
        # State attributes
        self.latitude = 0.0
        self.longitude = 0.0
        self.altitude = 0.0
        self.relative_altitude = 0.0
        self.heading = 0
        self.airspeed = 0.0
        self.groundspeed = 0.0
        self.roll = 0.0
        self.pitch = 0.0
        self.yaw = 0.0
        self.mode = ""
        self.armed = False
        self.battery_voltage = 0.0
        self.battery_level = 0.0
        self.battery_current = 0.0
        self.gps_fix = 0
        self.gps_satellites = 0
        self.last_update_time = 0.0
        
        # Attribute listeners
        self._setup_attribute_listeners()
        
        # State change callbacks
        self.state_change_callbacks = []
        
        # Update thread
        self.update_thread = None
        self.stop_update = threading.Event()
    
    def set_vehicle(self, vehicle: Vehicle):
        """Set the vehicle to monitor
        
        Args:
            vehicle: DroneKit Vehicle object
        """
        self.vehicle = vehicle
        self._setup_attribute_listeners()
        self._start_update_thread()
    
    def clear_vehicle(self):
        """Clear the vehicle reference"""
        self._stop_update_thread()
        self.vehicle = None
    
    def _setup_attribute_listeners(self):
        """Set up listeners for vehicle attributes"""
        if not self.vehicle:
            return
        
        # Add attribute listeners
        self.vehicle.add_attribute_listener('location', self._update_location)
        self.vehicle.add_attribute_listener('attitude', self._update_attitude)
        self.vehicle.add_attribute_listener('velocity', self._update_velocity)
        self.vehicle.add_attribute_listener('armed', self._update_armed)
        self.vehicle.add_attribute_listener('mode', self._update_mode)
        self.vehicle.add_attribute_listener('battery', self._update_battery)
        self.vehicle.add_attribute_listener('gps_0', self._update_gps)
        
        logger.debug("Vehicle attribute listeners set up")
    
    def _remove_attribute_listeners(self):
        """Remove all attribute listeners"""
        if not self.vehicle:
            return
        
        # Remove attribute listeners
        self.vehicle.remove_attribute_listener('location', self._update_location)
        self.vehicle.remove_attribute_listener('attitude', self._update_attitude)
        self.vehicle.remove_attribute_listener('velocity', self._update_velocity)
        self.vehicle.remove_attribute_listener('armed', self._update_armed)
        self.vehicle.remove_attribute_listener('mode', self._update_mode)
        self.vehicle.remove_attribute_listener('battery', self._update_battery)
        self.vehicle.remove_attribute_listener('gps_0', self._update_gps)
        
        logger.debug("Vehicle attribute listeners removed")
    
    def _update_location(self, vehicle, attribute_name, value):
        """Update location information
        
        Args:
            vehicle: DroneKit Vehicle
            attribute_name: Attribute name
            value: New value
        """
        if value and value.global_frame:
            self.latitude = value.global_frame.lat
            self.longitude = value.global_frame.lon
            self.altitude = value.global_frame.alt
            
        if value and value.global_relative_frame:
            self.relative_altitude = value.global_relative_frame.alt
        
        self.last_update_time = time.time()
        self._notify_state_change()
    
    def _update_attitude(self, vehicle, attribute_name, value):
        """Update attitude information
        
        Args:
            vehicle: DroneKit Vehicle
            attribute_name: Attribute name
            value: New value
        """
        if value:
            self.roll = value.roll
            self.pitch = value.pitch
            self.yaw = value.yaw
            
        self.last_update_time = time.time()
        self._notify_state_change()
    
    def _update_velocity(self, vehicle, attribute_name, value):
        """Update velocity information
        
        Args:
            vehicle: DroneKit Vehicle
            attribute_name: Attribute name
            value: New value
        """
        # TODO: Implement velocity updates
        self.last_update_time = time.time()
        self._notify_state_change()
    
    def _update_armed(self, vehicle, attribute_name, value):
        """Update armed status
        
        Args:
            vehicle: DroneKit Vehicle
            attribute_name: Attribute name
            value: New value
        """
        self.armed = value
        self.last_update_time = time.time()
        self._notify_state_change()
    
    def _update_mode(self, vehicle, attribute_name, value):
        """Update flight mode
        
        Args:
            vehicle: DroneKit Vehicle
            attribute_name: Attribute name
            value: New value
        """
        if value:
            self.mode = value.name
        
        self.last_update_time = time.time()
        self._notify_state_change()
    
    def _update_battery(self, vehicle, attribute_name, value):
        """Update battery information
        
        Args:
            vehicle: DroneKit Vehicle
            attribute_name: Attribute name
            value: New value
        """
        if value:
            self.battery_voltage = value.voltage
            self.battery_level = value.level
            self.battery_current = value.current
        
        self.last_update_time = time.time()
        self._notify_state_change()
    
    def _update_gps(self, vehicle, attribute_name, value):
        """Update GPS information
        
        Args:
            vehicle: DroneKit Vehicle
            attribute_name: Attribute name
            value: New value
        """
        if value:
            self.gps_fix = value.fix_type
            self.gps_satellites = value.satellites_visible
        
        self.last_update_time = time.time()
        self._notify_state_change()
    
    def _start_update_thread(self):
        """Start the update thread"""
        if self.update_thread and self.update_thread.is_alive():
            return
        
        self.stop_update.clear()
        self.update_thread = threading.Thread(target=self._update_loop)
        self.update_thread.daemon = True
        self.update_thread.start()
        logger.debug("State update thread started")
    
    def _stop_update_thread(self):
        """Stop the update thread"""
        if self.update_thread and self.update_thread.is_alive():
            self.stop_update.set()
            self.update_thread.join(timeout=2.0)
            logger.debug("State update thread stopped")
    
    def _update_loop(self):
        """Update loop for polling state information"""
        while not self.stop_update.is_set() and self.vehicle:
            try:
                # Update airspeed and groundspeed
                self.airspeed = self.vehicle.airspeed
                self.groundspeed = self.vehicle.groundspeed
                
                # Update heading
                if hasattr(self.vehicle, 'heading'):
                    self.heading = self.vehicle.heading
                
                # Only notify if something changed
                self._notify_state_change()
                
            except Exception as e:
                logger.error(f"Error in state update loop: {str(e)}")
            
            # Sleep for a bit
            time.sleep(0.5)
    
    def register_state_change_callback(self, callback: Callable):
        """Register a callback for state changes
        
        Args:
            callback: Function to call on state changes
        """
        if callback not in self.state_change_callbacks:
            self.state_change_callbacks.append(callback)
    
    def unregister_state_change_callback(self, callback: Callable):
        """Unregister a state change callback
        
        Args:
            callback: Function to unregister
        """
        if callback in self.state_change_callbacks:
            self.state_change_callbacks.remove(callback)
    
    def _notify_state_change(self):
        """Notify all registered callbacks of state change"""
        for callback in self.state_change_callbacks:
            try:
                callback(self.get_state())
            except Exception as e:
                logger.error(f"Error in state change callback: {str(e)}")
    
    def get_state(self) -> Dict[str, Any]:
        """Get the current drone state
        
        Returns:
            dict: Current state as a dictionary
        """
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "altitude": self.altitude,
            "relative_altitude": self.relative_altitude,
            "heading": self.heading,
            "airspeed": self.airspeed,
            "groundspeed": self.groundspeed,
            "roll": self.roll,
            "pitch": self.pitch,
            "yaw": self.yaw,
            "mode": self.mode,
            "armed": self.armed,
            "battery_voltage": self.battery_voltage,
            "battery_level": self.battery_level,
            "battery_current": self.battery_current,
            "gps_fix": self.gps_fix,
            "gps_satellites": self.gps_satellites,
            "last_update_time": self.last_update_time
        }