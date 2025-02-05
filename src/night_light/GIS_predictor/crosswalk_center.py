import duckdb

from night_light.bronze_db import util


def find_crosswalk_centers(con: duckdb.DuckDBPyConnection):
    """
    Find centers of the crosswalks for each side of the road.

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
        CREATE OR REPLACE TABLE crosswalk_centers AS
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
            HAVING COUNT(*) >= 2
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
                ) AS edge_mid
            FROM crosswalk_segments
            WHERE is_vehicle_edge = FALSE
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
                ) AS geometry
            FROM ped_edge_mid e
            JOIN intersection_mid i USING (crosswalk_id)
        )
        SELECT
            *
        FROM centers;
        """
    )


if __name__ == "__main__":
    con = util.connect_to_duckdb("edge_classifier/edge_classifier.db")
    find_crosswalk_centers(con)
    util.save_table_to_geojson(
        con,
        "crosswalk_centers",
        "crosswalk_centers.geojson",
    )
