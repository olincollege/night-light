import duckdb
import night_light.bronze_db.util as util


def initialize_edge_classifier_db(
    con: duckdb.DuckDBPyConnection,
    crosswalks_geojson_path: str,
    street_segments_geojson_path: str,
) -> duckdb.DuckDBPyConnection:
    """
    Initialize duckdb database tables for edge classifier.

    The db should include Boston crosswalks and street segments tables.
    """
    datasets = [
        (crosswalks_geojson_path, "crosswalks"),
        (street_segments_geojson_path, "street_segments"),
    ]

    util.load_multiple_datasets(con, datasets)

    return con


def simplify_crosswalk_polygon_to_box(con: duckdb.DuckDBPyConnection):
    gdf = util.query_table_to_gdf(con, "crosswalks", "SELECT * FROM crosswalks")
    # Get oriented bounding rectangles
    gdf["oriented_env"] = gdf["geometry"].apply(
        lambda geom: geom.minimum_rotated_rectangle
    )
    # Write the result back to DuckDB
    gdf["geometry"] = gdf["oriented_env"].to_wkt()
    con.register("temp_gdf", gdf[["OBJECTID", "geometry"]])
    con.execute(
        """
            UPDATE crosswalks
            SET geometry = (
                SELECT t.geometry
                FROM temp_gdf t
                WHERE t.OBJECTID = crosswalks.OBJECTID
            )
        """
    )


def decompose_crosswalk_edges(con: duckdb.DuckDBPyConnection):
    """Decompose crosswalks polygons into separate edges."""
    con.execute(
        """
        -- Create or replace the table of crosswalk edges (line segments)
        CREATE OR REPLACE TABLE crosswalk_segments AS
        WITH boundaries AS (
            SELECT
                cw.OBJECTID AS crosswalk_id,
                (UNNEST(ST_Dump(ST_Boundary(ST_GeomFromText(cw.geometry)))).geom) AS boundary_geom
            FROM crosswalks cw
        ),
        segments AS (
            SELECT
                crosswalk_id,
                g.i AS edge_id,
                ST_AsText(ST_MakeLine(
                    ST_PointN(boundary_geom, CAST(g.i AS INT)),
                    ST_PointN(boundary_geom, CAST(g.i + 1 AS INT))
                )) AS segment_geom
            FROM boundaries
            -- Generate a series 1..(npoints-1), label it g(i)
            CROSS JOIN generate_series(1, ST_NPoints(boundary_geom) - 1) AS g(i)
        )
        SELECT
            crosswalk_id,
            edge_id,
            segment_geom AS geometry
        FROM segments;
        """
    )


def classify_edges_by_intersection(con: duckdb.DuckDBPyConnection):
    """Classify edges based on their intersection with street segments."""
    con.execute(
        """
        -- 1. Add a new boolean column
        ALTER TABLE crosswalk_segments 
        ADD COLUMN is_vehicle_edge BOOLEAN;
        
        -- 2. Update is_vehicle_edge = TRUE if there's any intersection, otherwise FALSE
        UPDATE crosswalk_segments
        SET is_vehicle_edge = (
            SELECT COUNT(*) > 0
            FROM street_segments s
            WHERE ST_Intersects(ST_GeomFromText(crosswalk_segments.geometry), ST_GeomFromText(s.geometry))
        );
        """
    )


if __name__ == "__main__":
    conn = util.connect_to_duckdb("test_edge_classifier.db")
    initialize_edge_classifier_db(
        conn,
        "../../road_characteristics/boston_street_segments.geojson",
        "../../../../tests/test_boston_crosswalk.geojson",
    )
    simplify_crosswalk_polygon_to_box(conn)
    decompose_crosswalk_edges(conn)
    classify_edges_by_intersection(conn)
    # save the db table to geojson
    util.save_table_to_geojson(
        conn,
        "crosswalk_segments",
        "test_crosswalk_segments.geojson",
    )
