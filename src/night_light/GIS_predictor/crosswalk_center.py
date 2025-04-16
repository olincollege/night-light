import duckdb

## Calculates center points for crosswalks, taking into account whether the 
## intersecting street is one-way or two-way. Creates the table crosswalk_centers.

def find_crosswalk_centers(con: duckdb.DuckDBPyConnection):
    """Find the centers of crosswalks."""
    # Find the centers of crosswalks for one-way and two-way streets
    _find_crosswalk_centers_oneway(con)
    _find_crosswalk_centers_twoway(con)

    # Combine the one-way and two-way centers into one table
    con.execute(
        """
        CREATE OR REPLACE TABLE crosswalk_centers AS
        SELECT
            crosswalk_id,
            street_segment_id,
            ped_edge_geom,
            street_center_point,
            geometry,
            center_id,
            is_oneway
        FROM crosswalk_centers_oneway
        
        UNION ALL
        
        SELECT
            crosswalk_id,
            street_segment_id,
            ped_edge_geom,
            street_center_point,
            geometry,
            center_id,
            is_oneway
        FROM crosswalk_centers_twoway;
        
        DROP TABLE IF EXISTS crosswalk_centers_oneway;
        DROP TABLE IF EXISTS crosswalk_centers_twoway;
        """
    )


def _find_crosswalk_centers_oneway(con: duckdb.DuckDBPyConnection):
    """
    Find crosswalk centers for one-way streets.

    Steps to get the centers of the crosswalks:
    1. Find the points of intersection of the crosswalks with the street segments.
    2. Find the midpoint of the intersection points.
    3. Save the midpoint as a point in the database as a new table.
    """
    con.execute(
        """
        CREATE OR REPLACE TABLE crosswalk_centers_oneway AS
        SELECT
            i.crosswalk_id,
            i.street_segment_id,
            p.ped_edge_geom,
            ST_AsText(i.center_geom) AS street_center_point,
            ST_AsText(i.center_geom) AS geometry,
            TRUE AS is_oneway,
            'A' AS center_id
        FROM (
            SELECT
                cw.OBJECTID AS crosswalk_id,
                s.OBJECTID AS street_segment_id,
                ST_Centroid(
                    ST_Intersection(
                        ST_Boundary(ST_GeomFromText(cw.geometry)),
                        ST_GeomFromText(s.geometry)
                    )
                ) AS center_geom
            FROM crosswalks cw
            JOIN street_segments s
                ON ST_Intersects(ST_Boundary(ST_GeomFromText(cw.geometry)), ST_GeomFromText(s.geometry))
            WHERE cw.OBJECTID IN (
                SELECT DISTINCT crosswalk_id FROM crosswalk_segments WHERE is_oneway = TRUE
            )
        ) i
        LEFT JOIN (
            SELECT
                cs.crosswalk_id,
                cs.geometry AS ped_edge_geom
            FROM crosswalk_segments cs
            JOIN (
                SELECT
                    crosswalk_id,
                    MIN(edge_id) AS min_edge_id
                FROM crosswalk_segments
                WHERE is_vehicle_edge = FALSE
                  AND crosswalk_id IN (
                      SELECT DISTINCT crosswalk_id FROM crosswalk_segments WHERE is_oneway = TRUE
                  )
                GROUP BY crosswalk_id
            ) selected
            ON cs.crosswalk_id = selected.crosswalk_id AND cs.edge_id = selected.min_edge_id
        ) p
        ON i.crosswalk_id = p.crosswalk_id;
        """
    )


def _find_crosswalk_centers_twoway(con: duckdb.DuckDBPyConnection):
    """
    Find crosswalk centers for two-way streets.

    Steps to get the centers of the crosswalks:
        * Assume that there are always 2 centers for each crosswalk that mark each vehicle
        * sides of the road. This means that we're assuming 2-way traffic.
    1. Find the points of intersection of the crosswalks with the street segments.
    2. Find the midpoint of the intersection points.
    3. Find the midpoints of the two edges of the crosswalk that pedestrians use.
    4. Find the two midpoints between the midpoints of the edges and the midpoint of the
        intersections.
    5. Save the two midpoints as individual points in the database as a new table.

    Known edge cases:
    - More than 4 vertices for a crosswalk polygon
        This causes extra intersection points and segments; using oriented rectangles to fix
        this issue.
    - More than 1 intersecting street segment
        Averaging multiple intersection points to output 2 intersection points.
    """
    con.execute(
        """
        CREATE OR REPLACE TABLE crosswalk_centers_twoway AS
        WITH intersection_points AS (
            SELECT
                cw.OBJECTID AS crosswalk_id,
                (UNNEST(
                    ST_Dump(
                        ST_Intersection(
                            ST_Boundary(ST_GeomFromText(cw.geometry)),
                            ST_GeomFromText(s.geometry)
                        )
                    )
                ).geom) AS intersection_geom
            FROM crosswalks cw
            JOIN street_segments s
                ON ST_Intersects(
                    ST_Boundary(ST_GeomFromText(cw.geometry)),
                    ST_GeomFromText(s.geometry)
                )
        ),
        intersection_mid AS (
            SELECT
                crosswalk_id,
                -- Average all X’s and Y’s to get one “intersection_center”
                ST_Point(
                    AVG(ST_X(intersection_geom)),
                    AVG(ST_Y(intersection_geom))
                ) AS intersection_center
            FROM intersection_points
            GROUP BY crosswalk_id
            -- Use >= 2 (not = 2) so you include crosswalks with more than 2 intersection points
            HAVING COUNT(*) >= 1
        ),
        ped_edge_mid AS (
            SELECT
                crosswalk_id,
                street_segment_id,
                geometry as ped_edge_geom,
                ST_Point(
                    (
                        ST_X(ST_PointN(ST_GeomFromText(geometry), 1)) +
                        ST_X(ST_PointN(ST_GeomFromText(geometry), 2))
                    ) / 2.0,
                    (
                        ST_Y(ST_PointN(ST_GeomFromText(geometry), 1)) +
                        ST_Y(ST_PointN(ST_GeomFromText(geometry), 2))
                    ) / 2.0
                ) AS edge_mid,
                is_oneway
            FROM crosswalk_segments
            WHERE is_vehicle_edge = FALSE AND is_oneway = FALSE
        ),
        centers AS (
            SELECT
                e.crosswalk_id,
                e.street_segment_id,
                e.ped_edge_geom,
                ST_AsText(i.intersection_center) AS street_center_point,
                ST_AsText(
                    ST_Point(
                        (ST_X(e.edge_mid) + ST_X(i.intersection_center)) / 2.0,
                        (ST_Y(e.edge_mid) + ST_Y(i.intersection_center)) / 2.0
                    )
                ) AS geometry,
                e.is_oneway
            FROM ped_edge_mid e
            JOIN intersection_mid i USING (crosswalk_id)
        )
        SELECT
            crosswalk_id,
            street_segment_id,
            ped_edge_geom,
            street_center_point,
            geometry,
            CASE 
                WHEN rn = 1 THEN 'A'
                WHEN rn = 2 THEN 'B'
                ELSE NULL
            END AS center_id,
            is_oneway
        FROM (
            SELECT
                *,
                ROW_NUMBER() OVER (PARTITION BY crosswalk_id ORDER BY geometry) AS rn
            FROM centers
        ) sub
        WHERE rn <= 2;
        """
    )
