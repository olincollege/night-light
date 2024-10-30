import requests
import geopandas as gpd
import matplotlib.pyplot as plt

# Define the ArcGIS REST API endpoint and parameters for querying data
url = "https://gis.massdot.state.ma.us/arcgis/rest/services/Assets/Crosswalk_Poly/FeatureServer/0/query"

# Define parameters for querying all features and requesting GeoJSON format
params = {
    "where": "TOWN='BOSTON'",  # Query all records
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
    print("Data successfully retrieved and loaded into a GeoDataFrame")
else:
    print("Error fetching data:", response.status_code)
    response.raise_for_status()

# Plot the polygon data for Boston
gdf.plot(edgecolor="black", facecolor="cyan")
plt.title("Boston Crosswalk Polygons from MassDOT")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.show()
