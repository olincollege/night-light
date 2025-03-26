import duckdb


def classify_lights_by_side(con: duckdb.DuckDBPyConnection):
    """
    Classify lights as either `to` or `from` side of the crosswalk center.

    The algorithm compares the sign of the cross products to classify. Refer to the
    script for detailed steps.
    """
    con.execute(
        """
        CREATE OR REPLACE TABLE classified_streetlights AS
        WITH centers AS (
            -- Get geometries for center_id A and B to construct the `a_to_b` line
            SELECT
                crosswalk_id,
                MAX(CASE WHEN center_id = 'A' THEN geometry END) AS geom_a,
                MAX(CASE WHEN center_id = 'B' THEN geometry END) AS geom_b
            FROM crosswalk_centers_lights
            GROUP BY crosswalk_id
        ),
        grouped_crosswalks AS (
            -- 1. Construct the `a_to_b` line using center_id A and B
            SELECT
                c.crosswalk_id,
                ST_MakeLine(ST_GeomFromText(c.geom_a), ST_GeomFromText(c.geom_b)) AS a_to_b
            FROM centers c
        ),
        from_to_vectors AS (
            -- 2. Add column `from_to_to` for every crosswalk row using from_coord and to_coord
            SELECT
                cl.crosswalk_id,
                cl.center_id,
                cl.streetlight_id,
                cl.geometry AS crosswalk_center,
                gc.a_to_b,
                ST_MakeLine(ST_GeomFromText(from_coord), ST_GeomFromText(to_coord)) AS from_to_to,
            FROM crosswalk_centers_lights cl
            JOIN grouped_crosswalks gc USING (crosswalk_id)
        ),
        exploded_streetlights AS (
            -- 3. Unnest `streetlight_id` and fetch geometry from `streetlights`
            SELECT
                f.crosswalk_id,
                f.center_id,
                t.streetlight_id,  -- Unnested value
                f.a_to_b,
                f.from_to_to,
                ST_MakeLine(ST_GeomFromText(f.crosswalk_center), ST_GeomFromText(s.geometry)) AS center_to_light
            FROM from_to_vectors f
            CROSS JOIN UNNEST(f.streetlight_id) AS t(streetlight_id)  -- Unnest array
            JOIN streetlights s ON s.OBJECTID = t.streetlight_id  -- Fetch geometry from `streetlights`
        ),
        cross_product_computation AS (
            -- 4. Compute the sign of the cross product between a_to_b and from_to_to
            -- 5. Compute the sign of the cross product between a_to_b and center_to_light
            SELECT
                e.crosswalk_id,
                e.center_id,
                e.streetlight_id,
                e.center_to_light,
                SIGN(
                    (ST_X(ST_PointN(a_to_b,2)) - ST_X(ST_PointN(a_to_b,1))) * 
                    (ST_Y(ST_PointN(from_to_to,2)) - ST_Y(ST_PointN(from_to_to,1))) - 
                    (ST_Y(ST_PointN(a_to_b,2)) - ST_Y(ST_PointN(a_to_b,1))) * 
                    (ST_X(ST_PointN(from_to_to,2)) - ST_X(ST_PointN(from_to_to,1)))
                ) AS from_to_sign,
                SIGN(
                    (ST_X(ST_PointN(a_to_b,2)) - ST_X(ST_PointN(a_to_b,1))) * 
                    (ST_Y(ST_PointN(center_to_light,2)) - ST_Y(ST_PointN(center_to_light,1))) - 
                    (ST_Y(ST_PointN(a_to_b,2)) - ST_Y(ST_PointN(a_to_b,1))) * 
                    (ST_X(ST_PointN(center_to_light,2)) - ST_X(ST_PointN(center_to_light,1)))
                ) AS center_to_light_sign
            FROM exploded_streetlights e
        ),
        classification AS (
            -- 6. Apply classification logic where all points are classified as 'to_side' or 'from_side'
            SELECT
                c.crosswalk_id,
                c.center_id,
                c.streetlight_id,
                c.center_to_light AS line_geom,
                ST_PointN(c.center_to_light,2) AS geometry,
                CASE 
                    WHEN c.from_to_sign = c.center_to_light_sign THEN 'to'
                    ELSE 'from'
                END AS side
            FROM cross_product_computation c
        )
        -- 7. Final table with `crosswalk_id`, `center_id`, `streetlight_id`, `side`, `geometry`
        SELECT * FROM classification;
        """
    )


def add_distances(con: duckdb.DuckDBPyConnection):
    """Append distances of the streetlights to the table."""
    con.execute(
        """
        ALTER TABLE classified_streetlights 
        ADD COLUMN IF NOT EXISTS dist FLOAT;
        """
    )
    con.execute(
        """
        UPDATE classified_streetlights AS cls
        SET dist = array_extract(cl.streetlight_dist, array_position(cl.streetlight_id, cls.streetlight_id))
        FROM crosswalk_centers_lights cl
        WHERE cls.crosswalk_id = cl.crosswalk_id
        AND cls.center_id = cl.center_id
        AND array_position(cl.streetlight_id, cls.streetlight_id) IS NOT NULL;
        """
    )


def calculate_contrast_heuristics(con: duckdb.DuckDBPyConnection, threshold: float):
    """
    Computes to_heuristic, from_heuristic, and contrast_heuristic for crosswalk centers.
    Uses a threshold to determine when contrast should be classified as 'no contrast'.
    """

    con.execute("DROP TABLE IF EXISTS crosswalk_centers_contrast;")

    con.execute(
        f"""
        CREATE TABLE crosswalk_centers_contrast AS 
        WITH heuristics AS (
            -- Compute heuristics once per crosswalk center
            SELECT 
                crosswalk_id,
                center_id,
                SUM(CASE WHEN side = 'to' THEN 1.0 / (dist * dist) ELSE 0 END) AS to_heuristic,
                SUM(CASE WHEN side = 'from' THEN 1.0 / (dist * dist) ELSE 0 END) AS from_heuristic
            FROM classified_streetlights
            GROUP BY crosswalk_id, center_id
        ),
        contrast AS (
            -- Compute contrast heuristic using the provided threshold
            SELECT 
                h.crosswalk_id,
                h.center_id,
                h.to_heuristic,
                h.from_heuristic,
                CASE 
                    WHEN ABS(h.from_heuristic - h.to_heuristic) <= {threshold} THEN 'no contrast'
                    WHEN h.from_heuristic > h.to_heuristic THEN 'positive contrast'
                    WHEN h.from_heuristic < h.to_heuristic THEN 'negative contrast'
                END AS contrast_heuristic
            FROM heuristics h
        )
        SELECT 
            c.*,
            cl.geometry  -- Add the geometry column from crosswalk_centers_lights
        FROM contrast c
        LEFT JOIN crosswalk_centers_lights cl 
        ON c.crosswalk_id = cl.crosswalk_id 
        AND c.center_id = cl.center_id;
    """
    )
