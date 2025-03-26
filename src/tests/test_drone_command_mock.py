# src/tests/test_drone_command_mock.py
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
from src.drone.drone_command import DroneCommand
from pymavlink import mavutil

class TestDroneCommandMock(unittest.TestCase):
    """Tests for the DroneCommand class using mocks"""
    
    def setUp(self):
        """Set up for each test"""
        self.command = DroneCommand()
        self.mock_vehicle = MagicMock()
        self.command.set_vehicle(self.mock_vehicle)
        
    def test_arm(self):
        """Test arming the drone"""
        # Configure the mock
        self.mock_vehicle.armed = False
        self.mock_vehicle.is_armable = True
        self.mock_vehicle.mode.name = "GUIDED"
        
        # Make the 'armed' property change when set
        def set_armed(value):
            self.mock_vehicle.armed = value
            return True
        
        type(self.mock_vehicle).armed = MagicMock(
            return_value=False, 
            side_effect=set_armed
        )
        
        # Call the method under test
        result = self.command.arm()
        
        # Assert results
        self.assertTrue(result)
        self.assertTrue(self.mock_vehicle.armed)
    
    def test_arm_not_armable(self):
        """Test arming when drone is not armable"""
        # Configure the mock
        self.mock_vehicle.armed = False
        self.mock_vehicle.is_armable = False
        self.mock_vehicle.mode.name = "GUIDED"
        
        # Override time.time to simulate timeout
        original_time = time.time
        time.time = MagicMock(side_effect=[0, 31])  # Start time, timeout check
        
        try:
            # Call the method under test
            result = self.command.arm(timeout=30)
            
            # Assert results
            self.assertFalse(result)
            self.assertFalse(self.mock_vehicle.armed)
        finally:
            # Restore original time function
            time.time = original_time
    
    def test_disarm(self):
        """Test disarming the drone"""
        # Configure the mock
        self.mock_vehicle.armed = True
        self.mock_vehicle.location.global_relative_frame.alt = 0.0
        
        # Make the 'armed' property change when set
        def set_armed(value):
            self.mock_vehicle.armed = value
            return True
        
        type(self.mock_vehicle).armed = MagicMock(
            return_value=True, 
            side_effect=set_armed
        )
        
        # Call the method under test
        result = self.command.disarm()
        
        # Assert results
        self.assertTrue(result)
        self.assertFalse(self.mock_vehicle.armed)
    
    def test_set_mode(self):
        """Test setting flight mode"""
        # Configure the mock
        mock_mode = MagicMock()
        mock_mode.name = "GUIDED"
        self.mock_vehicle.mode = mock_mode
        
        # Override time.time to avoid timeout
        original_time = time.time
        time.time = MagicMock(side_effect=[0, 0.5])  # Start time, check time
        
        try:
            # Call the method under test
            result = self.command.set_mode("GUIDED")
            
            # Assert results
            self.assertTrue(result)
            # Since the mode is already "GUIDED", we don't expect a change
        finally:
            # Restore original time function
            time.time = original_time