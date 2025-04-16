import inspect
import os

import duckdb

import night_light.utils.util_duckdb as util_duckdb
import night_light.GIS_predictor.vehicle_direction as vehicle_direction
import night_light.GIS_predictor.crosswalk_center as crosswalk_center
import night_light.GIS_predictor.edge_classifier as edge_classifier
import night_light.GIS_predictor.distance as distance
import night_light.GIS_predictor.percieved_brightness as brightness
import night_light.GIS_predictor.contrast as contrast

# move to a until file?
def abs_path(relative_path: str) -> str:
    """
    Define an absolute path for file

    Args:
        relative_path: a string of a file name
    
    Returns:
        A string that is a full file path in the user's directory
    """
    caller_file = inspect.stack()[1].filename  # Get the caller's frame
    caller_dir = os.path.dirname(
        os.path.abspath(caller_file)
    )  # Get the directory of the caller's script
    return os.path.join(caller_dir, relative_path)


def initialize_db(con: duckdb.DuckDBPyConnection):
    """
    Create an inital .db file with crosswalks, streetlights, and street_segments datasets
    """
    datasets = [
        (abs_path("datasets/boston_crosswalks.geojson"), "crosswalks"),
        (abs_path("datasets/boston_streetlights.geojson"), "streetlights"),
        (abs_path("datasets/boston_street_segments.geojson"), "street_segments"),
    ]
    util_duckdb.load_multiple_datasets(con, datasets)


if __name__ == "__main__":
    # Initilize the .db file and connect to it
    con = util_duckdb.connect_to_duckdb(abs_path("boston_contrast.db"))
    initialize_db(con)

    # Simplify crosswalks and decompose edges
    edge_classifier.simplify_crosswalk_polygon_to_box(con)
    edge_classifier.decompose_crosswalk_edges(con)

    # Get centers and directions of crosswalks
    edge_classifier.classify_edges_by_intersection(con)
    crosswalk_center.find_crosswalk_centers(con)
    vehicle_direction.identify_vehicle_direction(con)

    # Get distance between crosswalks and streetlights
    distance.create_crosswalk_centers_lights(con)
    distance.find_streetlights_crosswalk_centers(con, 20)

    # Calculate contrast hueristic per streetlight centerpoint
    contrast.classify_lights_by_side(con)
    contrast.add_distances(con)
    contrast.calculate_contrast_heuristics(con, 0.01)

    # Get brightness hueristic per streetlight centerpoint
    brightness.calculate_percieved_brightness(con)

    # Save the results to parquet
    output_dir = abs_path("output")
    os.makedirs(output_dir, exist_ok=True)

    util_duckdb.save_table_to_parquet(
        con,
        "crosswalk_centers_contrast",
        os.path.join(output_dir, "crosswalk_centers_contrast.parquet"),
    )
    util_duckdb.save_table_to_csv(
        con,
        "classified_streetlights",
        os.path.join(output_dir, "classified_streetlights.csv"),
    )
    util_duckdb.save_table_to_parquet(
        con,
        "crosswalk_centers_lights",
        os.path.join(output_dir, "crosswalk_centers_lights.parquet"),
    )
    util_duckdb.save_table_to_parquet(
        con,
        "streetlights",
        os.path.join(output_dir, "streetlights.parquet"),
    )
