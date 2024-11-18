import pytest
import os
from night_light.utils import query_geojson


def test_save_boston_traffic_speed_geojson(boston_traffic_speed):
    """
    Test saving Boston traffic speed data to a geojson
    """
    geojson_name = "tests/test_road_speeds.geojson"
    saved_gdf = query_geojson.gpd.read_file(geojson_name)

    assert boston_traffic_speed.crs == saved_gdf.crs
    assert list(boston_traffic_speed.columns) == list(saved_gdf.columns)
    assert boston_traffic_speed.shape == saved_gdf.shape

    os.remove(geojson_name)
    assert not os.path.exists(geojson_name)
