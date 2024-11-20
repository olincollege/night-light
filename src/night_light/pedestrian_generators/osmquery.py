import requests
import geojson


def osm_query(overpass_query: str, file_path: str):
    """
    Make a GeoJSON file containing all queried features from Open Street Map.

    args:
        overpass_query: string formatted as OSM query. See docs for more.
        file_path: string of the full file path where the GeoJSON should be saved
    """
    # Make the API request
    overpass_url = "http://overpass-api.de/api/interpreter"
    response = requests.post(overpass_url, data=overpass_query)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()

        # Collect features
        features = []

        for element in data['elements']:
            if 'lat' in element and 'lon' in element:
                point = geojson.Point((element['lon'], element['lat']))
                properties = {key: element[key] for key in element if key not in ['lat', 'lon']}
                feature = geojson.Feature(geometry=point, properties=properties)
                features.append(feature)

        feature_collection = geojson.FeatureCollection(features)

        # Save to the provided file path
        with open(file_path, 'w') as f:
            geojson.dump(feature_collection, f)

        print(f"GeoJSON file created: {file_path}")
    else:
        print("Error fetching data:", response.status_code)


def get_all_pedestrian_geojson(file_path: str):
    """
    Queries all pedestrian generators and saves them in geojson.

    args:
        file_path: string that is location and title of the file.
    """
    query = """
    [out:json];
    area["name"="Boston"]["boundary"="administrative"];
    (
        node["tourism"](area);
        node["tourism"="museum"](area);
        node["tourism"="art_gallery"](area);
        node["tourism"="attraction"](area);
        node["tourism"="viewpoint"](area);
        node["tourism"="zoo"](area);
        node["tourism"="theme_park"](area);
        node["historic"="memorial"](area);
        node["historic"="monument"](area);
        node["historic"="site"](area);

        node["amenity"="school"](area);
        node["amenity"="university"](area);
        node["amenity"="college"](area);
        node["amenity"="language_school"](area);

        node["amenity"="hospital"](area);
        node["amenity"="clinic"](area);
        node["amenity"="nursing_home"](area);
        node["amenity"="doctors"](area);
        node["amenity"="dentist"](area);
        node["amenity"="pharmacy"](area);
        node["service"="disability"](area);
        node["amenity"="social_facility"](area);
        node["amenity"="healthcare"](area);

        node["leisure"="park"](area);
        node["leisure"="nature_reserve"](area);
        node["leisure"="garden"](area);
        node["leisure"="recreation_ground"](area);
        node["amenity"="playground"](area);
        node["landuse"="grass"](area);
        node["landuse"="recreation_ground"](area);

        node["shop"](area);
        node["amenity"="market"](area);
        node["amenity"="supermarket"](area);
        node["amenity"="convenience"](area);
        node["amenity"="department_store"](area);
        node["amenity"="clothes"](area);
        node["amenity"="shoes"](area);

        node["amenity"="bar"](area);
        node["amenity"="pub"](area);
        node["amenity"="nightclub"](area);
        node["amenity"="casino"](area);
        node["amenity"="cocktail_bar"](area);
        node["amenity"="beer_garden"](area);
        node["leisure"="nightclub"](area);
        node["leisure"="dance_centre"](area);
        node["leisure"="drinking_water"](area);

        node["amenity"="restaurant"](area);
        node["amenity"="fast_food"](area);
        node["amenity"="food_court"](area);
        node["amenity"="ice_cream"](area);
        node["amenity"="pizza"](area);
    );
    out body;
    >;
    out skel qt;
    """
    osm_query(query, file_path)


def get_tourist_geojson(file_path: str):
    query = """
    [out:json];
    area["name"="Boston"]["boundary"="administrative"];
    (
        node["tourism"](area);
        node["tourism"="museum"](area);
        node["tourism"="art_gallery"](area);
        node["tourism"="attraction"](area);
        node["tourism"="viewpoint"](area);
        node["tourism"="zoo"](area);
        node["tourism"="theme_park"](area);
        node["historic"="memorial"](area);
        node["historic"="monument"](area);
        node["historic"="site"](area);
    );
    out body;
    >;
    out skel qt;
    """
    osm_query(query, file_path)


def get_schooling_geojson(file_path: str):
    query = """
    [out:json];
    area["name"="Boston"]["boundary"="administrative"];
    (
        node["amenity"="school"](area);
        node["amenity"="university"](area);
        node["amenity"="college"](area);
        node["amenity"="language_school"](area);
    );
    out body;
    >;
    out skel qt;
    """
    osm_query(query, file_path)


def get_health_geojson(file_path: str):
    query = """
    [out:json];
    area["name"="Boston"]["boundary"="administrative"];
    (
        node["amenity"="hospital"](area);
        node["amenity"="clinic"](area);
        node["amenity"="nursing_home"](area);
        node["amenity"="doctors"](area);
        node["amenity"="dentist"](area);
        node["amenity"="pharmacy"](area);
        node["service"="disability"](area);
        node["amenity"="social_facility"](area);
        node["amenity"="healthcare"](area);
    );
    out body;
    >;
    out skel qt;
    """
    osm_query(query, file_path)


def get_parks_open_space_geojson(file_path: str):
    query = """
    [out:json];
    area["name"="Boston"]["boundary"="administrative"];
    (
        node["leisure"="park"](area);
        node["leisure"="nature_reserve"](area);
        node["leisure"="garden"](area);
        node["leisure"="recreation_ground"](area);
        node["amenity"="playground"](area);
        node["landuse"="grass"](area);
        node["landuse"="recreation_ground"](area);
    );
    out body;
    >;
    out skel qt;
    """
    osm_query(query, file_path)


def get_shopping(file_path: str):
    query = """
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
    osm_query(query, file_path)


def get_night_life(file_path: str):
    query = """[out:json];
    area["name"="Boston"]["boundary"="administrative"];
    (
        node["amenity"="bar"](area);
        node["amenity"="pub"](area);
        node["amenity"="nightclub"](area);
        node["amenity"="casino"](area);
        node["amenity"="cocktail_bar"](area);
        node["amenity"="beer_garden"](area);
        node["leisure"="nightclub"](area);
        node["leisure"="dance_centre"](area);
        node["leisure"="drinking_water"](area);
    );
    out body;
    >;
    out skel qt;
    """
    osm_query(query, file_path)


def get_resturants(file_path: str):
    query = """
    [out:json];
    area["name"="Boston"]["boundary"="administrative"];
    (
        node["amenity"="restaurant"](area);
        node["amenity"="fast_food"](area);
        node["amenity"="food_court"](area);
        node["amenity"="ice_cream"](area);
        node["amenity"="pizza"](area);
    );
    out body;
    >;
    out skel qt;
    """
    osm_query(query, file_path)
