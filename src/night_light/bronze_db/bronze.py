import util

# Eventually we want to automate the process of generating these geojsons into this file, so they are generated
# at the same time that the bronze database is created and then automatically deleted.


def generate_bronze_db():
    db_path = "bronze.db"

    # Run the scripts in tests to generate the GeoJSON files
    datasets = [
        ("tests/test_boston_crosswalk.geojson", "crosswalks"),
        ("tests/test_boston_streetlights.geojson", "streetlights"),
        ("tests/test_all_population_density.geojson", "population_density"),
        ("tests/test_boston_traffic.geojson", "traffic"),
        ("tests/test_boston_vision_zero.geojson", "accidents"),
        ("tests/test_ma_median_household_income.geojson", "median_income"),
        ("tests/test_boston_traffic_lights.geojson", "traffic_lights"),
        ("tests/test_pedestrian.geojson", "pedestrian_generators"),
        ("tests/test_road_speeds.geojson", "speed_limits"),
    ]

    conn = util.connect_to_duckdb(db_path)
    util.load_multiple_datasets(conn, datasets)
    gdf = util.query_table_to_gdf(conn, "crosswalks")
    return gdf


if __name__ == "__main__":
    print(generate_bronze_db())
