import duckdb.duckdb


def make_lines_from_crosswalk_to_streetlights(con: duckdb.DuckDBPyConnection):
    """Create a table with lines from the crosswalk centers to the streetlights."""
    con.execute(
        """
        CREATE OR REPLACE TABLE crosswalk_centers_to_lights AS
        WITH streetlight_expansion AS (
            -- Explode streetlight arrays into individual rows
            SELECT
                crosswalk_id,
                UNNEST(from_side_streetlight_id) AS streetlight_id,
                'from_side' AS side,
                ST_MakeLine(ST_GeomFromText(geometry), ST_GeomFromText(UNNEST(from_side_streetlight_geom))) AS geometry
            FROM
                crosswalk_centers_classified_lights
            WHERE from_side_streetlight_id IS NOT NULL
            UNION ALL
            SELECT
                crosswalk_id,
                UNNEST(to_side_streetlight_id) AS streetlight_id,
                'to_side' AS side,
                ST_MakeLine(ST_GeomFromText(geometry), ST_GeomFromText(UNNEST(to_side_streetlight_geom))) AS geometry
            FROM
                crosswalk_centers_classified_lights
            WHERE to_side_streetlight_id IS NOT NULL
        )
        SELECT * FROM streetlight_expansion;
        """
    )
