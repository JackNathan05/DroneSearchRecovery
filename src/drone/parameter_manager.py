# src/drone/parameter_manager.py
import logging
import time
from typing import Dict, Any, Optional, Tuple, List, Union
from src.drone import dronekit_wrapper as dronekit
from dronekit import Vehicle

logger = logging.getLogger(__name__)

class ParameterManager:
    """Manages vehicle parameters"""
    
    def __init__(self, vehicle: Optional[Vehicle] = None):
        """Initialize with optional vehicle
        
        Args:
            vehicle: DroneKit Vehicle object
        """
        self.vehicle = vehicle
    
    def set_vehicle(self, vehicle: Vehicle):
        """Set the vehicle to manage
        
        Args:
            vehicle: DroneKit Vehicle object
        """
        self.vehicle = vehicle
    
    def get_all_parameters(self) -> Dict[str, Any]:
        """Get all vehicle parameters
        
        Returns:
            dict: Dictionary of parameter names and values
        """
        if not self.vehicle:
            logger.error("No vehicle available for parameter retrieval")
            return {}
        
        try:
            # Wait for parameters to be available
            if not self.vehicle.parameters:
                logger.info("Waiting for parameters...")
                while not self.vehicle.parameters:
                    time.sleep(0.5)
            
            # Get all parameters
            parameters = {}
            for key, value in self.vehicle.parameters.items():
                parameters[key] = value
            
            logger.info(f"Retrieved {len(parameters)} parameters")
            return parameters
            
        except Exception as e:
            logger.error(f"Get parameters failed: {str(e)}")
            return {}
    
    def get_parameter(self, param_name: str) -> Optional[Any]:
        """Get a specific parameter value
        
        Args:
            param_name: Parameter name
            
        Returns:
            Any: Parameter value, or None if not found
        """
        if not self.vehicle:
            logger.error("No vehicle available for parameter retrieval")
            return None
        
        try:
            # Wait for parameters to be available
            if not self.vehicle.parameters:
                logger.info("Waiting for parameters...")
                while not self.vehicle.parameters:
                    time.sleep(0.5)
            
            # Get the parameter
            if param_name in self.vehicle.parameters:
                value = self.vehicle.parameters[param_name]
                logger.info(f"Parameter {param_name} = {value}")
                return value
            else:
                logger.warning(f"Parameter {param_name} not found")
                return None
                
        except Exception as e:
            logger.error(f"Get parameter {param_name} failed: {str(e)}")
            return None
    
    def set_parameter(self, param_name: str, value: Any) -> bool:
        """Set a parameter value
        
        Args:
            param_name: Parameter name
            value: Parameter value
            
        Returns:
            bool: True if set successfully, False otherwise
        """
        if not self.vehicle:
            logger.error("No vehicle available for parameter setting")
            return False
        
        try:
            # Wait for parameters to be available
            if not self.vehicle.parameters:
                logger.info("Waiting for parameters...")
                while not self.vehicle.parameters:
                    time.sleep(0.5)
            
            # Set the parameter
            logger.info(f"Setting parameter {param_name} = {value}")
            self.vehicle.parameters[param_name] = value
            
            # Verify the change
            time.sleep(0.5)  # Give some time for the change to take effect
            if param_name in self.vehicle.parameters:
                actual_value = self.vehicle.parameters[param_name]
                if actual_value == value:
                    logger.info(f"Parameter {param_name} set to {value} successfully")
                    return True
                else:
                    logger.warning(f"Parameter {param_name} set to {actual_value}, not {value}")
                    return False
            else:
                logger.warning(f"Parameter {param_name} not found after setting")
                return False
                
        except Exception as e:
            logger.error(f"Set parameter {param_name} failed: {str(e)}")
            return False
    
    def get_parameter_groups(self) -> Dict[str, List[str]]:
        """Group parameters by prefix for easier management
        
        Returns:
            dict: Dictionary of parameter groups and parameter names
        """
        if not self.vehicle:
            logger.error("No vehicle available for parameter grouping")
            return {}
        
        try:
            # Wait for parameters to be available
            if not self.vehicle.parameters:
                logger.info("Waiting for parameters...")
                while not self.vehicle.parameters:
                    time.sleep(0.5)
            
            # Group parameters
            groups = {}
            for key in self.vehicle.parameters.keys():
                # Extract group prefix (e.g., ARMING, BATT, GPS)
                parts = key.split('_')
                if len(parts) > 1:
                    group = parts[0]
                else:
                    group = "OTHER"
                
                # Add to group
                if group not in groups:
                    groups[group] = []
                groups[group].append(key)
            
            logger.info(f"Grouped parameters into {len(groups)} categories")
            return groups
            
        except Exception as e:
            logger.error(f"Get parameter groups failed: {str(e)}")
            return {}
    
    def save_parameters_to_file(self, filename: str) -> bool:
        """Save all parameters to a file
        
        Args:
            filename: Path to save parameters
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        if not self.vehicle:
            logger.error("No vehicle available for parameter saving")
            return False
        
        try:
            # Get all parameters
            parameters = self.get_all_parameters()
            if not parameters:
                logger.error("No parameters to save")
                return False
            
            # Save to file
            logger.info(f"Saving {len(parameters)} parameters to {filename}")
            with open(filename, 'w') as f:
                for key, value in sorted(parameters.items()):
                    f.write(f"{key}={value}\n")
            
            logger.info(f"Parameters saved to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Save parameters failed: {str(e)}")
            return False
    
    def load_parameters_from_file(self, filename: str, apply: bool = False) -> Dict[str, Any]:
        """Load parameters from a file
        
        Args:
            filename: Path to parameter file
            apply: Whether to apply parameters to vehicle
            
        Returns:
            dict: Dictionary of loaded parameters
        """
        parameters = {}
        
        try:
            # Load from file
            logger.info(f"Loading parameters from {filename}")
            with open(filename, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split('=')
                        if len(parts) == 2:
                            key = parts[0].strip()
                            value_str = parts[1].strip()
                            
                            # Try to convert value to appropriate type
                            try:
                                # Try as int
                                value = int(value_str)
                            except ValueError:
                                try:
                                    # Try as float
                                    value = float(value_str)
                                except ValueError:
                                    # Keep as string
                                    value = value_str
                            
                            parameters[key] = value
            
            logger.info(f"Loaded {len(parameters)} parameters from {filename}")
            
            # Apply parameters if requested
            if apply and self.vehicle:
                logger.info(f"Applying {len(parameters)} parameters to vehicle")
                success_count = 0
                for key, value in parameters.items():
                    if self.set_parameter(key, value):
                        success_count += 1
                
                logger.info(f"Applied {success_count} out of {len(parameters)} parameters")
            
            return parameters
            
        except Exception as e:
            logger.error(f"Load parameters failed: {str(e)}")
            return {}