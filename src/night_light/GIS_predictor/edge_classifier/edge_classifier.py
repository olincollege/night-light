import duckdb
import night_light.bronze_db.util as util


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
    """Classify edges based on intersection with street segments and oneway status."""
    con.execute(
        """
        -- 1. Ensure necessary columns exist
        ALTER TABLE crosswalk_segments 
        ADD COLUMN IF NOT EXISTS is_vehicle_edge BOOLEAN DEFAULT FALSE;
        
        ALTER TABLE crosswalk_segments
        ADD COLUMN IF NOT EXISTS street_segment_id INT;
        
        ALTER TABLE crosswalk_segments
        ADD COLUMN IF NOT EXISTS is_oneway BOOLEAN DEFAULT FALSE;
        
        -- 2. Update crosswalk segments to find intersecting street segments
        UPDATE crosswalk_segments
        SET 
        is_vehicle_edge = COALESCE((
            SELECT COUNT(*) > 0
            FROM street_segments s
            WHERE ST_Intersects(ST_GeomFromText(crosswalk_segments.geometry), ST_GeomFromText(s.geometry))
        ), FALSE), -- Default to FALSE if no intersection is found
        street_segment_id = (
            SELECT COALESCE(MAX(t.street_segment_id), NULL) -- Ensure NULL safety
            FROM (
                SELECT cs2.crosswalk_id,
                       (SELECT s.OBJECTID
                        FROM street_segments s
                        WHERE ST_Intersects(
                                 ST_GeomFromText(cs2.geometry),
                                 ST_GeomFromText(s.geometry)
                              )
                        ORDER BY s.OBJECTID LIMIT 1 -- Get the first intersecting street segment
                       ) AS street_segment_id
                FROM crosswalk_segments cs2
                WHERE cs2.crosswalk_id = crosswalk_segments.crosswalk_id
            ) t
        );
        
        -- 3. Determine if the intersecting street segment is one-way
        UPDATE crosswalk_segments
        SET is_oneway = COALESCE((
        SELECT CASE 
            WHEN s.ONEWAY = 'FT' THEN TRUE
            ELSE FALSE
        END
        FROM street_segments s
        WHERE s.OBJECTID = crosswalk_segments.street_segment_id
        ), FALSE) -- Default to FALSE if no street segment is found
        WHERE is_vehicle_edge = TRUE;
        """
    )
