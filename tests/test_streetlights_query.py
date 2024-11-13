import os
from night_light.utils import query_geojson


def test_query_boston_streetlights(boston_streetlights):
    """Test querying the Boston crosswalk"""
    assert boston_streetlights.shape[0] > 0
    assert boston_streetlights.crs == "EPSG:4326"
    assert boston_streetlights.geometry.name == "geometry"
    assert boston_streetlights.geometry.geom_type.unique()[0] == "Point"
    assert boston_streetlights.columns.to_list() == [
        "geometry",
        "OBJECTID",
        "Final_Fixture_Type",
        "Final_Wattage",
        "Final_Bulb_Type",
        "Final_Luminaires_Per_Pole",
    ]


def test_save_boston_streetlights_geojson(boston_streetlights):
    """Test saving the Boston streelights to a GeoJSON file"""
    query_geojson.save_geojson(boston_streetlights, "test_boston_streetlights.geojson")
    geojson_filename = "test_boston_streetlights.geojson"
    saved_gdf = query_geojson.gpd.read_file(geojson_filename)

    assert boston_streetlights.crs == saved_gdf.crs
    assert set(boston_streetlights.columns) == set(saved_gdf.columns)
    assert boston_streetlights.index.equals(saved_gdf.index)
    assert boston_streetlights.shape == saved_gdf.shape

    os.remove(geojson_filename)
    assert not os.path.exists(geojson_filename)
