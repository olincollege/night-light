import folium
import geopandas as gpd


def create_folium_map(
    gdf: gpd.GeoDataFrame, center: list, zoom_start: int, map_filename: str
):
    """Create a Folium map with the given GeoDataFrame and save it to an HTML file."""
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
