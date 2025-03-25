# src/utils/config.py
import os
import json
import logging

logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_CONFIG = {
    "app": {
        "name": "Drone Search & Recovery",
        "version": "0.1.0",
    },
    "ui": {
        "theme": "light",
        "colors": {
            "primary": "#4A90E2",
            "secondary": "#1E3A8A",
            "accent": "#FF7E47",
            "neutral": "#D1D5DB",
            "background": "#FFFFFF"
        }
    },
    "drone": {
        "connection_timeout": 10,
        "telemetry_frequency": 2.0,  # Hz
        "command_timeout": 5.0,      # seconds
    },
    "mapping": {
        "default_zoom": 13,
        "default_view": "satellite",
        "cache_enabled": True,
        "cache_max_size": 200        # MB
    },
    "paths": {
        "missions": "data/missions",
        "logs": "data/logs",
        "backup": "data/backup"
    }
}

class Config:
    """Application configuration handler"""
    
    def __init__(self, config_path="data/config.json"):
        """Initialize with default or saved configuration"""
        self.config_path = config_path
        self.config = DEFAULT_CONFIG.copy()
        
        # Load configuration if exists
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    saved_config = json.load(f)
                self._update_nested_dict(self.config, saved_config)
                logger.info("Configuration loaded from %s", config_path)
            except Exception as e:
                logger.error("Failed to load configuration: %s", str(e))
        else:
            self.save()
            logger.info("Created default configuration at %s", config_path)
    
    def save(self):
        """Save current configuration to file"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=4)
        logger.info("Configuration saved to %s", self.config_path)
    
    def get(self, path, default=None):
        """Get a configuration value by path (e.g., 'ui.theme')"""
        keys = path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, path, value):
        """Set a configuration value by path"""
        keys = path.split('.')
        config = self.config
        
        # Navigate to the nested dictionary
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # Set the value
        config[keys[-1]] = value
        self.save()
    
    def _update_nested_dict(self, d, u):
        """Update nested dictionary with another"""
        for k, v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                self._update_nested_dict(d[k], v)
            else:
                d[k] = v