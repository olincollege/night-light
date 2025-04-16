import inspect
import os

import duckdb

from night_light.analyzer import (identify_vehicle_direction,
                                  simplify_crosswalk_polygon_to_box,
                                  decompose_crosswalk_edges,
                                  classify_edges_by_intersection,
                                  find_crosswalk_centers,
                                  create_crosswalk_centers_lights,
                                  find_streetlights_crosswalk_centers,
                                  classify_lights_by_side, add_streetlight_distances,
                                  calculate_contrast_heuristics,
                                  calculate_percieved_brightness)
from night_light.utils import util_duckdb


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
    simplify_crosswalk_polygon_to_box(con)
    decompose_crosswalk_edges(con)

    # Get centers and directions of crosswalks
    classify_edges_by_intersection(con)
    find_crosswalk_centers(con)
    identify_vehicle_direction(con)

    # Get distance between crosswalks and streetlights
    create_crosswalk_centers_lights(con)
    find_streetlights_crosswalk_centers(con, 20)

    # Calculate contrast hueristic per streetlight centerpoint
    classify_lights_by_side(con)
    add_streetlight_distances(con)
    calculate_contrast_heuristics(con, 0.01)

    # Get brightness hueristic per streetlight centerpoint
    calculate_percieved_brightness(con)

    # Save the results to parquet
    output_dir = abs_path("output")
    os.makedirs(output_dir, exist_ok=True)

    util_duckdb.save_table_to_parquet(con, "crosswalk_centers_contrast",
        os.path.join(output_dir, "crosswalk_centers_contrast.parquet"), )
    util_duckdb.save_table_to_csv(con, "classified_streetlights",
        os.path.join(output_dir, "classified_streetlights.csv"), )
    util_duckdb.save_table_to_parquet(con, "crosswalk_centers_lights",
        os.path.join(output_dir, "crosswalk_centers_lights.parquet"), )
    util_duckdb.save_table_to_parquet(con, "streetlights",
        os.path.join(output_dir, "streetlights.parquet"), )
