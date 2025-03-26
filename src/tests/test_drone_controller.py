# src/tests/test_drone_controller.py
import unittest
import time
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.drone.drone_controller import DroneController
from src.drone.drone_simulator import DroneSimulator

class TestDroneController(unittest.TestCase):
    """Integration tests for the DroneController"""
    
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
        self.controller = DroneController()
        self.controller.connect("tcp:127.0.0.1:5760", is_simulation=True)
        time.sleep(2)  # Wait for connection to establish fully
    
    def tearDown(self):
        """Clean up after each test"""
        if self.controller.is_connected:
            self.controller.disconnect()
    
    def test_get_state(self):
        """Test getting drone state"""
        state = self.controller.get_state()
        
        # Check that we got a valid state
        self.assertIsNotNone(state)
        self.assertIn("latitude", state)
        self.assertIn("longitude", state)
        self.assertIn("altitude", state)
        self.assertIn("mode", state)
    
    def test_arm_disarm(self):
        """Test arming and disarming"""
        # First, make sure we're in GUIDED mode
        self.controller.set_mode("GUIDED")
        time.sleep(1)
        
        # Arm
        armed = self.controller.arm()
        time.sleep(1)
        
        # Check arm status
        self.assertTrue(armed)
        state = self.controller.get_state()
        self.assertTrue(state["armed"])
        
        # Disarm
        disarmed = self.controller.disarm()
        time.sleep(1)
        
        # Check disarm status
        self.assertTrue(disarmed)
        state = self.controller.get_state()
        self.assertFalse(state["armed"])
    
    def test_mission_operations(self):
        """Test mission operations"""
        # Clear any existing mission
        cleared = self.controller.clear_mission()
        self.assertTrue(cleared)
        
        # Create a simple mission
        waypoints = [
            (40.071374, -105.229195, 10),  # First waypoint
            (40.071800, -105.229100, 15),  # Second waypoint
            (40.071900, -105.229500, 10)   # Third waypoint
        ]
        
        mission = self.controller.create_waypoint_mission(waypoints)
        
        # Mission should have waypoints plus home and RTL
        self.assertEqual(len(mission), len(waypoints) + 2)
        
        # Upload the mission
        uploaded = self.controller.upload_mission(mission)
        self.assertTrue(uploaded)
        
        # Download and verify
        downloaded = self.controller.download_mission()
        self.assertEqual(len(downloaded), len(mission))