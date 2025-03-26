# src/tests/test_drone_connection_mock.py
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
from src.drone.drone_connection import DroneConnection

class TestDroneConnectionMock(unittest.TestCase):
    """Tests for the DroneConnection class using mocks"""
    
    def setUp(self):
        """Set up for each test"""
        self.connection = DroneConnection()
        
    def tearDown(self):
        """Clean up after each test"""
        if hasattr(self.connection, 'vehicle'):
            self.connection.vehicle = None
    
    @patch('dronekit.connect')
    def test_connect(self, mock_connect):
        """Test connecting with a mock"""
        # Configure the mock
        mock_vehicle = MagicMock()
        mock_connect.return_value = mock_vehicle
        
        # Call the method under test
        connected = self.connection.connect("mock:connection", is_simulation=True)
        
        # Assert results
        self.assertTrue(connected)
        self.assertTrue(self.connection.is_connected)
        self.assertEqual(self.connection.vehicle, mock_vehicle)
        mock_connect.assert_called_once()
    
    @patch('dronekit.connect')
    def test_connect_exception(self, mock_connect):
        """Test connection exception handling"""
        # Configure the mock to raise an exception
        mock_connect.side_effect = Exception("Test connection error")
        
        # Call the method under test
        connected = self.connection.connect("mock:connection")
        
        # Assert results
        self.assertFalse(connected)
        self.assertFalse(self.connection.is_connected)
        self.assertIsNone(self.connection.vehicle)
    
    def test_disconnect(self):
        """Test disconnecting"""
        # Create mock vehicle
        mock_vehicle = MagicMock()
        self.connection.vehicle = mock_vehicle
        self.connection.is_connected = True
        
        # Register a disconnection callback
        callback_called = [False]
        def on_disconnect():
            callback_called[0] = True
        self.connection.register_on_disconnection(on_disconnect)
        
        # Call the method under test
        self.connection.disconnect()
        
        # Assert results
        self.assertFalse(self.connection.is_connected)
        mock_vehicle.close.assert_called_once()
        self.assertTrue(callback_called[0])
    
    def test_connection_callbacks(self):
        """Test connection callbacks"""
        # Variables to track callback execution
        on_connect_called = [False]
        on_disconnect_called = [False]
        
        # Define callback functions
        def on_connect():
            on_connect_called[0] = True
        
        def on_disconnect():
            on_disconnect_called[0] = True
        
        # Register callbacks
        self.connection.register_on_connection(on_connect)
        self.connection.register_on_disconnection(on_disconnect)
        
        # Manually trigger callbacks
        self.connection._trigger_connection_callbacks()
        self.connection._trigger_disconnection_callbacks()
        
        # Check callback execution
        self.assertTrue(on_connect_called[0])
        self.assertTrue(on_disconnect_called[0])
    
    def test_unregister_callbacks(self):
        """Test unregistering callbacks"""
        # Variables to track callback execution
        on_connect_called = [False]
        on_disconnect_called = [False]
        
        # Define callback functions
        def on_connect():
            on_connect_called[0] = True
        
        def on_disconnect():
            on_disconnect_called[0] = True
        
        # Register callbacks
        self.connection.register_on_connection(on_connect)
        self.connection.register_on_disconnection(on_disconnect)
        
        # Unregister callbacks
        self.connection.unregister_on_connection(on_connect)
        self.connection.unregister_on_disconnection(on_disconnect)
        
        # Manually trigger callbacks
        self.connection._trigger_connection_callbacks()
        self.connection._trigger_disconnection_callbacks()
        
        # Check callback execution (shouldn't be called)
        self.assertFalse(on_connect_called[0])
        self.assertFalse(on_disconnect_called[0])