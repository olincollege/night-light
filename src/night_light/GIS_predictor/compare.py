import pandas as pd
import duckdb


def create_compare_table(con, file_path):
    df = pd.read_csv(file_path)

    conditions = []
    for crosswalk_id in df["Crosswalk ID"]:
        center_id = crosswalk_id[-1]
        crosswalk_id = crosswalk_id[:-1]
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


if __name__ == "__main__":
    # Establish a connection to your DuckDB database
    con = duckdb.connect("src/night_light/boston_contrast.db")

    # Specify the path to your CSV file
    file_path = "SVData2-11.csv"
    df = pd.read_csv(file_path)

    # Call the function to filter the data and create the new table
    # create_compare_table(con, file_path)
    # add_perceived_contrast_column(con, df)

    print(df["Perceived Contrast "])
