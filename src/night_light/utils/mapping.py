import os

import folium
from functools import partial

Tooltip = partial(
    folium.GeoJsonTooltip,
    localize=True,
    sticky=True,
    labels=True,
    style="""
            background-color: #F0EFEF; 
            border: 2px solid black; 
            border-radius: 3px; 
            box-shadow: 3px;
        """,
)

Choropleth = partial(
    folium.Choropleth,
    fill_color="YlOrRd",
    fill_opacity=0.7,
    line_opacity=0.2,
    line_weight=0.1,
)

LAYER_STYLE_DICT = {
    "fillColor": "cyan",
    "color": "black",
    "weight": 1,
    "fillOpacity": 0.5,
}

LAYER_HIGHLIGHT_STYLE_DICT = {
    "fillColor": "red",
    "color": "red",
    "weight": 3,
    "fillOpacity": 0.5,
}


def create_folium_map(
    layers: list[folium.map.Layer],
    center: list,
    zoom_start: int,
    map_filename: str,
):
    """
    Create a Folium map from a GeoDataFrame and save it to an HTML file.

    This function generates a Folium map centered at a specified location and zoom
    level, overlays the geometries from the provided GeoDataFrame, and saves the map as
    an HTML file.

    Args:
        layers (list[folium.map.Layer]): Layers containing geometries to be added to the
            map.
        center (list): A list containing the latitude and longitude for the map center
            [latitude, longitude].
        zoom_start (int): The initial zoom level for the map.
        map_filename (str): The file path where the HTML map will be saved.

    Returns:
        None
    """
    m = folium.Map(location=center, zoom_start=zoom_start)
    for layer in layers:
        layer.add_to(m)
    folium.LayerControl().add_to(m)
    m.save(map_filename)


def open_html_file(file_path: str | os.PathLike[str]):
    file_path = os.path.abspath(file_path)

    if os.name == "posix":
        os.system(
            f"open '{file_path}'"
            if "Darwin" in os.uname().sysname
            else f"xdg-open '{file_path}'"
        )
    elif os.name == "nt":
        os.system(f"start {file_path}")
    else:
        print("Unsupported operating system")
