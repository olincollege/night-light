import geopandas as gpd
import requests
import pandas as pd

BOSTON_VISION_ZERO_URL = "https://data.boston.gov/api/3/action/datastore_search_sql"
BOSTON_VISION_ZERO_PED_CRASHES = '"e4bfe397-6bfc-49c5-9367-c879fac7401d"'
BOSTON_VISION_ZERO_PED_FATALITIES = '"92f18923-d4ec-4c17-9405-4e0da63e1d6c"'


def _boston_vision_zero_ped_accidents(resource_id: str) -> gpd.GeoDataFrame:
    params = {"sql": "SELECT * from " + resource_id + " WHERE mode_type	= 'ped'"}
    response = requests.get(BOSTON_VISION_ZERO_URL, params=params)
    response.raise_for_status()
    data = response.json()["result"]["records"]
    gdf = gpd.GeoDataFrame.from_records(data)
    gdf.drop(["_full_text"], axis=1, inplace=True)
    gdf.set_geometry(
        gpd.points_from_xy(gdf["long"], gdf["lat"]), inplace=True, crs="EPSG:4326"
    )
    return gdf


def boston_vision_zero_ped_accidents():
    gdf_crashes = _boston_vision_zero_ped_accidents(BOSTON_VISION_ZERO_PED_CRASHES)
    gdf_fatalities = _boston_vision_zero_ped_accidents(
        BOSTON_VISION_ZERO_PED_FATALITIES
    )
    gdf_crashes["is_fatal"] = False
    gdf_crashes.rename(columns={"dispatch_ts": "date_time"}, inplace=True)
    gdf_fatalities["is_fatal"] = True
    return pd.concat([gdf_crashes, gdf_fatalities], ignore_index=True)
