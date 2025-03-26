# src/tests/test_mission_manager_mock.py
import unittest
from unittest.mock import MagicMock, patch
import time
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Fix for DroneKit compatibility with Python 3.9+
import collections
import collections.abc
collections.MutableMapping = collections.abc.MutableMapping

# Import the module to test
from src.drone.mission_manager import MissionManager
from pymavlink import mavutil

class TestMissionManagerMock(unittest.TestCase):
    """Tests for the MissionManager class using mocks"""
    
    def setUp(self):
        """Set up for each test"""
        self.mission_manager = MissionManager()
        self.mock_vehicle = MagicMock()
        self.mock_commands = MagicMock()
        self.mock_vehicle.commands = self.mock_commands
        self.mission_manager.set_vehicle(self.mock_vehicle)
        
    def test_clear_mission(self):
        """Test clearing the mission"""
        # Call the method under test
        result = self.mission_manager.clear_mission()
        
        # Assert results
        self.assertTrue(result)
        self.mock_commands.clear.assert_called_once()
        self.mock_commands.upload.assert_called_once()
    
    def test_download_mission(self):
        """Test downloading mission"""
        # Configure the mock
        mock_cmd1 = MagicMock()
        mock_cmd1.frame = 0
        mock_cmd1.command = 16  # MAV_CMD_NAV_WAYPOINT
        mock_cmd1.param1 = 0
        mock_cmd1.param2 = 0
        mock_cmd1.param3 = 0
        mock_cmd1.param4 = 0
        mock_cmd1.x = 40.0
        mock_cmd1.y = -105.0
        mock_cmd1.z = 100.0
        
        mock_cmd2 = MagicMock()
        mock_cmd2.frame = 0
        mock_cmd2.command = 20  # MAV_CMD_NAV_RETURN_TO_LAUNCH
        mock_cmd2.param1 = 0
        mock_cmd2.param2 = 0
        mock_cmd2.param3 = 0
        mock_cmd2.param4 = 0
        mock_cmd2.x = 0
        mock_cmd2.y = 0
        mock_cmd2.z = 0
        
        # Make commands iterable
        self.mock_commands.__iter__.return_value = [mock_cmd1, mock_cmd2]
        self.mock_commands.count = 2
        
        # Call the method under test
        waypoints = self.mission_manager.download_mission()
        
        # Assert results
        self.assertEqual(len(waypoints), 2)
        self.mock_commands.download.assert_called_once()
        self.mock_commands.wait_ready.assert_called_once()
    
    def test_create_waypoint_mission(self):
        """Test creating a waypoint mission"""
        # Define test waypoints
        test_waypoints = [
            (40.0, -105.0, 100.0),
            (40.1, -105.1, 150.0),
            (40.2, -105.2, 100.0)
        ]
        
        # Call the method under test
        mission = self.mission_manager.create_waypoint_mission(test_waypoints)
        
        # Assert results
        # Should be waypoints + home + RTL
        self.assertEqual(len(mission), len(test_waypoints) + 2)
        
        # Check first regular waypoint (index 1, after home)
        wp1 = mission[1]
        self.assertEqual(wp1["command"], mavutil.mavlink.MAV_CMD_NAV_WAYPOINT)
        self.assertEqual(wp1["x"], 40.0)
        self.assertEqual(wp1["y"], -105.0)
        self.assertEqual(wp1["z"], 100.0)
        
        # Check last waypoint is RTL
        last_wp = mission[-1]
        self.assertEqual(last_wp["command"], mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH)