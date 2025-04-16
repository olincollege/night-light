import duckdb

import datetime
import math

## Links streetlights to crosswalk centers by identifying all streetlights within a specified distance of each crosswalk center. 
## The goal is to populate each crosswalk center with nearby streetlight IDs and their respective distances.


def find_streetlights_crosswalk_centers(con: duckdb.DuckDBPyConnection, dist: float):
    """
    Find all of the streetlights within a distance from each crosswalk center.

    Fill in the columns:
    - `streetlight_id`: a list of streetlight IDs (ints) within the specified distance from each crosswalk centerpoint
    - `streetlight_dist`: a list of distances (in meters) from the centerpoint to each nearby streetlight.

    Args:
        con: connection to duckdb table
        dist: float of meters to search for streetlights near each crosswalk centerpoint
    """
    long_lat_flipper(con, "streetlights")
    long_lat_flipper(con, "crosswalk_centers_lights")

    print(datetime.datetime.now(), "Calculating distances between streetlights and crosswalks. This might take awhile...")

    query = """
    WITH 
    -- 1. Precast geometries to avoid redundant parsing
    geom_inputs AS (
        SELECT 
            cl.crosswalk_id,
            ST_GeomFromText(cl.geometry_lat_long) AS cross_geom
        FROM crosswalk_centers_lights cl
    ),
    geom_lights AS (
        SELECT 
            s.OBJECTID AS streetlight_id,
            ST_GeomFromText(s.geometry_lat_long) AS light_geom
        FROM streetlights s
    ),
    -- 2. Add pre-filtering with bounding boxes for better performance
    filtered_pairs AS (
        SELECT 
            gi.crosswalk_id,
            gi.cross_geom,
            gl.streetlight_id,
            gl.light_geom
        FROM geom_inputs gi
        JOIN geom_lights gl
            ON ST_DWithin_Spheroid(gl.light_geom, gi.cross_geom, ?)
    )
    -- 3. Aggregate distances and IDs
    SELECT
        crosswalk_id,
        ST_AsText(cross_geom) AS crosswalk_geometry,
        array_agg(streetlight_id) AS streetlight_ids,
        array_agg(ST_Distance_Sphere(light_geom, cross_geom)) AS streetlight_dists
    FROM filtered_pairs
    GROUP BY crosswalk_id, cross_geom;
    """

    # Execute the query
    crosswalks_streetlights = con.execute(query, [dist]).fetchall()

    print(datetime.datetime.now(), "Finished calculations, adding to the db")

    # Update crosswalk_centers_lights with the streetlight data
    for crosswalk in crosswalks_streetlights:
        crosswalk_geometry = crosswalk[1]
        streetlight_ids = crosswalk[2]
        streetlight_dists = crosswalk[3]

        con.execute(
            """
            UPDATE crosswalk_centers_lights
            SET streetlight_id = ?, streetlight_dist = ?
            WHERE geometry_lat_long = ?
        """,
            (streetlight_ids, streetlight_dists, crosswalk_geometry),
        )

    print(datetime.datetime.now())
    print(
        f"Updated crosswalk_centers_lights for {len(crosswalks_streetlights)} crosswalks."
    )


def long_lat_flipper(con: duckdb.DuckDBPyConnection, table: str):
    """
    Flips the coordinate so that they are in lat, long order instead of long, lat

    Args:
        Name (string) of table of database
    """
    query = f"""
    ALTER TABLE {table} ADD COLUMN IF NOT EXISTS geometry_lat_long TEXT;
    
    UPDATE {table}
    SET geometry_lat_long = ST_AsText(
        ST_Point(ST_Y(ST_GeomFromText(geometry)), ST_X(ST_GeomFromText(geometry)))
    );
    """
    con.execute(query)


def create_crosswalk_centers_lights(con: duckdb.DuckDBPyConnection):
    """
    Create a table called crosswalk_centers_lights.

    This table will include the columns streetlight_id and streetlight_dist.
    - `streetlight_id`: a list of ints
    - `streetlight_dist`: a list of floats
    args:
        con: connection to duckdb table.
    """
    # Copy crosswalk_centers into a new table
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS crosswalk_centers_lights AS
        SELECT * FROM crosswalk_centers
    """
    )

    # Add new columns: streetlight_id and streetlight_dist
    con.execute(
        """
    ALTER TABLE crosswalk_centers_lights ADD COLUMN IF NOT EXISTS streetlight_id INTEGER[]
    """
    )
    con.execute(
        """
        ALTER TABLE crosswalk_centers_lights ADD COLUMN IF NOT EXISTS streetlight_dist FLOAT[]
    """
    )


def meters_to_degrees(meters:float, latitude=42.3601):
    """
    Convert meters to degrees

    Rough calculation that defults the location to boston. Calculation
    will tend to be an overestimates. It will pick which ever degree value
    is bigger between lat and long.

    args:
        meters: int
        latitude: int (defaults to boston)

    returns:
        int in degrees
    """
    latitude_change = meters / 111320
    longitude_change = meters / (111320 * math.cos(math.radians(latitude)))

    if longitude_change > latitude_change:
        return longitude_change
    return latitude_change
