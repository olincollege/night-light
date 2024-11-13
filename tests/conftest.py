from night_light.utils import query_geojson

import pytest
import asyncio
import aiohttp
import geopandas as gpd

MA_CROSSWALK_URL = "https://gis.massdot.state.ma.us/arcgis/rest/services/Assets/Crosswalk_Poly/FeatureServer/0/query"
MA_TRAFFIC_URL = "https://gis.massdot.state.ma.us/arcgis/rest/services/Roads/VMT/FeatureServer/10/query"
MA_MUNICIPALITIES_URL = "https://arcgisserver.digital.mass.gov/arcgisserver/rest/services/AGOL/Towns_survey_polym/FeatureServer/0/query"
BOSTON_STREETLIGHTS_URL = "https://services.evari.io/evari/rest/services/Boston/Boston_Read_Only/MapServer/0/query"

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

STREETLIGHTS_BOSTON_PARAMS = {
    "where": "1=1",
    "outFields": "OBJECTID, Final_Fixture_Type, Final_Wattage, Final_Bulb_Type, Final_Luminaires_Per_Pole",
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


@pytest.fixture
def boston_streetlights():
    async def fetch_data(session, url, params):
        async with session.get(url, params=params) as response:
            response.raise_for_status()
            return await response.json()

    async def fetch_all_data():
        data = []
        batch_size = 2000
        max_concurrent_requests = 50

        async with aiohttp.ClientSession() as session:
            while True:
                tasks = [
                    fetch_data(
                        session,
                        BOSTON_STREETLIGHTS_URL,
                        {
                            **STREETLIGHTS_BOSTON_PARAMS,
                            "resultOffset": str((i * batch_size)),
                        },
                    )
                    for i in range(max_concurrent_requests)
                ]

                responses = await asyncio.gather(*tasks)

                for result in responses:
                    features = result.get("features", [])
                    data.extend(features)
                    feature_count = len(features)
                    if (
                        not result.get("exceededTransferLimit")
                        or feature_count < batch_size
                    ):
                        return data

    data = asyncio.run(fetch_all_data())
    gdf = gpd.GeoDataFrame.from_features(data, crs="EPSG:4326")
    return gdf
