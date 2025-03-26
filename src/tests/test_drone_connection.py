# src/tests/test_drone_connection.py
import unittest
import time
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.drone.drone_connection import DroneConnection
from src.drone.drone_simulator import DroneSimulator

class TestDroneConnection(unittest.TestCase):
    """Tests for the DroneConnection class"""
    
    @classmethod
    def setUpClass(cls):
        """Set up simulator for all tests"""
        cls.simulator = DroneSimulator()
        cls.simulator.start()
        time.sleep(5)  # Give simulator time to start
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests"""
        cls.simulator.stop()
    
    def setUp(self):
        """Set up for each test"""
        self.connection = DroneConnection()
    
    def tearDown(self):
        """Clean up after each test"""
        if self.connection.is_connected:
            self.connection.disconnect()
    
    def test_connect(self):
        """Test connecting to the simulator"""
        # Connect to simulator
        connected = self.connection.connect("tcp:127.0.0.1:5760", is_simulation=True)
        
        # Check connection status
        self.assertTrue(connected)
        self.assertTrue(self.connection.is_connected)
        self.assertIsNotNone(self.connection.vehicle)
    
    def test_disconnect(self):
        """Test disconnecting from the simulator"""
        # Connect first
        self.connection.connect("tcp:127.0.0.1:5760", is_simulation=True)
        
        # Then disconnect
        self.connection.disconnect()
        
        # Check connection status
        self.assertFalse(self.connection.is_connected)
    
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
        
        # Connect
        self.connection.connect("tcp:127.0.0.1:5760", is_simulation=True)
        time.sleep(1)  # Give time for callbacks to execute
        
        # Check on_connect callback
        self.assertTrue(on_connect_called[0])
        
        # Disconnect
        self.connection.disconnect()
        time.sleep(1)  # Give time for callbacks to execute
        
        # Check on_disconnect callback
        self.assertTrue(on_disconnect_called[0])