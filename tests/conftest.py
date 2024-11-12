import pytest
from night_light.utils import query_geojson

MA_CROSSWALK_URL = "https://gis.massdot.state.ma.us/arcgis/rest/services/Assets/Crosswalk_Poly/FeatureServer/0/query"
MA_TRAFFIC_URL = "https://gis.massdot.state.ma.us/arcgis/rest/services/Roads/VMT/FeatureServer/10/query"
MA_MUNICIPALITIES_URL = "https://arcgisserver.digital.mass.gov/arcgisserver/rest/services/AGOL/Towns_survey_polym/FeatureServer/0/query"

MUNICIPALITIES_MA_PARAMS = {
    "where": "1=1",
    "outFields": "TOWN, TOWN_ID, FIPS_STCO",
    "outSR": "4326",
    "f": "geojson",
}

MA_MUNICIPALITIES = query_geojson.fetch_geojson_data(
    url=MA_MUNICIPALITIES_URL, params=MUNICIPALITIES_MA_PARAMS
)
BOSTON_TOWN_ID = MA_MUNICIPALITIES[MA_MUNICIPALITIES["TOWN"] == "BOSTON"][
    "TOWN_ID"
].values[0]

CROSSWALK_BOSTON_PARAMS = {
    "where": "TOWN='BOSTON'",
    "outFields": "*",
    "outSR": "4326",
    "f": "geojson",
}

TRAFFIC_BOSTON_PARAMS = {
    "where": f"CITY={BOSTON_TOWN_ID}",
    "outFields": "*",
    "outSR": "4326",
    "f": "geojson",
}


BOSTON_CENTER_COORD = [42.3601, -71.0589]


@pytest.fixture
def boston_crosswalk():
    return query_geojson.fetch_geojson_data(
        url=MA_CROSSWALK_URL, params=CROSSWALK_BOSTON_PARAMS
    )


@pytest.fixture
def boston_traffic():
    return query_geojson.fetch_geojson_data(
        url=MA_TRAFFIC_URL, params=TRAFFIC_BOSTON_PARAMS
    )
