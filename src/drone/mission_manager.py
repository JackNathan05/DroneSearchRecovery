# src/drone/mission_manager.py
import logging
import time
from typing import Dict, Any, Optional, Tuple, List, Union
from src.drone import dronekit_wrapper as dronekit
from dronekit import Vehicle, Command, LocationGlobal, LocationGlobalRelative
from pymavlink import mavutil

logger = logging.getLogger(__name__)

class MissionManager:
    """Manages mission waypoints for a drone"""
    
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
    
    def clear_mission(self) -> bool:
        """Clear the current mission
        
        Returns:
            bool: True if mission cleared successfully, False otherwise
        """
        if not self.vehicle:
            logger.error("No vehicle available for mission clear")
            return False
        
        try:
            logger.info("Clearing current mission...")
            cmds = self.vehicle.commands
            cmds.clear()
            cmds.upload()
            logger.info("Mission cleared successfully")
            return True
        except Exception as e:
            logger.error(f"Clear mission failed: {str(e)}")
            return False
    
    def download_mission(self) -> List[Dict[str, Any]]:
        """Download the current mission from the vehicle
        
        Returns:
            list: List of waypoint dictionaries
        """
        if not self.vehicle:
            logger.error("No vehicle available for mission download")
            return []
        
        try:
            logger.info("Downloading mission from vehicle...")
            cmds = self.vehicle.commands
            cmds.download()
            cmds.wait_ready()
            
            # Convert commands to a more usable format
            mission = []
            for i, cmd in enumerate(cmds):
                waypoint = {
                    "seq": i,
                    "frame": cmd.frame,
                    "command": cmd.command,
                    "param1": cmd.param1,
                    "param2": cmd.param2,
                    "param3": cmd.param3,
                    "param4": cmd.param4,
                    "x": cmd.x,  # Latitude
                    "y": cmd.y,  # Longitude
                    "z": cmd.z,  # Altitude
                }
                mission.append(waypoint)
            
            logger.info(f"Downloaded mission with {len(mission)} waypoints")
            return mission
            
        except Exception as e:
            logger.error(f"Download mission failed: {str(e)}")
            return []
    
    def upload_mission(self, waypoints: List[Dict[str, Any]]) -> bool:
        """Upload a mission to the vehicle
        
        Args:
            waypoints: List of waypoint dictionaries
            
        Returns:
            bool: True if mission uploaded successfully, False otherwise
        """
        if not self.vehicle:
            logger.error("No vehicle available for mission upload")
            return False
        
        try:
            logger.info(f"Uploading mission with {len(waypoints)} waypoints...")
            
            # Clear existing mission
            cmds = self.vehicle.commands
            cmds.clear()
            
            # Add new commands
            for wp in waypoints:
                cmd = Command(
                    0, 0, 0,  # target_system, target_component, seq
                    wp.get("frame", mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT),
                    wp.get("command", mavutil.mavlink.MAV_CMD_NAV_WAYPOINT),
                    wp.get("current", 0),  # Set to 0, auto-populate based on upload
                    wp.get("autocontinue", 1),  # Auto-continue to next waypoint
                    wp.get("param1", 0),  # Hold time (seconds)
                    wp.get("param2", 0),  # Acceptance radius (meters)
                    wp.get("param3", 0),  # Pass radius (meters)
                    wp.get("param4", 0),  # Yaw (degrees)
                    wp.get("x", 0),  # Latitude
                    wp.get("y", 0),  # Longitude
                    wp.get("z", 0)   # Altitude
                )
                cmds.add(cmd)
            
            # Upload mission to vehicle
            cmds.upload()
            logger.info(f"Mission uploaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Upload mission failed: {str(e)}")
            return False
    
    def create_waypoint_mission(self, waypoints: List[Tuple[float, float, float]], hold_time: float = 0) -> List[Dict[str, Any]]:
        """Create a waypoint mission from a list of coordinates
        
        Args:
            waypoints: List of (latitude, longitude, altitude) tuples
            hold_time: Hold time at each waypoint in seconds
            
        Returns:
            list: List of waypoint dictionaries ready for upload
        """
        mission = []
        
        # Add home as first waypoint (0 is home)
        mission.append({
            "frame": mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
            "command": mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
            "param1": 0,  # Hold time
            "param2": 0,  # Acceptance radius
            "param3": 0,  # Pass radius
            "param4": 0,  # Yaw
            "x": 0,  # Latitude - will be overridden by vehicle
            "y": 0,  # Longitude - will be overridden by vehicle
            "z": 0    # Altitude - will be overridden by vehicle
        })
        
        # Add the waypoints
        for lat, lon, alt in waypoints:
            mission.append({
                "frame": mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                "command": mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
                "param1": hold_time,  # Hold time
                "param2": 2.0,        # Acceptance radius (meters)
                "param3": 0,          # Pass radius (meters)
                "param4": 0,          # Yaw (degrees)
                "x": lat,             # Latitude
                "y": lon,             # Longitude
                "z": alt              # Altitude (relative)
            })
        
        # Add RTL (Return to Launch) as final waypoint
        mission.append({
            "frame": mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
            "command": mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH,
            "param1": 0,  # Not used
            "param2": 0,  # Not used
            "param3": 0,  # Not used
            "param4": 0,  # Not used
            "x": 0,        # Not used
            "y": 0,        # Not used
            "z": 0         # Not used
        })
        
        logger.info(f"Created waypoint mission with {len(waypoints)} waypoints (plus home and RTL)")
        return mission
    
    def start_mission(self) -> bool:
        """Start the mission
        
        Returns:
            bool: True if mission started successfully, False otherwise
        """
        if not self.vehicle:
            logger.error("No vehicle available to start mission")
            return False
        
        try:
            logger.info("Starting mission...")
            
            # Set the mode to AUTO to start the mission
            self.vehicle.mode = "AUTO"
            
            # Wait for mode change
            start_time = time.time()
            while self.vehicle.mode.name != "AUTO":
                if time.time() - start_time > 5:
                    logger.error("Timeout waiting for AUTO mode")
                    return False
                time.sleep(0.5)
            
            logger.info("Mission started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Start mission failed: {str(e)}")
            return False
    
    def get_mission_status(self) -> Dict[str, Any]:
        """Get the current mission status
        
        Returns:
            dict: Mission status information
        """
        if not self.vehicle:
            return {"status": "no_vehicle", "progress": 0, "current_waypoint": 0}
        
        try:
            # Get the current mission status
            status = {
                "status": "unknown",
                "progress": 0,
                "current_waypoint": 0,
                "waypoint_count": 0
            }
            
            # Get the current mode
            mode = self.vehicle.mode.name
            
            # Get the current mission item
            wp = self.vehicle.commands.next
            count = self.vehicle.commands.count
            
            # Calculate progress
            if count > 0:
                progress = (wp - 1) / count * 100
            else:
                progress = 0
            
            # Update status
            if mode == "AUTO":
                if wp < count:
                    status["status"] = "in_progress"
                else:
                    status["status"] = "completed"
            elif mode == "RTL":
                status["status"] = "returning"
            else:
                status["status"] = "ready" if count > 0 else "no_mission"
            
            status["progress"] = progress
            status["current_waypoint"] = wp
            status["waypoint_count"] = count
            
            return status
            
        except Exception as e:
            logger.error(f"Get mission status failed: {str(e)}")
            return {"status": "error", "progress": 0, "current_waypoint": 0}