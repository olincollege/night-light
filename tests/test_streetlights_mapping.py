import os
import time

import folium
from folium.plugins import MarkerCluster

from night_light.utils import create_folium_map
from night_light.utils.mapping import open_html_file
from tests.conftest import BOSTON_CENTER_COORD


def test_boston_streetlights_map(boston_streetlights):
    """Test creating a map of the Boston streetlights"""
    map_filename = "test_boston_streetlights.html"
    streetlights_marker_cluster = MarkerCluster(
        name="Streetlights", show=True, control=True, overlay=True
    )
    for _, row in boston_streetlights.iterrows():
        tooltip_text = (
            f"Streetlight ID: {row['OBJECTID']}<br>"
            f"Fixture Type: {row['Final_Fixture_Type']}<br>"
            f"Wattage: {row['Final_Wattage']}<br>"
            f"Bulb Type: {row['Final_Bulb_Type']}<br>"
            f"Luminaires Per Pole: {row['Final_Luminaires_Per_Pole']}"
        )

        folium.Marker(
            location=[row.geometry.y, row.geometry.x],
            tooltip=tooltip_text,
            icon=folium.Icon(color="yellow", icon="lightbulb-o", prefix="fa"),
        ).add_to(streetlights_marker_cluster)

    create_folium_map(
        layers=[streetlights_marker_cluster],
        zoom_start=12,
        center=BOSTON_CENTER_COORD,
        map_filename=map_filename,
    )
    assert os.path.exists(map_filename)
    open_html_file(map_filename)
    time.sleep(1)
    os.remove(map_filename)
    assert not os.path.exists(map_filename)
