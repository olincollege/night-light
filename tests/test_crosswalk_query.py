import os
from night_light.utils import query_geojson


def test_query_boston_crosswalk(boston_crosswalk):
    """Test querying the Boston crosswalk"""
    assert boston_crosswalk.shape[0] > 0
    assert boston_crosswalk.crs == "EPSG:4326"
    assert boston_crosswalk.geometry.name == "geometry"
    assert boston_crosswalk.geometry.geom_type.unique()[0] == "Polygon"
    assert boston_crosswalk.columns.to_list() == [
        "geometry",
        "OBJECTID",
        "Conf_Score",
        "tilename",
        "layer",
        "path",
        "TOWN",
        "Degradatio",
        "MPOName",
        "Class_Loc",
        "DistrictName",
        "DistrictNumber",
        "RPA_NAME",
        "CrossType",
        "Shape__Area",
        "Shape__Length",
    ]
    assert boston_crosswalk["TOWN"].unique().size == 1
    assert boston_crosswalk["TOWN"].unique()[0] == "BOSTON"


def test_save_boston_geojson(boston_crosswalk):
    """Test saving the Boston crosswalk to a GeoJSON file"""
    query_geojson.save_geojson(boston_crosswalk, "test_boston_crosswalk.geojson")
    geojson_filename = "test_boston_crosswalk.geojson"
    saved_gdf = query_geojson.gpd.read_file(geojson_filename)

    assert boston_crosswalk.crs == saved_gdf.crs
    assert set(boston_crosswalk.columns) == set(saved_gdf.columns)
    assert boston_crosswalk.index.equals(saved_gdf.index)
    assert boston_crosswalk.shape == saved_gdf.shape

    os.remove(geojson_filename)
    assert not os.path.exists(geojson_filename)
