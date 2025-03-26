# src/drone/dronekit_wrapper.py
import collections
import collections.abc
import sys

# Add MutableMapping to collections module for backward compatibility
if not hasattr(collections, 'MutableMapping'):
    collections.MutableMapping = collections.abc.MutableMapping

# Now import DroneKit
import dronekit

# Export all DroneKit components
sys.modules[__name__] = dronekit