# src/drone/drone_connection.py
import logging
import time
import threading
from typing import Callable, Dict, List, Optional, Tuple, Union
from src.drone import dronekit_wrapper as dronekit
import dronekit
from pymavlink import mavutil

logger = logging.getLogger(__name__)

class DroneConnection:
    """Handles communication with a drone via MAVLink protocol"""
    
    def __init__(self):
        """Initialize the drone connection manager"""
        self.vehicle = None
        self.connection_string = ""
        self.is_connected = False
        self.is_simulation = False
        self.heartbeat_thread = None
        self.stop_heartbeat = threading.Event()
        
        # Callback handlers
        self.on_connection_callbacks = []
        self.on_disconnection_callbacks = []
        self.on_status_changed_callbacks = []
        
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
        self.connection_string = connection_string
        self.is_simulation = is_simulation
        
        try:
            logger.info(f"Connecting to drone on {connection_string}...")
            
            # Connect to the vehicle
            if "tcp:" in connection_string or "udp:" in connection_string:
                self.vehicle = dronekit.connect(connection_string, wait_ready=True, timeout=timeout)
            else:
                self.vehicle = dronekit.connect(connection_string, baud=baud, wait_ready=True, timeout=timeout)
            
            self.is_connected = True
            logger.info(f"Connected to drone on {connection_string}")
            
            # Start heartbeat monitoring
            self._start_heartbeat_monitoring()
            
            # Trigger connection callbacks
            self._trigger_connection_callbacks()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to drone: {str(e)}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """Disconnect from the drone"""
        if self.vehicle:
            try:
                # Stop heartbeat monitoring
                self._stop_heartbeat_monitoring()
                
                # Close the connection
                self.vehicle.close()
                self.is_connected = False
                logger.info("Disconnected from drone")
                
                # Trigger disconnection callbacks
                self._trigger_disconnection_callbacks()
                
            except Exception as e:
                logger.error(f"Error disconnecting from drone: {str(e)}")
    
    def _start_heartbeat_monitoring(self):
        """Start a thread to monitor the drone heartbeat"""
        if self.heartbeat_thread and self.heartbeat_thread.is_alive():
            return
        
        self.stop_heartbeat.clear()
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop)
        self.heartbeat_thread.daemon = True
        self.heartbeat_thread.start()
        logger.debug("Heartbeat monitoring started")
    
    def _stop_heartbeat_monitoring(self):
        """Stop the heartbeat monitoring thread"""
        if self.heartbeat_thread and self.heartbeat_thread.is_alive():
            self.stop_heartbeat.set()
            self.heartbeat_thread.join(timeout=2.0)
            logger.debug("Heartbeat monitoring stopped")
    
    def _heartbeat_loop(self):
        """Heartbeat monitoring loop"""
        last_heartbeat_time = time.time()
        was_connected = True
        
        while not self.stop_heartbeat.is_set():
            # Check if we're still connected
            if self.vehicle:
                # Get last heartbeat time
                try:
                    current_time = time.time()
                    time_since_last_heartbeat = current_time - self.vehicle.last_heartbeat
                    
                    # If we haven't received a heartbeat in 3 seconds, consider the connection lost
                    if time_since_last_heartbeat > 3.0:
                        if was_connected:
                            logger.warning(f"Lost heartbeat from drone, last heartbeat {time_since_last_heartbeat:.1f}s ago")
                            was_connected = False
                            self.is_connected = False
                            self._trigger_disconnection_callbacks()
                    else:
                        if not was_connected:
                            logger.info("Reconnected to drone, heartbeat restored")
                            was_connected = True
                            self.is_connected = True
                            self._trigger_connection_callbacks()
                except:
                    pass
                    
            # Sleep for a bit
            time.sleep(1.0)
    
    def register_on_connection(self, callback: Callable):
        """Register a callback for when the drone connects
        
        Args:
            callback: Function to call when connected
        """
        if callback not in self.on_connection_callbacks:
            self.on_connection_callbacks.append(callback)
    
    def unregister_on_connection(self, callback: Callable):
        """Unregister a connection callback
        
        Args:
            callback: Function to unregister
        """
        if callback in self.on_connection_callbacks:
            self.on_connection_callbacks.remove(callback)
    
    def register_on_disconnection(self, callback: Callable):
        """Register a callback for when the drone disconnects
        
        Args:
            callback: Function to call when disconnected
        """
        if callback not in self.on_disconnection_callbacks:
            self.on_disconnection_callbacks.append(callback)
    
    def unregister_on_disconnection(self, callback: Callable):
        """Unregister a disconnection callback
        
        Args:
            callback: Function to unregister
        """
        if callback in self.on_disconnection_callbacks:
            self.on_disconnection_callbacks.remove(callback)
    
    def register_on_status_changed(self, callback: Callable):
        """Register a callback for when the drone status changes
        
        Args:
            callback: Function to call when status changes
        """
        if callback not in self.on_status_changed_callbacks:
            self.on_status_changed_callbacks.append(callback)
    
    def unregister_on_status_changed(self, callback: Callable):
        """Unregister a status change callback
        
        Args:
            callback: Function to unregister
        """
        if callback in self.on_status_changed_callbacks:
            self.on_status_changed_callbacks.remove(callback)
    
    def _trigger_connection_callbacks(self):
        """Trigger all registered connection callbacks"""
        for callback in self.on_connection_callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error in connection callback: {str(e)}")
    
    def _trigger_disconnection_callbacks(self):
        """Trigger all registered disconnection callbacks"""
        for callback in self.on_disconnection_callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error in disconnection callback: {str(e)}")
    
    def _trigger_status_changed_callbacks(self):
        """Trigger all registered status change callbacks"""
        for callback in self.on_status_changed_callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error in status change callback: {str(e)}")
    
    def is_vehicle_connected(self) -> bool:
        """Check if the vehicle is connected
        
        Returns:
            bool: True if connected, False otherwise
        """
        return self.is_connected and self.vehicle is not None
    
    def get_connection_status(self) -> Dict:
        """Get the current connection status
        
        Returns:
            dict: Connection status information
        """
        status = {
            "connected": self.is_connected,
            "connection_string": self.connection_string,
            "is_simulation": self.is_simulation,
        }
        
        if self.vehicle and self.is_connected:
            status.update({
                "vehicle_type": self.vehicle.version,
                "autopilot_version": self.vehicle.version,
                "gps_status": self.vehicle.gps_0,
                "mode": self.vehicle.mode.name,
            })
        
        return status