import requests
import geopandas as gpd
import folium

# Define the ArcGIS REST API endpoint and parameters for querying data
url = "https://gis.massdot.state.ma.us/arcgis/rest/services/Assets/Crosswalk_Poly/FeatureServer/0/query"

# Define parameters for querying only Boston
params = {
    "where": "TOWN='Boston'",  # Filter for town of Boston
    "outFields": "*",  # Select all fields
    "outSR": "4326",  # Set output spatial reference to WGS84
    "f": "geojson",  # Return data in GeoJSON format
}

# Send the GET request to the API
response = requests.get(url, params=params)

# Check if the request was successful
if response.status_code == 200:
    # Load the response JSON as a GeoDataFrame
    gdf = gpd.GeoDataFrame.from_features(response.json()["features"])
    # Set CRS to EPSG:4326 explicitly
    gdf.set_crs("EPSG:4326", inplace=True)
    print("Data successfully retrieved, loaded, and CRS set to EPSG:4326")
else:
    print("Error fetching data:", response.status_code)
    response.raise_for_status()

# Initialize a Folium map centered on Boston
boston_center = [42.3601, -71.0589]  # Latitude and longitude for Boston
m = folium.Map(location=boston_center, zoom_start=12)

# Add the polygon data to the map
# Convert GeoDataFrame to GeoJSON and add to the folium map
folium.GeoJson(
    gdf,
    name="Boston Crosswalk Polygons",
    style_function=lambda x: {
        "fillColor": "cyan",
        "color": "black",
        "weight": 1,
        "fillOpacity": 0.5,
    },
).add_to(m)

# Add a layer control for toggling
folium.LayerControl().add_to(m)

# Save and display the map
m.save("boston_crosswalks_map.html")
m
