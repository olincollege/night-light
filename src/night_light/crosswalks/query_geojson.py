import requests
import geopandas as gpd


def fetch_geojson_data(url: str, params: dict) -> gpd.GeoDataFrame:
    """
    Fetch GeoJSON data from a specified URL with given parameters.

    This function sends a GET request to the provided URL with the specified query
    parameters, retrieves the GeoJSON data, and converts it into a GeoDataFrame with an
    EPSG:4326 CRS.

    Args:
        url (str): The URL to request the GeoJSON data from.
        params (dict): A dictionary of query parameters to include in the request.

    Returns:
        gpd.GeoDataFrame: A GeoDataFrame containing the geometries and properties from
        the fetched GeoJSON data.

    Raises:
        requests.HTTPError: If the HTTP request fails.
        ValueError: If the retrieved data does not contain valid GeoJSON features.
    """
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
    """
    Save a GeoDataFrame to a GeoJSON file.

    Args:
        gdf (gpd.GeoDataFrame): The GeoDataFrame to be saved as GeoJSON.
        filename (str): The file path where the GeoJSON will be saved.

    Returns:
        None
    """
    gdf.to_file(filename, driver="GeoJSON")
