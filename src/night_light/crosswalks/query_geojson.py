import requests
import geopandas as gpd


def fetch_geojson_data(url: str, params: dict) -> gpd.GeoDataFrame:
    """Fetch GeoJSON data from the given URL with specified parameters."""
    response = requests.get(url, params=params)
    response.raise_for_status()
    try:
        gdf = gpd.GeoDataFrame.from_features(
            response.json()["features"], crs="EPSG:4326"
        )
        return gdf
    except KeyError:
        raise ValueError("Invalid GeoJSON data")


def save_geojson(gdf: gpd.GeoDataFrame, filename: str):
    """Save GeoDataFrame to a GeoJSON file."""
    gdf.to_file(filename, driver="GeoJSON")
