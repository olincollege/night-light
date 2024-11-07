import os
import time

import folium

from night_light.utils import (
    create_folium_map,
    LAYER_STYLE_DICT,
    LAYER_HIGHLIGHT_STYLE_DICT,
    Tooltip,
)
from night_light.utils.mapping import open_html_file
from tests.conftest import BOSTON_CENTER_COORD


def test_boston_crosswalk_map(boston_crosswalk):
    """Test creating a map of the Boston crosswalk"""
    map_filename = "test_boston_crosswalk.html"
    crosswalk_layer = folium.GeoJson(
        boston_crosswalk,
        name="Crosswalk",
        style_function=lambda x: LAYER_STYLE_DICT,
        highlight_function=lambda x: LAYER_HIGHLIGHT_STYLE_DICT,
        smooth_factor=2.0,
        tooltip=Tooltip(
            fields=["OBJECTID", "CrossType", "Conf_Score"],
            aliases=["Crosswalk ID", "Crosswalk Type", "Confidence Score"],
            max_width=800,
        ),
    )
    create_folium_map(
        layers=[crosswalk_layer],
        zoom_start=12,
        center=BOSTON_CENTER_COORD,
        map_filename=map_filename,
    )
    assert os.path.exists(map_filename)
    open_html_file(map_filename)
    time.sleep(1)
    os.remove(map_filename)
    assert not os.path.exists(map_filename)
