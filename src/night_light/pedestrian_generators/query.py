import requests
import geojson

# Define the Overpass API endpoint
overpass_url = "http://overpass-api.de/api/interpreter"

# Define the Overpass query for shopping places in Boston
overpass_query = """
[out:json];
area["name"="Boston"]["boundary"="administrative"];
(
  node["shop"](area);
  node["amenity"="market"](area);
  node["amenity"="supermarket"](area);
  node["amenity"="convenience"](area);
  node["amenity"="department_store"](area);
  node["amenity"="clothes"](area);
  node["amenity"="shoes"](area);
);
out body;
>;
out skel qt;
"""

# Make the API request
response = requests.post(overpass_url, data=overpass_query)

# Check if the request was successful
if response.status_code == 200:
    data = response.json()
    
    # Create a GeoJSON feature collection
    features = []
    
    for element in data['elements']:
        if 'lat' in element and 'lon' in element:
            point = geojson.Point((element['lon'], element['lat']))
            properties = {key: element[key] for key in element if key not in ['lat', 'lon']}
            feature = geojson.Feature(geometry=point, properties=properties)
            features.append(feature)
    
    feature_collection = geojson.FeatureCollection(features)
    
    # Save the GeoJSON data to a file
    with open('src/night_light/pedestrian_generators/geojsons_dump/shopping_places_boston.geojson', 'w') as f:
        geojson.dump(feature_collection, f)
    
    print("GeoJSON file created: shopping_places_boston.geojson")
else:
    print("Error fetching data:", response.status_code)
