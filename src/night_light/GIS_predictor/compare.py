import pandas as pd
import duckdb


def create_compare_table(con, file_path):
    df = pd.read_csv(file_path)

    conditions = []
    for _, row in df.iterrows():
        center_id = row["Center ID"]
        crosswalk_id = row["Crosswalk ID"]
        condition = f"crosswalk_id = {crosswalk_id} AND center_id = '{center_id}'"
        conditions.append(condition)

    query_conditions = " OR ".join(conditions)

    query = f"""
    CREATE TABLE IF NOT EXISTS crosswalk_compare AS
    SELECT crosswalk_id, center_id, light_heuristic, contrast_heuristic, to_heuristic, from_heuristic FROM crosswalk_centers_contrast
    WHERE {query_conditions};
    """

    con.execute(query)
    print("Table 'crosswalk_compare' created successfully.")


def add_collected_data_columns(con, df):
    """
    Create coloumns to put the csv data
    """
    con.execute("""                
    ALTER TABLE crosswalk_compare
    ADD COLUMN IF NOT EXISTS perceived_contrast string;
                
    ALTER TABLE crosswalk_compare
    ADD COLUMN IF NOT EXISTS perceived_visibility float;
    
    ALTER TABLE crosswalk_compare
    ADD COLUMN IF NOT EXISTS lux_toward_car float;
                
    ALTER TABLE crosswalk_compare
    ADD COLUMN IF NOT EXISTS lux_away_car float;
                
    ALTER TABLE crosswalk_compare
    ADD COLUMN IF NOT EXISTS net_lux float;
    """)

    # Update the table with data from csv
    for _, row in df.iterrows():
        center_id = row["Center ID"]
        crosswalk_id = row["Crosswalk ID"]
        perceived_contrast = row["Perceived Contrast"]
        perceived_contrast = f"'{perceived_contrast}'"

        perceived_visibility = row["Perceived Visibility (1-5)"]
        lux_toward_car = row["Average Lux (toward car)"]
        lux_away_car = row["Average Lux (away from car)"]
        net_lux = row["Net lux"]

        # Update the table with the perceived_contrast value
        update_query = f"""
        UPDATE crosswalk_compare
        SET perceived_contrast = {perceived_contrast},
            perceived_visibility = {perceived_visibility},
            lux_toward_car = {lux_toward_car},
            lux_away_car = {lux_away_car},
            net_lux = {net_lux}
        WHERE crosswalk_id = {crosswalk_id} AND center_id = '{center_id}';
        """
        con.execute(update_query)

def ordered_compare_table(con):
    """
    Make the order easier to read
    """
    query = f"""
    CREATE TABLE IF NOT EXISTS crosswalk_compared AS
    SELECT crosswalk_id,
        center_id,
        light_heuristic,
        perceived_visibility,
        lux_toward_car,
        to_side_heuristic,
        lux_away_car,
        from_side_heuristic,
        contrast_heuristic,
        perceived_contrast,
        net_lux FROM crosswalk_compare
    """

    con.execute(query)
    print("Table 'crosswalk_compare' created successfully.")


if __name__ == "__main__":
    con = duckdb.connect('src/night_light/boston_contrast.db') 
    file_path = 'SVDataCollection2-11.csv'
    df = pd.read_csv(file_path)

    # Call the function to filter the data and create the new table
    create_compare_table(con, file_path)
    add_collected_data_columns(con, df)
    ordered_compare_table(con)

