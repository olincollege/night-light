import os
from night_light.utils import query_geojson


def test_query_boston_traffic_light(boston_traffic_lights):
    """
    Test querying Boston traffic light data
    """
    # assert boston_traffic_lights.shape[0] > 0
    assert boston_traffic_lights.geometry.name == "geometry"
    assert set(boston_traffic_lights.geometry.geom_type.unique()) == {"Point"}
    assert boston_traffic_lights.columns.to_list() == [
        "geometry",
        "OBJECTID",
        "Count_",
        "Int_Number",
        "Location",
        "Dist",
    ]
    assert boston_traffic_lights["Dist"].unique().size == 10


def test_save_boston_traffic_light(boston_traffic_lights):
    """
    Test saving Boston traffic light data to GeoJSON
    """
    geojson_name = "test_boston_traffic_lights.geojson"
    query_geojson.save_geojson(boston_traffic_lights, geojson_name)
    saved_gdf = query_geojson.gpd.read_file(geojson_name)

    assert boston_traffic_lights.crs == saved_gdf.crs
    assert set(boston_traffic_lights.columns) == set(saved_gdf.columns)
    assert boston_traffic_lights.index.equals(saved_gdf.index)
    assert boston_traffic_lights.shape == saved_gdf.shape

    os.remove(geojson_name)
    assert not os.path.exists(geojson_name)
