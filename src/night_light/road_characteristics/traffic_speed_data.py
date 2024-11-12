import geojson
import geopandas as gpd
from night_light.crosswalks import query_geojson
import requests

"""
Data Source:
https://gis.massdot.state.ma.us/voyager/navigo/show?id=3f87999a6ac248debd488461efc889d0&disp=default
"""

import os


def geodatabase_to_geojson(file_location, geojson_title):
    """
    Read geodatabase into geojson
    """
    gdf = gpd.read_file(filename=file_location)
    gdf.to_file(geojson_title, driver="GeoJSON")


print(os.getcwd())

road_inventory_data = "src/night_light/road_characteristics/RoadInventory2023.gdb"
geojson_name = "src/night_light/road_characteristics/road_inventory.geojson"
geodatabase_to_geojson(road_inventory_data, geojson_name)


# with open("src/night_light/road_characteristics/road_inventory.geojson") as f:
#     gj = geojson.load(f)
#     features = gj["features"][0]
#     print(features["properties"]["Speed_Lim"])
#     # print(gj["features"][0])

# features = gj["features"][0]
# print(features["properties"]["Speed_Lim"])

# response = requests.get(
#     "https://gis.massdot.state.ma.us/arcgis/rest/services/Roads/VMT/FeatureServer/10/query?where=1%3D1&outFields=*&outSR=4326&f=json"
# )
# if (response.status_code) != 200:
#     print("ERROR GETTING DATA")

# traffic_data = response.json()

# print(traffic_data.keys())

# from arcgis.gis import GIS, ItemProperties, ItemTypeEnum

# portal = GIS(username="ruchadave")

# file_database = "road_characteristics/RoadInventory2023.gdb"

# gdf = gpd.read_file(filename=file_database)
# gdf.to_file("output_file.geojson", driver="GeoJSON")
