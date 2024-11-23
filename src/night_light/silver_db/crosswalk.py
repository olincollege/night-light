from night_light.bronze_db.util import connect_to_duckdb

def generate_silver_crosswalks() -> None: 
    """
    Creates crosswalk table for the silver database

    Rewrites pervious verison of the table if it exists.
    """
    db_path = "silver.db"
    conn = connect_to_duckdb(db_path)
    conn.execute("ATTACH DATABASE 'bronze.db' AS bronze")

    query = """
    DROP TABLE IF EXISTS crosswalks;

    CREATE TABLE crosswalks AS 
    SELECT OBJECTID, Class_Loc, CrossType, geometry
    FROM bronze.crosswalks;
    """

    conn.execute(query)
    print("Silver table regenerated for crosswalks")

if __name__ == "__main__":
    generate_silver_crosswalks()