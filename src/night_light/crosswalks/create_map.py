import folium
import geopandas as gpd


def create_folium_map(
    gdf: gpd.GeoDataFrame, center: list, zoom_start: int, map_filename: str
):
    """
    Create a Folium map from a GeoDataFrame and save it to an HTML file.

    This function generates a Folium map centered at a specified location and zoom
    level, overlays the geometries from the provided GeoDataFrame, and saves the map as
    an HTML file.

    Args:
        gdf (gpd.GeoDataFrame): A GeoDataFrame containing geometries to be added to the
        map.
        center (list): A list containing the latitude and longitude for the map center
        [latitude, longitude].
        zoom_start (int): The initial zoom level for the map.
        map_filename (str): The file path where the HTML map will be saved.

    Returns:
        None
    """
    m = folium.Map(location=center, zoom_start=zoom_start)
    folium.GeoJson(
        gdf,
        name="Crosswalk Polygons",
        style_function=lambda x: {
            "fillColor": "cyan",
            "color": "black",
            "weight": 1,
            "fillOpacity": 0.5,
        },
    ).add_to(m)
    folium.LayerControl().add_to(m)
    m.save(map_filename)
