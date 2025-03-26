# src/tests/test_drone_controller_mock.py
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
from src.drone.drone_controller import DroneController

class TestDroneControllerMock(unittest.TestCase):
    """Tests for the DroneController class using mocks"""
    
    def setUp(self):
        """Set up for each test"""
        self.controller = DroneController()
        
        # Create patches for key components
        self.connection_patch = patch('src.drone.drone_connection.DroneConnection.connect')
        self.connect_mock = self.connection_patch.start()
        
        # Create mock vehicle
        self.mock_vehicle = MagicMock()
        self.mock_vehicle.mode.name = "GUIDED"
        self.mock_vehicle.armed = False
        self.mock_vehicle.is_armable = True
        
        # Configure the connection mock
        self.connect_mock.return_value = True
        
        # Add mock vehicle
        self.controller.connection.vehicle = self.mock_vehicle
    
    def tearDown(self):
        """Clean up after each test"""
        self.connection_patch.stop()
    
    def test_connect(self):
        """Test connecting to drone"""
        # Set up a side effect to trigger the callback when connect is called
        def connect_side_effect(*args, **kwargs):
            # Simulate successful connection
            self.controller._on_connect()  # This will set is_connected = True
            return True
        
        # Apply the side effect to our mock
        self.connect_mock.side_effect = connect_side_effect
        
        # Call the method under test
        result = self.controller.connect("mock:connection", is_simulation=True)
        
        # Assert results
        self.assertTrue(result)
        self.connect_mock.assert_called_once()
    
    @patch('src.drone.drone_command.DroneCommand.arm')
    def test_arm(self, mock_arm):
        """Test arming through controller"""
        # Configure the mock
        mock_arm.return_value = True
        
        # Make sure controller is connected
        self.controller.is_connected = True
        
        # Call the method under test
        result = self.controller.arm()
        
        # Assert results
        self.assertTrue(result)
        mock_arm.assert_called_once()
    
    @patch('src.drone.drone_command.DroneCommand.takeoff')
    def test_takeoff(self, mock_takeoff):
        """Test takeoff through controller"""
        # Configure the mock
        mock_takeoff.return_value = True
        
        # Make sure controller is connected
        self.controller.is_connected = True
        
        # Call the method under test
        result = self.controller.takeoff(10.0)
        
        # Assert results
        self.assertTrue(result)
        mock_takeoff.assert_called_once_with(10.0)
    
    @patch('src.drone.mission_manager.MissionManager.create_waypoint_mission')
    @patch('src.drone.mission_manager.MissionManager.upload_mission')
    def test_mission_operations(self, mock_upload, mock_create):
        """Test mission operations through controller"""
        # Configure the mocks
        mock_waypoints = [{"command": 16, "x": 40.0, "y": -105.0, "z": 100.0}]
        mock_create.return_value = mock_waypoints
        mock_upload.return_value = True
        
        # Make sure controller is connected
        self.controller.is_connected = True
        
        # Test creating a waypoint mission
        test_points = [(40.0, -105.0, 100.0)]
        waypoints = self.controller.create_waypoint_mission(test_points)
        
        # Assert results
        self.assertEqual(waypoints, mock_waypoints)
        mock_create.assert_called_once_with(test_points, 0)
        
        # Test uploading the mission
        result = self.controller.upload_mission(waypoints)
        
        # Assert results
        self.assertTrue(result)
        mock_upload.assert_called_once_with(waypoints)