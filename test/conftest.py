import pytest
from night_light.crosswalks import query_geojson

MA_CROSSWALK_URL = "https://gis.massdot.state.ma.us/arcgis/rest/services/Assets/Crosswalk_Poly/FeatureServer/0/query"
BOSTON_PARAMS = {
    "where": "TOWN='BOSTON'",
    "outFields": "*",
    "outSR": "4326",
    "f": "geojson",
}
BOSTON_CENTER_COORD = [42.3601, -71.0589]


@pytest.fixture
def boston_crosswalk():
    return query_geojson.fetch_geojson_data(url=MA_CROSSWALK_URL, params=BOSTON_PARAMS)
