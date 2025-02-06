from night_light.bronze_db.util import connect_to_duckdb
import datetime
import night_light.bronze_db.util as util



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
    print(datetime.datetime.now())
    conn = connect_to_duckdb(db_path)

    # Query that retrieves all crosswalks with their nearby streetlights and distances
    query = """
    WITH nearby_streetlights AS (
        SELECT
            crosswalk_centers_lights.crosswalk_id,
            crosswalk_centers_lights.geometry AS crosswalk_geometry,
            streetlights.OBJECTID AS streetlight_id,
            ST_Distance_Sphere(ST_GeomFromText(streetlights.geometry), ST_GeomFromText(crosswalk_centers_lights.geometry)) AS dist
        FROM
            crosswalk_centers_lights
        JOIN streetlights
            ON ST_DWithin_Spheroid(
                ST_GeomFromText(streetlights.geometry), 
                ST_GeomFromText(crosswalk_centers_lights.geometry),
                ?
            )
    )
    SELECT
        crosswalk_id,
        crosswalk_geometry,
        array_agg(streetlight_id) AS streetlight_ids,
        array_agg(dist) AS streetlight_dists
    FROM nearby_streetlights
    GROUP BY crosswalk_id, crosswalk_geometry
    """

    # Execute the query to get all results
    crosswalks_streetlights = conn.execute(query, (dist,)).fetchall()

    print(datetime.datetime.now())
    print("done with first query")

    # Update crosswalk_centers_lights with the streetlight data
    for crosswalk in crosswalks_streetlights:
        crosswalk_geometry = crosswalk[1]  # crosswalk geometry as POINT
        streetlight_ids = crosswalk[2]    # List of streetlight IDs
        streetlight_dists = crosswalk[3]  # List of distances for each streetlight

        # Execute update with the geometry of the crosswalk
        conn.execute("""
            UPDATE crosswalk_centers_lights
            SET streetlight_id = ?, streetlight_dist = ?
            WHERE geometry = ?
        """, (streetlight_ids, streetlight_dists, crosswalk_geometry))

    conn.commit()

    print(datetime.datetime.now())
    print(f"Updated crosswalk_centers_lights for {len(crosswalks_streetlights)} crosswalks.")





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

def add_streetlights_to_edge_classifier():
    """
    Add the street light table to edge_classifier
    """
    conn_edge = connect_to_duckdb('edge_classifier.db')
    conn_edge.execute("ATTACH 'bronze.db' AS bronze;")
    conn_edge.execute("""
        CREATE TABLE IF NOT EXISTS streetlights AS 
        SELECT * FROM bronze.streetlights;
    """)
    conn_edge.close()




if __name__ == "__main__":
    db_path = "edge_classifier5.db"
    conn = connect_to_duckdb(db_path)
    # # add_streetlights_to_edge_classifier()
    # # create_crosswalk_centers_lights(conn)
    find_streetlights_crosswalk_centers(db_path, 20)

    # util.save_table_to_geojson(
    #     conn,
    #     "crosswalk_centers_lights",
    #     "crosswalk_centers_lights.geojson",
    # )
