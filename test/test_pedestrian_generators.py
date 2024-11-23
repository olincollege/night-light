import os
import geojson
from night_light.pedestrian_generators.osmquery import osm_query 

def test_osm_query_success():
    """Test querying OpenStreetMap for pedestrian-related features and saving to a GeoJSON file."""
    file_path = "test_pedestrian.geojson"
    overpass_query = """
    [out:json];
    area["name"="Boston"]["boundary"="administrative"];
    (
        node["tourism"](area);
        node["tourism"="museum"](area);
        node["tourism"="art_gallery"](area);
        node["tourism"="attraction"](area);
    );
    out body;
    >;
    out skel qt;
    """

    # Call the osm_query function
    osm_query(overpass_query, file_path)

    # Check if the GeoJSON file was created
    assert os.path.exists(file_path), f"GeoJSON file {file_path} was not created."

    # Load the saved GeoJSON file
    with open(file_path, 'r') as f:
        data = geojson.load(f)

    # Verify the structure of the GeoJSON
    assert isinstance(data, geojson.FeatureCollection), "GeoJSON is not a FeatureCollection"
    assert len(data['features']) > 0, "GeoJSON does not contain any features"

    # Check the first feature's structure (basic example, can be adjusted as needed)
    first_feature = data['features'][0]
    assert 'geometry' in first_feature, "First feature does not contain geometry"
    assert 'properties' in first_feature, "First feature does not contain properties"

    # Ensure the file contains the expected geometry type (Point for OSM node queries)
    assert first_feature['geometry']['type'] == 'Point', "Geometry type is not 'Point'"

    # Clean up
    os.remove(file_path)
    assert not os.path.exists(file_path), f"GeoJSON file {file_path} was not deleted after test"

