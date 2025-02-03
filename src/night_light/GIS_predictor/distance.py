from night_light.bronze_db.util import connect_to_duckdb

def find_streetlights_crosswalk_centers(db_path, dist):
    """
    Find all of the streetlights within a distance from a crosswalk center.

    Fill in the columns:
    - `streetlight_id`: a list of streetlight IDs (ints) within the specified distance from each crosswalk centerpoint
    - `streetlight_dist`: a list of distances (in meters) from the centerpoint to each nearby streetlight.

    Args:
        db_path: Path to the database containing the tables
        dist: int of meters to search for streetlights near each crosswalk centerpoint
    """
    conn = connect_to_duckdb(db_path)

    # Go through all of the centerpoints and find the street lights and distances
    crosswalks = conn.execute("SELECT crosswalk_id, geometry FROM crosswalk_centers_lights").fetchall()
    for crosswalk in crosswalks:
        # crosswalk_id = crosswalk[0]
        centerpoint = crosswalk[1]

        # Parse the coordinates into floats to work with query formatting
        point_coords = centerpoint[7:-1].split()
        lon, lat = float(point_coords[0]), float(point_coords[1])

        query = """
        SELECT streetlights.OBJECTID, 
               ST_Distance_Sphere(ST_GeomFromText(streetlights.geometry), ST_Point(?, ?)) AS dist
        FROM streetlights
        WHERE ST_DWithin_Spheroid(
            ST_GeomFromText(streetlights.geometry), 
            ST_Point(?, ?), 
            ?
        )
        """
        nearby_streetlights = conn.execute(query, (lon, lat, lon, lat, dist)).fetchall()
       
        # Extract the results
        streetlight_ids = [row[0] for row in nearby_streetlights]
        streetlight_distances = [row[1] for row in nearby_streetlights]

        # Add the new data to the table
        conn.execute("""
            UPDATE crosswalk_centers_lights
            SET streetlight_id = ?, streetlight_dist = ?
            WHERE geometry = ?
            """, (streetlight_ids, streetlight_distances, centerpoint))

    conn.commit()  
    print(f"Updated crosswalk_centers_lights for {len(crosswalks)} crosswalks.")


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
    db_path = "edge_classifier.db"
    conn = connect_to_duckdb(db_path)
    add_streetlights_to_edge_classifier()
    create_crosswalk_centers_lights(conn)
    find_streetlights_crosswalk_centers(db_path, 30)
