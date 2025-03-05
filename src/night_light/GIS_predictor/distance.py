import duckdb

import datetime
import math


def find_streetlights_crosswalk_centers(con: duckdb.DuckDBPyConnection, dist):
    """
    Find all of the streetlights within a distance from each crosswalk center.

    Fill in the columns:
    - `streetlight_id`: a list of streetlight IDs (ints) within the specified distance from each crosswalk centerpoint
    - `streetlight_dist`: a list of distances (in meters) from the centerpoint to each nearby streetlight.

    Args:
        con: connection to duckdb table
        dist: int of meters to search for streetlights near each crosswalk centerpoint
    """
    print(datetime.datetime.now())

    long_lat_flipper(con, "streetlights")
    long_lat_flipper(con, "crosswalk_centers_lights")
    lat_long_to_meters(con, "streetlights")

    print(datetime.datetime.now())

    query = """
    WITH nearby_streetlights AS (
        SELECT
            crosswalk_centers_lights.crosswalk_id,
            crosswalk_centers_lights.geometry_lat_long AS crosswalk_geometry,
            streetlights.OBJECTID AS streetlight_id,
            streetlights.geometry_lat_long AS streetlight_geometry_lat_long,
            streetlights.geometry as streetlight_geometry,
            streetlights.geometry_xy as streetlight_geometry_xy
        FROM
            crosswalk_centers_lights
        JOIN streetlights
            ON ST_DWithin(
                ST_GeomFromText(streetlights.geometry_lat_long), 
                ST_GeomFromText(crosswalk_centers_lights.geometry_lat_long),
                ?
            )
    )
    SELECT
        crosswalk_id,
        crosswalk_geometry,
        array_agg(streetlight_id) AS streetlight_ids,
        array_agg(ST_Distance_Sphere(streetlight_geometry_lat_long::GEOMETRY, crosswalk_geometry::GEOMETRY)) AS streetlight_dists,
        array_agg(streetlight_geometry_lat_long) AS streetlight_geometries_lat_long,
        array_agg(streetlight_geometry) AS streetlight_geometries,
        array_agg(streetlight_geometry_xy) as streetlight_geometries_xy

    FROM nearby_streetlights
    GROUP BY crosswalk_id, crosswalk_geometry
    """

    dist_degrees = meters_to_degrees(dist)

    # Execute the query
    crosswalks_streetlights = con.execute(query, (dist_degrees,)).fetchall()

    print(datetime.datetime.now(), "adding to db")

    # Update crosswalk_centers_lights with the streetlight data
    for crosswalk in crosswalks_streetlights:
        crosswalk_geometry = crosswalk[1]
        streetlight_ids = crosswalk[2]
        streetlight_dists = crosswalk[3]
        streetlight_geom_lat_long = crosswalk[4]
        streetlight_geom = crosswalk[5]
        streetlight_geom_xy = crosswalk[6]

        con.execute(
            """
            UPDATE crosswalk_centers_lights
            SET streetlight_id = ?, streetlight_dist = ?, streetlight_geometries_lat_long = ?, streetlight_geometries = ?, streetlight_geometries_xy = ?
            WHERE geometry_lat_long = ?
        """,
            (streetlight_ids, streetlight_dists, streetlight_geom_lat_long, streetlight_geom, streetlight_geom_xy, crosswalk_geometry,),
        )

    print(datetime.datetime.now())
    print(
        f"Updated crosswalk_centers_lights for {len(crosswalks_streetlights)} crosswalks."
    )


def long_lat_flipper(con: duckdb.DuckDBPyConnection, table):
    """
    Flips the coordinate so that they are in lat, long order instead of long, lat
    """
    query = f"""
    ALTER TABLE {table} ADD COLUMN IF NOT EXISTS geometry_lat_long TEXT;
    
    UPDATE {table}
    SET geometry_lat_long = ST_AsText(
        ST_Point(ST_Y(ST_GeomFromText(geometry)), ST_X(ST_GeomFromText(geometry)))
    )
    """
    con.execute(query)
    print("flipped coords")


def lat_long_to_meters(con: duckdb.DuckDBPyConnection, table):
    """
    make to meters
    """
    query = f"""
    ALTER TABLE {table} ADD COLUMN IF NOT EXISTS geometry_xy TEXT;
    
    UPDATE {table}
    SET geometry_xy = ST_AsText(
                            ST_Transform(
                                ST_GeomFromText({table}.geometry_lat_long), 
                                CAST('EPSG:4326' AS VARCHAR),
                                CAST('EPSG:3857' AS VARCHAR)
                            )
                        )
    """
    con.execute(query)
    print("changed to meters")


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
        LIMIT 500
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
    """)
    con.execute(
        """
        ALTER TABLE crosswalk_centers_lights ADD COLUMN IF NOT EXISTS streetlight_geometries TEXT[]
    """)
    con.execute(
        """
        ALTER TABLE crosswalk_centers_lights ADD COLUMN IF NOT EXISTS streetlight_geometries_lat_long TEXT[]
    """
    )
    con.execute(
        """
        ALTER TABLE crosswalk_centers_lights ADD COLUMN IF NOT EXISTS streetlight_geometries_xy TEXT[]
    """
    )


def meters_to_degrees(meters, latitude=42.3601):
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
