from night_light.bronze_db.util import connect_to_duckdb

def find_streetlight_dist(centerpoint, dist, db_path):
    """
    Find the lamp posts that are near a given crosswalk centerpoint and calculate the distance to each streetlight.
    
    args:
        centerpoint: A tuple of coordinates (longitude, latitude) representing the centerpoint of the crosswalk.
        dist: int of meters aways from center point to search for
        db_path: Path to the database containing the tables

        
    returns:
        List of tuples [(ID, location, distance), (ID, location, distance), ...]
    """
    conn = connect_to_duckdb(db_path)
    
    query = """
    SELECT streetlights.OBJECTID, streetlights.geometry, ST_Distance_Sphere(
               ST_GeomFromText(streetlights.geometry), 
               ST_Point(?, ?)
           ) AS distance
    FROM streetlights
    WHERE ST_DWithin_Spheroid(
        ST_GeomFromText(streetlights.geometry), 
        ST_Point(?, ?), 
        ?
    )
    """
    result = conn.execute(query, (centerpoint[0], centerpoint[1], centerpoint[0], centerpoint[1], dist)).fetchall()

    columns = [desc[0] for desc in conn.description]  
    print("Headers:", columns)
    for row in result:
        print(row)
    print(len(result))

    return result


# res = find_streetlight_dist((-71.14649222685253, 42.292342013391462), 30, "bronze.db")
# print("---------------")
# print(res)

def update_local_lamps(db_path, dist):
    """
    Update the crosswalks table by adding a new column `local_lamps` that stores a list of streetlight IDs
    within the specified distance from each crosswalk centerpoint.

    args:
        db_path: Path to the database containing the tables
        dist: int of meters to search for streetlights near each crosswalk centerpoint
    """
    conn = connect_to_duckdb(db_path)

    # column to crosswalk table if it doesn't exist
    conn.execute("""
        ALTER TABLE crosswalks
        ADD COLUMN IF NOT EXISTS local_lamps LIST<INTEGER>
    """)

    # Fetch all the centerpoints from the crosswalks table
    crosswalks = conn.execute("SELECT OBJECTID, centerpoint FROM crosswalks").fetchall()

    # iterate through each centerpoint
    for crosswalk in crosswalks:
        crosswalk_id = crosswalk[0]
        centerpoint = crosswalk[1]

        # Query to find all streetlights within the specified distance from the crosswalk centerpoint
        query = """
        SELECT streetlights.OBJECTID
        FROM streetlights
        WHERE ST_DWithin_Spheroid(
            ST_GeomFromText(streetlights.geometry), 
            ST_Point(?, ?), 
            ?
        )
        """
        # Execute the query and get the nearby streetlight IDs
        nearby_streetlights = conn.execute(query, (centerpoint[0], centerpoint[1], dist)).fetchall()

        # Extract the streetlight IDs from the result
        local_lamps = [row[0] for row in nearby_streetlights]

        # Update the crosswalk's `local_lamps` column with the list of nearby streetlight IDs
        conn.execute("""
        UPDATE crosswalks
        SET local_lamps = ?
        WHERE OBJECTID = ?
        """, (local_lamps, crosswalk_id))

    conn.commit()  # Commit the changes to the database
    print(f"Updated local_lamps for {len(crosswalks)} crosswalks.")

