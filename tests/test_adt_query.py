import os

from night_light.utils import query_geojson
from tests.conftest import BOSTON_TOWN_ID


def test_query_boston_adt(boston_traffic):
    """Test querying the Boston average annual daily traffic"""
    assert boston_traffic.shape[0] > 0
    assert boston_traffic.crs == "EPSG:4326"
    assert boston_traffic.geometry.name == "geometry"
    assert set(boston_traffic.geometry.geom_type.unique()) == {
        "MultiLineString",
        "LineString",
    }
    assert boston_traffic.columns.to_list() == [
        "geometry",
        "OBJECTID",
        "Route_ID",
        "From_Measure",
        "To_Measure",
        "Route_System",
        "Route_Number",
        "Route_Direction",
        "Facility",
        "Mile_Count",
        "F_Class",
        "Urban_Area",
        "Urban_Type",
        "F_F_Class",
        "Jurisdictn",
        "NHS",
        "Fd_Aid_Rd",
        "Control",
        "City",
        "County",
        "Hwy_Dist",
        "MPO",
        "SP_Station",
        "AADT",
        "VMT",
        "Length",
        "From_Date",
        "To_Date",
        "Shape__Length",
    ]
    assert boston_traffic["City"].unique().size == 1
    assert boston_traffic["City"].unique()[0] == BOSTON_TOWN_ID


def test_save_boston_geojson(boston_traffic):
    """Test saving the Boston average annual daily traffic to a GeoJSON file"""
    query_geojson.save_geojson(boston_traffic, "test_boston_crosswalk.geojson")
    geojson_filename = "test_boston_crosswalk.geojson"
    saved_gdf = query_geojson.gpd.read_file(geojson_filename)

    assert boston_traffic.crs == saved_gdf.crs
    assert set(boston_traffic.columns) == set(saved_gdf.columns)
    assert boston_traffic.index.equals(saved_gdf.index)
    assert boston_traffic.shape == saved_gdf.shape

    os.remove(geojson_filename)
    assert not os.path.exists(geojson_filename)
