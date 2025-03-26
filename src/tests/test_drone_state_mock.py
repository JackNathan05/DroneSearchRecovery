# src/tests/test_drone_state_mock.py
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
from src.drone.drone_state import DroneState

class TestDroneStateMock(unittest.TestCase):
    """Tests for the DroneState class using mocks"""
    
    def setUp(self):
        """Set up for each test"""
        self.state = DroneState()
        
    def tearDown(self):
        """Clean up after each test"""
        if hasattr(self.state, 'vehicle'):
            self.state.clear_vehicle()
    
    def test_set_vehicle(self):
        """Test setting the vehicle"""
        # Create mock vehicle
        mock_vehicle = MagicMock()
        
        # Call the method under test
        self.state.set_vehicle(mock_vehicle)
        
        # Assert results
        self.assertEqual(self.state.vehicle, mock_vehicle)
    
    def test_clear_vehicle(self):
        """Test clearing the vehicle"""
        # Create and set mock vehicle
        mock_vehicle = MagicMock()
        self.state.set_vehicle(mock_vehicle)
        
        # Call the method under test
        self.state.clear_vehicle()
        
        # Assert results
        self.assertIsNone(self.state.vehicle)
    
    def test_update_location(self):
        """Test location updates"""
        # Create mock vehicle and location
        mock_vehicle = MagicMock()
        mock_location = MagicMock()
        
        # Configure mock location
        mock_global_frame = MagicMock()
        mock_global_frame.lat = 40.0
        mock_global_frame.lon = -105.0
        mock_global_frame.alt = 1000.0
        
        mock_global_relative_frame = MagicMock()
        mock_global_relative_frame.alt = 100.0
        
        mock_location.global_frame = mock_global_frame
        mock_location.global_relative_frame = mock_global_relative_frame
        
        # Set up callback tracking
        callback_called = [False]
        def state_callback(state):
            callback_called[0] = True
        
        self.state.register_state_change_callback(state_callback)
        
        # Call the update method
        self.state._update_location(mock_vehicle, 'location', mock_location)
        
        # Assert results
        self.assertEqual(self.state.latitude, 40.0)
        self.assertEqual(self.state.longitude, -105.0)
        self.assertEqual(self.state.altitude, 1000.0)
        self.assertEqual(self.state.relative_altitude, 100.0)
        self.assertTrue(callback_called[0])
    
    def test_get_state(self):
        """Test getting the complete state"""
        # Set some state values
        self.state.latitude = 40.0
        self.state.longitude = -105.0
        self.state.altitude = 1000.0
        self.state.mode = "GUIDED"
        self.state.armed = True
        
        # Call the method under test
        state = self.state.get_state()
        
        # Assert results
        self.assertEqual(state["latitude"], 40.0)
        self.assertEqual(state["longitude"], -105.0)
        self.assertEqual(state["altitude"], 1000.0)
        self.assertEqual(state["mode"], "GUIDED")
        self.assertEqual(state["armed"], True)