from night_light.bronze_db.util import connect_to_duckdb
import datetime
import math



def find_streetlights_crosswalk_centers(db_path, dist):
    """
    Find all of the streetlights within a distance from each crosswalk center.

    Fill in the columns:
    - `streetlight_id`: a list of streetlight IDs (ints) within the specified distance from each crosswalk centerpoint
    - `streetlight_dist`: a list of distances (in meters) from the centerpoint to each nearby streetlight.

    Args:
        db_path: Path to the database containing the tables
        dist: int of meters to search for streetlights near each crosswalk centerpoint
    """
    conn = connect_to_duckdb(db_path)

    print(datetime.datetime.now())

    long_lat_flipper(conn, "streetlights")
    long_lat_flipper(conn, "crosswalk_centers_lights")

    print(datetime.datetime.now())

    query = """
    WITH nearby_streetlights AS (
        SELECT
            crosswalk_centers_lights.crosswalk_id,
            crosswalk_centers_lights.new_geometry AS crosswalk_geometry,
            streetlights.OBJECTID AS streetlight_id,
            streetlights.new_geometry AS streetlight_geometry
        FROM
            crosswalk_centers_lights
        JOIN streetlights
            ON ST_DWithin(
                ST_GeomFromText(streetlights.new_geometry), 
                ST_GeomFromText(crosswalk_centers_lights.new_geometry),
                ?
            )
    )
    SELECT
        crosswalk_id,
        crosswalk_geometry,
        array_agg(streetlight_id) AS streetlight_ids,
        array_agg(ST_Distance_Sphere(streetlight_geometry::GEOMETRY, crosswalk_geometry::GEOMETRY)) AS streetlight_dists
    FROM nearby_streetlights
    GROUP BY crosswalk_id, crosswalk_geometry
    """

    dist_degrees = meters_to_degrees(dist)

    # Execute the query
    crosswalks_streetlights = conn.execute(query, (dist_degrees,)).fetchall()

    print(datetime.datetime.now(), "adding to db")

    # Update crosswalk_centers_lights with the streetlight data
    for crosswalk in crosswalks_streetlights:
        crosswalk_geometry = crosswalk[1]
        streetlight_ids = crosswalk[2]
        streetlight_dists = crosswalk[3]

        conn.execute("""
            UPDATE crosswalk_centers_lights
            SET streetlight_id = ?, streetlight_dist = ?
            WHERE new_geometry = ?
        """, (streetlight_ids, streetlight_dists, crosswalk_geometry))

    # conn.commit()

    print(datetime.datetime.now())
    print(f"Updated crosswalk_centers_lights for {len(crosswalks_streetlights)} crosswalks.")


def long_lat_flipper(conn, table):
    """
    Flips the coordinate so that they are in lat, long order instead of long, lat
    """
    query = f"""
    ALTER TABLE {table} ADD COLUMN IF NOT EXISTS new_geometry TEXT;
    
    UPDATE {table}
    SET new_geometry = ST_AsText(
        ST_Point(ST_Y(ST_GeomFromText(geometry)), ST_X(ST_GeomFromText(geometry)))
    );
    """
    conn.execute(query)
    print("flipped coords")



def create_crosswalk_centers_lights(con):
    """
    Create a table called crosswalk_centers_lights.

    This table will include the columns streetlight_id and streetlight_dist.
    - `streetlight_id`: a list of ints
    - `streetlight_dist`: a list of floats
    args:
        conn: connection to duckdb table.
    """
    # Copy crosswalk_centers into a new table
    con.execute("""
        CREATE TABLE IF NOT EXISTS crosswalk_centers_lights AS
        SELECT * FROM crosswalk_centers
    """)

    # Add new columns: streetlight_id and streetlight_dist
    con.execute("""
    ALTER TABLE crosswalk_centers_lights ADD COLUMN IF NOT EXISTS streetlight_id INTEGER[]
    """)
    con.execute("""
        ALTER TABLE crosswalk_centers_lights ADD COLUMN IF NOT EXISTS streetlight_dist FLOAT[]
    """)

def add_streetlights_to_edge_classifier(conn):
    """
    Add the street light table to edge_classifier
    """
    conn.execute("ATTACH 'bronze.db' AS bronze;")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS streetlights AS 
        SELECT * FROM bronze.streetlights;
    """)


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


if __name__ == "__main__":
    db_path = "edge_classifier_lights3.db"
    conn = connect_to_duckdb(db_path)
    # # add_streetlights_to_edge_classifier()
    create_crosswalk_centers_lights(conn)
    find_streetlights_crosswalk_centers(db_path, 20)

    # util.save_table_to_geojson(
    #     conn,
    #     "crosswalk_centers_lights",
    #     "crosswalk_centers_lights.geojson",
    # )
