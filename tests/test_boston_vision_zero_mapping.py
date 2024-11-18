import os
import time

import folium

from night_light.past_accidents.vision_zero import boston_vision_zero_ped_accidents
from night_light.utils import (
    create_folium_map,
    LAYER_STYLE_DICT,
    LAYER_HIGHLIGHT_STYLE_DICT,
    Tooltip,
)
from night_light.utils.mapping import open_html_file
from tests.conftest import BOSTON_CENTER_COORD


def test_boston_vision_zero_map():
    """Test creating a map of the Boston Vision Zero accidents"""
    boston_vision_zero_accidents = boston_vision_zero_ped_accidents()
    map_filename = "test_boston_vision_zero.html"
    accidents_layer = folium.GeoJson(
        boston_vision_zero_accidents,
        name="Vision Zero Accidents",
        style_function=lambda x: LAYER_STYLE_DICT,
        highlight_function=lambda x: LAYER_HIGHLIGHT_STYLE_DICT,
        smooth_factor=2.0,
        tooltip=Tooltip(
            fields=["_id", "is_fatal"],
            aliases=["Accident ID", "Fatality"],
            max_width=800,
        ),
    )
    create_folium_map(
        layers=[accidents_layer],
        zoom_start=12,
        center=BOSTON_CENTER_COORD,
        map_filename=map_filename,
    )
    assert os.path.exists(map_filename)
    open_html_file(map_filename)
    time.sleep(1)
    os.remove(map_filename)
    assert not os.path.exists(map_filename)
