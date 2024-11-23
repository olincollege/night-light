import os

from night_light.past_accidents.vision_zero import boston_vision_zero_ped_accidents
from night_light.utils import query_geojson


def test_query_boston_vision_zero_ped_accidents():
    gdf_accidents = boston_vision_zero_ped_accidents()
    assert not gdf_accidents.empty
    assert "mode_type" in gdf_accidents.columns
    assert gdf_accidents.geometry.geom_type.unique() == "Point"
    assert gdf_accidents.crs == "EPSG:4326"
    assert gdf_accidents["mode_type"].unique() == "ped"
    assert not gdf_accidents["lat"].isnull().any()
    assert not gdf_accidents["long"].isnull().any()
    assert not gdf_accidents["is_fatal"].isnull().any()


def test_save_boston_vision_zero_ped_accidents():
    """Test saving the Boston Vision Zero accidents data to a GeoJSON file"""
    gdf_accidents = boston_vision_zero_ped_accidents()
    geojson_filename = "test_boston_vision_zero.geojson"

    query_geojson.save_geojson(gdf_accidents, geojson_filename)
    saved_gdf = query_geojson.gpd.read_file(geojson_filename)

    assert gdf_accidents.crs == saved_gdf.crs
    assert set(gdf_accidents.columns) == set(saved_gdf.columns)
    assert gdf_accidents.index.equals(saved_gdf.index)
    assert gdf_accidents.shape == saved_gdf.shape

    os.remove(geojson_filename)
    assert not os.path.exists(geojson_filename)
