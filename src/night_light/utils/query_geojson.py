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
        gdf = gpd.GeoDataFrame.from_features(response.json()["features"], crs="EPSG:4326")
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


def save_geodatabase_to_geojson(
    path_gdf: str, filename: str, params: dict = {}
) -> gpd.GeoDataFrame:
    """
    Given the path to a GeoDataFrame, filter it and save it as a GeoJSON file

    Args:
        path_gdf (str): The file path to the GeoDataFrame location
        filename (str): The file path where the GeoJSON will be saved
        params (dict): Dictionary representing parameters to filter geodataframe by

    Returns:
        gdf: A GeoDataFrame containing the geometries and properties from
        the fetched GeoJSON data
    """
    gdf = gpd.read_file(filename=path_gdf)
    for key, value in params.items():
        gdf_filtered = gdf[gdf[key] == value]
    gdf_filtered.to_file(filename, driver="GeoJSON")
    return gdf_filtered
