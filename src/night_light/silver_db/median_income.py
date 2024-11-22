from night_light.bronze_db.util import connect_to_duckdb

def generate_silver_median_income() -> None: 
    """
    Creates median income table for the silver database

    Rewrites pervious verison of the table if it exists.
    """
    db_path = "silver.db"
    conn = connect_to_duckdb(db_path)
    conn.execute("ATTACH DATABASE 'bronze.db' AS bronze")

    query = """
    DROP TABLE IF EXISTS crosswalks;

    CREATE TABLE median_income AS 
    SELECT GEOID, median_household_income, geometry
    FROM bronze.median_income;
    """

    conn.execute(query)
    print("Silver table regenerated for crosswalks")

if __name__ == "__main__":
    generate_silver_median_income()
