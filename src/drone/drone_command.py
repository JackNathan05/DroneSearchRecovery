# src/drone/drone_command.py
import logging
import time
from typing import Dict, Any, Optional, Tuple, List, Union
import math
from src.drone import dronekit_wrapper as dronekit
from dronekit import Vehicle, VehicleMode, LocationGlobal, LocationGlobalRelative
from pymavlink import mavutil

logger = logging.getLogger(__name__)

class DroneCommand:
    """Handles sending commands to a drone via MAVLink"""
    
    def __init__(self, vehicle: Optional[Vehicle] = None):
        """Initialize with optional vehicle
        
        Args:
            vehicle: DroneKit Vehicle object
        """
        self.vehicle = vehicle
    
    def set_vehicle(self, vehicle: Vehicle):
        """Set the vehicle to command
        
        Args:
            vehicle: DroneKit Vehicle object
        """
        self.vehicle = vehicle
    
    def arm(self, timeout: int = 30) -> bool:
        """Arm the drone
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            bool: True if successfully armed, False otherwise
        """
        if not self.vehicle:
            logger.error("No vehicle available for arming")
            return False
        
        # Don't try to arm if already armed
        if self.vehicle.armed:
            logger.info("Vehicle is already armed")
            return True
        
        # Make sure we're in a mode that allows arming
        if self.vehicle.mode.name != "GUIDED":
            logger.info("Setting vehicle mode to GUIDED for arming")
            self.set_mode("GUIDED")
            time.sleep(1)  # Wait a bit for mode change
        
        # Check if vehicle is armable
        if not self.vehicle.is_armable:
            logger.warning("Vehicle is not armable, waiting...")
            # Wait for GPS lock and other checks
            start_time = time.time()
            while not self.vehicle.is_armable:
                if time.time() - start_time > timeout:
                    logger.error("Timeout waiting for vehicle to become armable")
                    return False
                time.sleep(1)
        
        # Arm the vehicle
        logger.info("Arming vehicle...")
        self.vehicle.armed = True
        
        # Wait for arming
        start_time = time.time()
        while not self.vehicle.armed:
            if time.time() - start_time > timeout:
                logger.error("Timeout waiting for vehicle to arm")
                return False
            time.sleep(1)
        
        logger.info("Vehicle armed successfully")
        return True
    
    def disarm(self, timeout: int = 30) -> bool:
        """Disarm the drone
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            bool: True if successfully disarmed, False otherwise
        """
        if not self.vehicle:
            logger.error("No vehicle available for disarming")
            return False
        
        # Don't try to disarm if already disarmed
        if not self.vehicle.armed:
            logger.info("Vehicle is already disarmed")
            return True
        
        # Make sure we're landed before disarming
        if self.vehicle.location.global_relative_frame.alt > 0.1:
            logger.warning("Vehicle appears to be in air, cannot disarm safely")
            return False
        
        # Disarm the vehicle
        logger.info("Disarming vehicle...")
        self.vehicle.armed = False
        
        # Wait for disarming
        start_time = time.time()
        while self.vehicle.armed:
            if time.time() - start_time > timeout:
                logger.error("Timeout waiting for vehicle to disarm")
                return False
            time.sleep(1)
        
        logger.info("Vehicle disarmed successfully")
        return True
    
    def set_mode(self, mode_name: str, timeout: int = 10) -> bool:
        """Set the flight mode
        
        Args:
            mode_name: Name of the flight mode (e.g., 'GUIDED', 'RTL', 'AUTO')
            timeout: Timeout in seconds
            
        Returns:
            bool: True if mode set successfully, False otherwise
        """
        if not self.vehicle:
            logger.error("No vehicle available for mode change")
            return False
        
        # Check if already in this mode
        if self.vehicle.mode.name == mode_name:
            logger.info(f"Vehicle is already in {mode_name} mode")
            return True
        
        try:
            # Set the flight mode
            logger.info(f"Setting mode to {mode_name}...")
            self.vehicle.mode = VehicleMode(mode_name)
            
            # Wait for mode change
            start_time = time.time()
            while self.vehicle.mode.name != mode_name:
                if time.time() - start_time > timeout:
                    logger.error(f"Timeout waiting for mode change to {mode_name}")
                    return False
                time.sleep(0.5)
            
            logger.info(f"Mode changed to {mode_name} successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error setting mode to {mode_name}: {str(e)}")
            return False
    
    def takeoff(self, target_altitude: float, timeout: int = 60) -> bool:
        """Take off to a specified altitude
        
        Args:
            target_altitude: Target altitude in meters (relative)
            timeout: Timeout in seconds
            
        Returns:
            bool: True if takeoff successful, False otherwise
        """
        if not self.vehicle:
            logger.error("No vehicle available for takeoff")
            return False
        
        # Ensure vehicle is armed and in GUIDED mode
        if not self.vehicle.armed:
            logger.info("Vehicle not armed, attempting to arm before takeoff")
            if not self.arm():
                logger.error("Failed to arm vehicle for takeoff")
                return False
        
        if self.vehicle.mode.name != "GUIDED":
            logger.info("Setting vehicle mode to GUIDED for takeoff")
            if not self.set_mode("GUIDED"):
                logger.error("Failed to set GUIDED mode for takeoff")
                return False
        
        # Initiate takeoff command
        try:
            logger.info(f"Taking off to altitude: {target_altitude}m...")
            self.vehicle.simple_takeoff(target_altitude)
            
            # Wait for the drone to reach the target altitude
            start_time = time.time()
            
            while True:
                current_altitude = self.vehicle.location.global_relative_frame.alt
                logger.debug(f"Current altitude: {current_altitude}m, Target: {target_altitude}m")
                
                # Check if we're close enough to the target altitude
                if current_altitude >= target_altitude * 0.95:  # Within 5% of target
                    logger.info(f"Reached target altitude: {current_altitude}m")
                    break
                
                # Check for timeout
                if time.time() - start_time > timeout:
                    logger.warning(f"Takeoff timeout! Reached altitude: {current_altitude}m")
                    return False
                
                # Wait a bit
                time.sleep(1)
            
            return True
            
        except Exception as e:
            logger.error(f"Takeoff failed: {str(e)}")
            return False
    
    def land(self, timeout: int = 120) -> bool:
        """Land the drone
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            bool: True if landing successful, False otherwise
        """
        if not self.vehicle:
            logger.error("No vehicle available for landing")
            return False
        
        try:
            logger.info("Initiating landing sequence...")
            
            # Set the mode to LAND
            if not self.set_mode("LAND"):
                logger.error("Failed to set LAND mode")
                return False
            
            # Wait for the drone to land
            start_time = time.time()
            
            while True:
                current_altitude = self.vehicle.location.global_relative_frame.alt
                logger.debug(f"Current altitude during landing: {current_altitude}m")
                
                # Check if we've landed (altitude near zero)
                if current_altitude <= 0.2:
                    logger.info("Vehicle has landed")
                    break
                
                # Check for timeout
                if time.time() - start_time > timeout:
                    logger.warning(f"Landing timeout! Current altitude: {current_altitude}m")
                    return False
                
                # Wait a bit
                time.sleep(1)
            
            return True
            
        except Exception as e:
            logger.error(f"Landing failed: {str(e)}")
            return False
    
    def return_to_launch(self, timeout: int = 120) -> bool:
        """Return to launch location
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            bool: True if RTL initiated successfully, False otherwise
        """
        if not self.vehicle:
            logger.error("No vehicle available for RTL")
            return False
        
        try:
            logger.info("Initiating return to launch (RTL)...")
            
            # Set the mode to RTL
            if not self.set_mode("RTL"):
                logger.error("Failed to set RTL mode")
                return False
            
            # Wait for the vehicle to start descending
            start_time = time.time()
            initial_altitude = self.vehicle.location.global_relative_frame.alt
            
            while True:
                current_altitude = self.vehicle.location.global_relative_frame.alt
                logger.debug(f"Current altitude during RTL: {current_altitude}m")
                
                # Check if we're descending (at home location)
                if current_altitude < initial_altitude * 0.9:  # 10% decrease indicates descent
                    logger.info("Vehicle is returning and descending")
                    break
                
                # Check for timeout
                if time.time() - start_time > timeout:
                    logger.warning("RTL timeout! Vehicle may still be navigating home")
                    return False
                
                # Wait a bit
                time.sleep(1)
            
            return True
            
        except Exception as e:
            logger.error(f"RTL failed: {str(e)}")
            return False
    
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
        if not self.vehicle:
            logger.error("No vehicle available for position command")
            return False
        
        try:
            # Ensure vehicle is in GUIDED mode
            if self.vehicle.mode.name != "GUIDED":
                logger.info("Setting vehicle mode to GUIDED for position command")
                if not self.set_mode("GUIDED"):
                    logger.error("Failed to set GUIDED mode for position command")
                    return False
            
            # Set groundspeed if specified
            if ground_speed is not None:
                self.vehicle.groundspeed = ground_speed
                logger.info(f"Set groundspeed to {ground_speed} m/s")
            
            # Create the target location
            target_location = LocationGlobalRelative(lat, lon, alt)
            
            # Send the command to go to the target location
            logger.info(f"Going to position: lat={lat}, lon={lon}, alt={alt}m")
            self.vehicle.simple_goto(target_location)
            
            return True
            
        except Exception as e:
            logger.error(f"Goto position failed: {str(e)}")
            return False
    
    def goto_position_with_heading(self, lat: float, lon: float, alt: float, heading: float, ground_speed: Optional[float] = None) -> bool:
        """Go to a specific position with a specific heading
        
        Args:
            lat: Target latitude
            lon: Target longitude
            alt: Target altitude (relative)
            heading: Target heading in degrees (0-359)
            ground_speed: Optional ground speed in m/s
            
        Returns:
            bool: True if command sent successfully, False otherwise
        """
        if not self.vehicle:
            logger.error("No vehicle available for position command")
            return False
        
        try:
            # Ensure vehicle is in GUIDED mode
            if self.vehicle.mode.name != "GUIDED":
                logger.info("Setting vehicle mode to GUIDED for position command")
                if not self.set_mode("GUIDED"):
                    logger.error("Failed to set GUIDED mode for position command")
                    return False
            
            # Set groundspeed if specified
            if ground_speed is not None:
                self.vehicle.groundspeed = ground_speed
                logger.info(f"Set groundspeed to {ground_speed} m/s")
            
            # Create the target location
            target_location = LocationGlobalRelative(lat, lon, alt)
            
            # Send the command to go to the target location (simple_goto doesn't control heading)
            logger.info(f"Going to position: lat={lat}, lon={lon}, alt={alt}m, heading={heading}°")
            
            # Send MAVLink command directly to control position and heading
            msg = self.vehicle.message_factory.set_position_target_global_int_encode(
                0,       # time_boot_ms (not used)
                0, 0,    # target system, target component
                mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT, # frame
                0b0000111111111000, # type_mask (only positions enabled)
                int(lat * 1e7), int(lon * 1e7), alt, # lat, lon, alt
                0, 0, 0, # x, y, z velocity in m/s (not used)
                0, 0, 0, # x, y, z acceleration (not used)
                math.radians(heading), 0  # yaw, yaw_rate (set yaw in radians)
            )
            
            # Send command to vehicle
            self.vehicle.send_mavlink(msg)
            
            return True
            
        except Exception as e:
            logger.error(f"Goto position with heading failed: {str(e)}")
            return False
    
    def set_airspeed(self, airspeed: float) -> bool:
        """Set the target airspeed
        
        Args:
            airspeed: Target airspeed in m/s
            
        Returns:
            bool: True if set successfully, False otherwise
        """
        if not self.vehicle:
            logger.error("No vehicle available for airspeed command")
            return False
        
        try:
            logger.info(f"Setting airspeed to {airspeed} m/s")
            self.vehicle.airspeed = airspeed
            return True
        except Exception as e:
            logger.error(f"Set airspeed failed: {str(e)}")
            return False
    
    def set_groundspeed(self, groundspeed: float) -> bool:
        """Set the target groundspeed
        
        Args:
            groundspeed: Target groundspeed in m/s
            
        Returns:
            bool: True if set successfully, False otherwise
        """
        if not self.vehicle:
            logger.error("No vehicle available for groundspeed command")
            return False
        
        try:
            logger.info(f"Setting groundspeed to {groundspeed} m/s")
            self.vehicle.groundspeed = groundspeed
            return True
        except Exception as e:
            logger.error(f"Set groundspeed failed: {str(e)}")
            return False
    
    def set_home_position(self, lat: float, lon: float, alt: float) -> bool:
        """Set the home position
        
        Args:
            lat: Home latitude
            lon: Home longitude
            alt: Home altitude (absolute)
            
        Returns:
            bool: True if set successfully, False otherwise
        """
        if not self.vehicle:
            logger.error("No vehicle available for set home command")
            return False
        
        try:
            logger.info(f"Setting home position to: lat={lat}, lon={lon}, alt={alt}m")
            
            # Send MAVLink command to set home position
            self.vehicle.home_location = LocationGlobal(lat, lon, alt)
            
            # Verify the change
            if self.vehicle.home_location:
                home = self.vehicle.home_location
                logger.info(f"New home position: lat={home.lat}, lon={home.lon}, alt={home.alt}m")
                return True
            else:
                logger.error("Home position not set")
                return False
                
        except Exception as e:
            logger.error(f"Set home position failed: {str(e)}")
            return False