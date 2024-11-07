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


def test_boston_map(boston_traffic, boston_crosswalk):
    """
    Test creating a complete map of the Boston with multiple layers.

    Layers:
    - Average Annual Daily Traffic
    - Crosswalk
    """
    map_filename = "test_boston_crosswalk.html"
    adt_layer = folium.GeoJson(
        boston_traffic,
        name=f"Annual Daily Traffic",
        style_function=lambda x: LAYER_STYLE_DICT,
        highlight_function=lambda x: LAYER_HIGHLIGHT_STYLE_DICT,
        smooth_factor=2.0,
        tooltip=Tooltip(
            fields=["Route_ID", "AADT", "Facility"],
            aliases=["Route ID", "Average Annual Daily Traffic", "Facility Type"],
            max_width=800,
        ),
    )
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
        layers=[adt_layer, crosswalk_layer],
        zoom_start=12,
        center=BOSTON_CENTER_COORD,
        map_filename=map_filename,
    )

    assert os.path.exists(map_filename)
    open_html_file(map_filename)
    time.sleep(1)
    os.remove(map_filename)
    assert not os.path.exists(map_filename)
