import night_light.bronze_db.util as util
import night_light.silver_db.crosswalk as crosswalk
import night_light.GIS_predictor.vehicle_direction as vehicle_direction
import night_light.GIS_predictor.crosswalk_center as crosswalk_center
import night_light.GIS_predictor.edge_classifier.edge_classifier as edge_classifier
import night_light.GIS_predictor.distance as distance
import night_light.GIS_predictor.contrast_table as contrast_table

def generate_bronze_db_mini():
    db_path = "bronze.db"

    # Run the scripts in tests to generate the GeoJSON files
    datasets = [
        ("tests/test_boston_crosswalk.geojson", "crosswalks"),
        ("tests/test_boston_streetlights.geojson", "streetlights"),
        ("tests/test_boston_traffic_lights.geojson", "traffic_lights"),
    ]

    conn = util.connect_to_duckdb(db_path)
    util.load_multiple_datasets(conn, datasets)

if __name__ == "__main__":
    # Get edges of crosswalks
    conn = util.connect_to_duckdb("src/night_light/GIS_predictor/edge_classifier/edge_classifier.db")
    edge_classifier.initialize_edge_classifier_db(
        conn,
        street_segments_geojson_path="src/night_light/road_characteristics/boston_street_segments.geojson",
        crosswalks_geojson_path="tests/test_boston_crosswalk.geojson",
    )
    edge_classifier.simplify_crosswalk_polygon_to_box(conn)
    edge_classifier.decompose_crosswalk_edges(conn)

    # Get centers and directions of crosswalks
    edge_classifier.classify_edges_by_intersection(conn)
    crosswalk_center.find_crosswalk_centers(conn)
    vehicle_direction.identify_vehicle_direction(conn)

    # # Add streetlights to database
    distance.add_streetlights_to_edge_classifier(conn)
    distance.create_crosswalk_centers_lights(conn)
    distance.find_streetlights_crosswalk_centers("src/night_light/GIS_predictor/edge_classifier/edge_classifier.db", 20)
    contrast_table.lights_geom(conn)

    # Get contrast per crosswalk
    contrast_table.classify_lights_table(conn)
    contrast_table.contrast_table(conn)


