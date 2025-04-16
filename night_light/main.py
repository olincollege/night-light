import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from analyzer import *
from util_duckdb import *


def initialize_db(con: duckdb.DuckDBPyConnection):
    """
    Create an initial .db file with crosswalks, streetlights, and street_segments datasets
    """
    datasets = [
        (abs_path("../datasets/boston_crosswalks.geojson"), "crosswalks"),
        (abs_path("../datasets/boston_streetlights.geojson"), "streetlights"),
        (abs_path("../datasets/boston_street_segments.geojson"), "street_segments"),
    ]
    load_multiple_datasets(con, datasets)


def main():
    # Initialize the .db file and connect to it
    con = connect_to_duckdb(abs_path("../boston_contrast.db"))
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

    # Calculate contrast heuristic per streetlight centerpoint
    classify_lights_by_side(con)
    add_streetlight_distances(con)
    calculate_contrast_heuristics(con, 0.01)

    # Get brightness heuristic per streetlight centerpoint
    calculate_percieved_brightness(con)

    # Save the results to parquet
    output_dir = abs_path("../output")
    os.makedirs(output_dir, exist_ok=True)

    save_table_to_parquet(
        con,
        "crosswalk_centers_contrast",
        os.path.join(output_dir, "crosswalk_centers_contrast.parquet"),
    )
    save_table_to_csv(
        con,
        "classified_streetlights",
        os.path.join(output_dir, "classified_streetlights.csv"),
    )
    save_table_to_parquet(
        con,
        "crosswalk_centers_lights",
        os.path.join(output_dir, "crosswalk_centers_lights.parquet"),
    )
    save_table_to_parquet(
        con,
        "streetlights",
        os.path.join(output_dir, "streetlights.parquet"),
    )


if __name__ == "__main__":
    main()
