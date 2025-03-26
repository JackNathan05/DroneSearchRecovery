# src/tests/test_parameter_manager_mock.py
import unittest
from unittest.mock import MagicMock, patch
import time
import sys
import os
import tempfile

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Fix for DroneKit compatibility with Python 3.9+
import collections
import collections.abc
collections.MutableMapping = collections.abc.MutableMapping

# Import the module to test
from src.drone.parameter_manager import ParameterManager

class TestParameterManagerMock(unittest.TestCase):
    """Tests for the ParameterManager class using mocks"""
    
    def setUp(self):
        """Set up for each test"""
        self.parameter_manager = ParameterManager()
        self.mock_vehicle = MagicMock()
        self.mock_params = {"ARMING_CHECK": 1, "RTL_ALT": 100, "WPNAV_SPEED": 500}
        
        # Add parameters to mock vehicle
        self.mock_vehicle.parameters = MagicMock()
        self.mock_vehicle.parameters.items.return_value = self.mock_params.items()
        self.mock_vehicle.parameters.__getitem__ = lambda _, k: self.mock_params.get(k)
        self.mock_vehicle.parameters.__contains__ = lambda _, k: k in self.mock_params
        
        self.parameter_manager.set_vehicle(self.mock_vehicle)
        
    def test_get_all_parameters(self):
        """Test getting all parameters"""
        # Call the method under test
        params = self.parameter_manager.get_all_parameters()
        
        # Assert results
        self.assertEqual(len(params), 3)
        self.assertEqual(params["ARMING_CHECK"], 1)
        self.assertEqual(params["RTL_ALT"], 100)
        self.assertEqual(params["WPNAV_SPEED"], 500)
    
    def test_get_parameter(self):
        """Test getting a specific parameter"""
        # Call the method under test
        value = self.parameter_manager.get_parameter("RTL_ALT")
        
        # Assert results
        self.assertEqual(value, 100)
    
    def test_get_nonexistent_parameter(self):
        """Test getting a parameter that doesn't exist"""
        # Call the method under test
        value = self.parameter_manager.get_parameter("NONEXISTENT")
        
        # Assert results
        self.assertIsNone(value)
    
    def test_save_parameters_to_file(self):
        """Test saving parameters to a file"""
        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Call the method under test
            result = self.parameter_manager.save_parameters_to_file(temp_path)
            
            # Assert results
            self.assertTrue(result)
            
            # Check file contents
            with open(temp_path, 'r') as f:
                content = f.read()
                self.assertIn("ARMING_CHECK=1", content)
                self.assertIn("RTL_ALT=100", content)
                self.assertIn("WPNAV_SPEED=500", content)
                
        finally:
            # Clean up
            os.unlink(temp_path)