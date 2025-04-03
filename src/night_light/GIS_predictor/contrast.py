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
            SELECT
                crosswalk_id,
                MAX(CASE WHEN center_id = 'A' THEN geometry END) AS geom_a,
                MAX(
                    CASE 
                        WHEN center_id = 'B' THEN geometry
                        WHEN is_oneway THEN ST_AsText(
                            ST_Point(
                                (ST_X(ST_PointN(ST_GeomFromText(ped_edge_geom), 1)) + ST_X(ST_PointN(ST_GeomFromText(ped_edge_geom), 2))) / 2.0,
                                (ST_Y(ST_PointN(ST_GeomFromText(ped_edge_geom), 1)) + ST_Y(ST_PointN(ST_GeomFromText(ped_edge_geom), 2))) / 2.0
                            )
                        )
                    END
                ) AS geom_b
            FROM crosswalk_centers_lights
            WHERE center_id IS NOT NULL OR is_oneway = TRUE
            GROUP BY crosswalk_id
        ),
        grouped_crosswalks AS (
            SELECT
                crosswalk_id,
                ST_MakeLine(ST_GeomFromText(geom_a), ST_GeomFromText(geom_b)) AS a_to_b
            FROM centers
        ),
        from_to_vectors AS (
            SELECT
                cl.crosswalk_id,
                cl.center_id,
                cl.streetlight_id,
                cl.geometry AS crosswalk_center,
                gc.a_to_b,
                ST_MakeLine(ST_GeomFromText(from_coord), ST_GeomFromText(to_coord)) AS from_to_to
            FROM crosswalk_centers_lights cl
            JOIN grouped_crosswalks gc USING (crosswalk_id)
        ),
        exploded_streetlights AS (
            SELECT
                f.crosswalk_id,
                f.center_id,
                t.streetlight_id,
                f.a_to_b,
                f.from_to_to,
                ST_MakeLine(ST_GeomFromText(f.crosswalk_center), ST_GeomFromText(s.geometry)) AS center_to_light
            FROM from_to_vectors f
            CROSS JOIN UNNEST(f.streetlight_id) AS t(streetlight_id)
            JOIN streetlights s ON s.OBJECTID = t.streetlight_id
        ),
        cross_product_computation AS (
            SELECT
                e.crosswalk_id,
                e.center_id,
                e.streetlight_id,
                e.center_to_light,
                e.a_to_b,
                (ST_X(ST_PointN(e.center_to_light,2)) - ST_X(ST_PointN(e.center_to_light,1))) AS delta_x_cl,
                (ST_Y(ST_PointN(e.center_to_light,2)) - ST_Y(ST_PointN(e.center_to_light,1))) AS delta_y_cl,
                (ST_X(ST_PointN(e.a_to_b,2)) - ST_X(ST_PointN(e.a_to_b,1))) AS delta_x_ab,
                (ST_Y(ST_PointN(e.a_to_b,2)) - ST_Y(ST_PointN(e.a_to_b,1))) AS delta_y_ab,
                SIGN(
                    (ST_X(ST_PointN(e.a_to_b,2)) - ST_X(ST_PointN(e.a_to_b,1))) * 
                    (ST_Y(ST_PointN(e.from_to_to,2)) - ST_Y(ST_PointN(e.from_to_to,1))) - 
                    (ST_Y(ST_PointN(e.a_to_b,2)) - ST_Y(ST_PointN(e.a_to_b,1))) * 
                    (ST_X(ST_PointN(e.from_to_to,2)) - ST_X(ST_PointN(e.from_to_to,1)))
                ) AS from_to_sign,
                SIGN(
                    (ST_X(ST_PointN(e.a_to_b,2)) - ST_X(ST_PointN(e.a_to_b,1))) * 
                    (ST_Y(ST_PointN(e.center_to_light,2)) - ST_Y(ST_PointN(e.center_to_light,1))) - 
                    (ST_Y(ST_PointN(e.a_to_b,2)) - ST_Y(ST_PointN(e.a_to_b,1))) * 
                    (ST_X(ST_PointN(e.center_to_light,2)) - ST_X(ST_PointN(e.center_to_light,1)))
                ) AS center_to_light_sign
            FROM exploded_streetlights e
        ),
        classification AS (
            SELECT
                c.crosswalk_id,
                c.center_id,
                c.streetlight_id,
                ST_AsText(c.center_to_light) AS line_geom,
                ST_AsText(ST_PointN(c.center_to_light,2)) AS geometry,
                CASE 
                    WHEN c.from_to_sign = c.center_to_light_sign THEN 'to'
                    ELSE 'from'
                END AS side,
                ATAN2(
                    c.delta_x_cl * c.delta_y_ab - c.delta_y_cl * c.delta_x_ab,
                    c.delta_x_cl * c.delta_x_ab + c.delta_y_cl * c.delta_y_ab
                ) AS angle_rad,
                ABS(SIN(
                    ATAN2(
                        c.delta_x_cl * c.delta_y_ab - c.delta_y_cl * c.delta_x_ab,
                        c.delta_x_cl * c.delta_x_ab + c.delta_y_cl * c.delta_y_ab
                    )
                )) AS abs_sin_angle,
                c.a_to_b
            FROM cross_product_computation c
        )
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
                SUM(CASE WHEN side = 'to' THEN abs_sin_angle / (dist * dist) ELSE 0 END) AS to_contrast_heuristic,
                SUM(CASE WHEN side = 'from' THEN abs_sin_angle / (dist * dist) ELSE 0 END) AS from_contrast_heuristic,
                SUM(CASE WHEN side = 'to' THEN 1.0 / (dist * dist) ELSE 0 END) AS to_brightness_heuristic,
                SUM(CASE WHEN side = 'from' THEN 1.0 / (dist * dist) ELSE 0 END) AS from_brightness_heuristic
            FROM classified_streetlights
            GROUP BY crosswalk_id, center_id
        ),
        contrast AS (
            -- Compute contrast heuristic using the provided threshold
            SELECT 
                h.crosswalk_id,
                h.center_id,
                h.to_contrast_heuristic,
                h.from_contrast_heuristic,
                h.to_brightness_heuristic,
                h.from_brightness_heuristic,
                CASE 
                    WHEN h.to_contrast_heuristic = 0 OR h.from_contrast_heuristic = 0 THEN
                        CASE 
                            WHEN ABS(h.from_contrast_heuristic - h.to_contrast_heuristic) <= ? THEN 'no contrast'
                            WHEN ABS(h.from_contrast_heuristic - h.to_contrast_heuristic) <= ? THEN 
                                CASE 
                                    WHEN h.from_contrast_heuristic > h.to_contrast_heuristic THEN 'weak positive contrast'
                                    ELSE 'weak negative contrast'
                                END
                            WHEN h.from_contrast_heuristic > h.to_contrast_heuristic THEN 'strong positive contrast'
                            ELSE 'strong negative contrast'
                        END
                    ELSE
                        CASE 
                            WHEN ABS(h.from_contrast_heuristic - h.to_contrast_heuristic) <= ? THEN 'no contrast'
                            WHEN ABS(h.from_contrast_heuristic - h.to_contrast_heuristic) <= ? THEN 
                                CASE 
                                    WHEN h.from_contrast_heuristic > h.to_contrast_heuristic THEN 'weak positive contrast'
                                    ELSE 'weak negative contrast'
                                END
                            WHEN h.from_contrast_heuristic > h.to_contrast_heuristic THEN 'strong positive contrast'
                            ELSE 'strong negative contrast'
                        END
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
    """,
        [threshold / 2, threshold * 3 / 4, threshold * 3 / 4, threshold],
    )
