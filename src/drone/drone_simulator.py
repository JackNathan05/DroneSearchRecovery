# src/drone/drone_simulator.py
import os
import subprocess
import time
import signal
import threading
import logging
import atexit
from src.drone import dronekit_wrapper as dronekit

logger = logging.getLogger(__name__)

class DroneSimulator:
    """Manages a simulated drone for testing"""
    
    def __init__(self, home_location=(40.071374, -105.229195, 1585)):
        """Initialize the simulator
        
        Args:
            home_location: (lat, lon, alt) for the simulated drone's home position
        """
        self.home_location = home_location
        self.process = None
        self.is_running = False
        self.connection_string = "tcp:127.0.0.1:5760"
    
    def start(self):
        """Start the simulator"""
        if self.is_running:
            logger.info("Simulator already running")
            return True
            
        try:
            # Command to start SITL
            cmd = [
                "sim_vehicle.py",  # You'll need to install DroneKit-SITL
                "-v", "ArduCopter",
                "--location", f"{self.home_location[0]},{self.home_location[1]},{self.home_location[2]},0",
                "--no-mavproxy"
            ]
            
            logger.info(f"Starting drone simulator: {' '.join(cmd)}")
            
            # Start the process
            self.process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False
            )
            
            # Register cleanup function
            atexit.register(self.stop)
            
            # Wait for simulator to start
            time.sleep(5)
            
            self.is_running = True
            logger.info("Drone simulator started")
            
            # Start output monitoring thread
            threading.Thread(target=self._monitor_output, daemon=True).start()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start simulator: {str(e)}")
            return False
    
    def stop(self):
        """Stop the simulator"""
        if not self.is_running or not self.process:
            return
            
        try:
            logger.info("Stopping drone simulator...")
            
            # Try to terminate gracefully
            self.process.terminate()
            
            # Wait for process to terminate
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if it doesn't terminate
                self.process.kill()
            
            self.is_running = False
            self.process = None
            
            logger.info("Drone simulator stopped")
            
        except Exception as e:
            logger.error(f"Error stopping simulator: {str(e)}")
    
    def _monitor_output(self):
        """Monitor simulator output for logging"""
        while self.is_running and self.process:
            try:
                # Read output and log it
                output = self.process.stdout.readline()
                if output:
                    logger.debug(f"Simulator: {output.decode().strip()}")
            except:
                # Break the loop if we can't read output
                break