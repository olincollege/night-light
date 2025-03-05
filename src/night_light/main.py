import inspect
import os

import duckdb

import night_light.bronze_db.util as util
import night_light.GIS_predictor.vehicle_direction as vehicle_direction
import night_light.GIS_predictor.crosswalk_center as crosswalk_center
import night_light.GIS_predictor.edge_classifier.edge_classifier as edge_classifier
import night_light.GIS_predictor.distance as distance
import night_light.GIS_predictor.contrast_table as contrast_table
import night_light.GIS_predictor.percieved_brightness as brightness
import night_light.GIS_predictor.compare as compare
import night_light.GIS_predictor.contrast as contrast


def abs_path(relative_path):
    caller_file = inspect.stack()[1].filename  # Get the caller's frame
    caller_dir = os.path.dirname(
        os.path.abspath(caller_file)
    )  # Get the directory of the caller's script
    return os.path.join(caller_dir, relative_path)


def initialize_db(
    con: duckdb.DuckDBPyConnection,
):
    datasets = [
        (abs_path("datasets/boston_crosswalks.geojson"), "crosswalks"),
        (abs_path("datasets/boston_streetlights.geojson"), "streetlights"),
        (abs_path("datasets/boston_street_segments.geojson"), "street_segments"),
    ]
    util.load_multiple_datasets(con, datasets)


if __name__ == "__main__":
    con = util.connect_to_duckdb(abs_path("boston_contrast.db"))
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

    contrast.classify_lights_by_side(con)
    contrast.add_distances(con)
    contrast.calculate_contrast_heuristics(con, 0.02)

    # Get brightness per crosswalk
    brightness.calculate_percieved_brightness(con)

    # Make comparison table
    file_path = abs_path("../../SVData2-11.csv")
    compare.create_compare_table(con, file_path)

    # Save the results to parquet
    output_dir = abs_path("output")
    os.makedirs(output_dir, exist_ok=True)

    util.save_table_to_parquet(
        con,
        "crosswalk_centers_contrast",
        os.path.join(output_dir, "crosswalk_centers_contrast.parquet"),
    )
    utils.save_table_to_csv(
        "classified_streetlights",
        os.path.join(output_dir, "classified_streetlights.csv"),
    )
    util.save_table_to_parquet(
        con,
        "crosswalk_centers_lights",
        os.path.join(output_dir, "crosswalk_centers_lights.parquet"),
    )
    util.save_table_to_parquet(
        con,
        "streetlights",
        os.path.join(output_dir, "streetlights.parquet"),
    )
