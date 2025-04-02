import folium
import json
from folium.plugins import Draw, MeasureControl
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QObject, pyqtSignal

class MapManager(QObject):
    def __init__(self, view):
        super().__init__()  # ✅ This line is missing — you MUST call it
        self.view = view  # This gets set via set_view()
        self.map = None
        self.shape_data = None
        self.draw_plugin = None
        self.active_shape = None
        self.drawn_shapes = []

    def create_map(self, center=(47.6062, -122.3321), zoom=13):
        self.map = folium.Map(location=center, zoom_start=zoom, control_scale=True)

        # Add drawing tools and measurement control
        self.draw_plugin = Draw(export=True)
        self.map.add_child(self.draw_plugin)
        self.map.add_child(MeasureControl(primary_length_unit='meters'))

        return self.map

    def save_map(self, path="data/maps/latest_map.html"):
        if self.map:
            self.map.save(path)
        return path

    def set_view(self, view):
        self.view = view

    def set_active_shape(self, shape):
        """
        Called when a shape is drawn or edited.
        `shape` should be a list of (lat, lon) tuples.
        """
        self.active_shape = shape
        if self.view:
            self.view.update_map()

    def get_active_shape(self):
        return self.active_shape
    
    def get_drawn_shapes(self):
        return self.drawn_shapes if hasattr(self, 'drawn_shapes') else []

    @pyqtSlot(str)
    def handle_shape_update(self, shape_coords):
        # Wrap the coordinates in a shape dictionary
        shape = {
            "type": "polygon",
            "coordinates": json.loads(shape_coords) if isinstance(shape_coords, str) else shape_coords
        }
        self.drawn_shapes = [shape]
        print(f"[DEBUG] Stored new drawn shape: {shape}")

        if self.view and hasattr(self.view, 'update_map'):
            self.view.update_map()