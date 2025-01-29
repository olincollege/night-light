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