# map_generator.py

import os
import re
import folium
import math
from folium.plugins import Draw, MeasureControl
from geopy.distance import geodesic
from bs4 import BeautifulSoup
from folium import PolyLine, Marker
from folium.features import CustomIcon

def generate_folium_map(waypoints=None, speed_mps=5.0, altitude=50):
    if waypoints and len(waypoints) > 0:
        map_center = waypoints[0]
    else:
        map_center = [34.0734, -118.4449]  # Default center

    base_map = folium.Map(location=map_center, zoom_start=16)

    def get_altitude_color(alt):
        if altitude < 30:
            return 'green'
        elif altitude < 60:
            return 'orange'
        else:
            return 'red'

    if waypoints and len(waypoints) > 1:
        for i in range(len(waypoints) - 1):
            start = waypoints[i]
            end = waypoints[i + 1]

            color = get_altitude_color(altitude)

            # Draw path segment
            PolyLine(
                locations=[(start[0], start[1]), (end[0], end[1])],
                color=color,
                weight=2,
                opacity=1.0
            ).add_to(base_map)

            # Calculate direction arrow
            mid_lat = (start[0] + end[0]) / 2
            mid_lon = (start[1] + end[1]) / 2
            direction = math.degrees(math.atan2(end[1] - start[1], end[0] - start[0]))

            # Add arrow marker
            folium.RegularPolygonMarker(
                location=(mid_lat, mid_lon),
                number_of_sides=3,
                radius=6,
                rotation=direction - 90,
                color=color,
                fill=True,
                fill_opacity=0.9
            ).add_to(base_map)

    # Waypoint markers
    for idx, point in enumerate(waypoints or []):
        folium.CircleMarker(
            location=point,
            radius = 4,
            fill = True,
            fill_opacity = 0.7,
            tooltip=f"Waypoint {idx + 1}"
        ).add_to(base_map)

    # Calculate total distance and estimated time
    total_distance = sum(
        geodesic(waypoints[i - 1], waypoints[i]).meters for i in range(1, len(waypoints or []))
    )
    speed = speed_mps if isinstance(speed_mps, (int, float)) else 0
    estimated_time_sec = total_distance / speed if speed else 0
    minutes, seconds = divmod(int(estimated_time_sec), 60)

    # Add measurement + tile layers
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Satellite',
        overlay=False,
        control=True
    ).add_to(base_map)
    folium.TileLayer(
        tiles="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
        attr="Map data: © OpenTopoMap contributors",
        name="Topographic",
        overlay=False,
        control=True
    ).add_to(base_map)
    folium.TileLayer('CartoDB positron', name='Light').add_to(base_map)
    folium.LayerControl(collapsed=False).add_to(base_map)
    base_map.add_child(MeasureControl(primary_length_unit='meters'))
    base_map.add_child(Draw(export=True))

    # Add distance info overlay
    distance_time_display = f"""
    <div id="distance-info" 
        style="position: absolute; bottom: 20px; left: 20px; background-color: white; padding: 6px 10px; 
        border: 1px solid #ccc; border-radius: 5px; font-size: 13px; font-weight: bold; 
        color: black; z-index: 9999;">
        Total Distance: {total_distance:.1f} m<br>
        Estimated Time: {minutes}m {seconds}s
    </div>
    """
    base_map.get_root().html.add_child(folium.Element(distance_time_display))

    # Save the base HTML
    map_dir = os.path.join("data", "maps")
    os.makedirs(map_dir, exist_ok=True)
    map_path = os.path.join(map_dir, "latest_map.html")
    base_map.save(map_path)
    print(f"[DEBUG] Map saved to: {map_path}")

        # Inject WebChannel and JS draw + hover handling
    with open(map_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # Add qwebchannel.js once
    head = soup.find("head")
    if head:
        qweb_script = soup.new_tag("script", src="qrc:///qtwebchannel/qwebchannel.js")
        head.append(qweb_script)

    # Extract map variable name
    match = re.search(r"var (map_\w+) = L\.map", str(soup))
    map_var = match.group(1) if match else "map"

    # Combined JS
    combined_js = f"""
    <script>
        window.onload = function() {{
            new QWebChannel(qt.webChannelTransport, function(channel) {{
                const mapBridge = channel.objects.mapBridge;
                const coordinateBridge = channel.objects.coordinateBridge;
                const map = typeof {map_var} !== 'undefined' ? {map_var} : null;

                if (!map) {{
                    console.error("Map variable not found.");
                    return;
                }}

                // Hover & Click
                map.on('click', function(e) {{
                    if (coordinateBridge) {{
                        coordinateBridge.send_coordinates(e.latlng.lat, e.latlng.lng);
                    }}
                }});
                map.on('mousemove', function(e) {{
                    if (coordinateBridge) {{
                        coordinateBridge.send_hover_coordinates(e.latlng.lat, e.latlng.lng);
                    }}
                }});

                // Shape Drawing
                function onShapeDrawn(e) {{
                    let shape = e.layer;
                    let type = e.layerType;
                    let latlngs = [];

                    if (type === 'polygon' || type === 'rectangle') {{
                        shape.getLatLngs()[0].forEach(p => latlngs.push([p.lat, p.lng]));
                    }} else if (type === 'circle') {{
                        const center = shape.getLatLng();
                        const radius = shape.getRadius();
                        latlngs = [[center.lat, center.lng, radius]];
                    }}

                    if (mapBridge) {{
                        mapBridge.receiveShape(JSON.stringify(latlngs));
                    }}
                }}

                map.on('draw:created', onShapeDrawn);
                map.on('draw:edited', function(e) {{
                    e.layers.eachLayer(layer => onShapeDrawn({{ layer: layer, layerType: 'polygon' }}));
                }});
            }});
        }};
    </script>
    """

    soup.body.append(BeautifulSoup(combined_js, "html.parser"))

    with open(map_path, "w", encoding="utf-8") as f:
        f.write(str(soup))

    return map_path