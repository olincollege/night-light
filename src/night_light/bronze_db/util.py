import os
import duckdb
import geopandas as gpd
from geopandas import GeoDataFrame
from typing import List, Tuple, Union


def connect_to_duckdb(db_path: str) -> duckdb.DuckDBPyConnection:
    """
    Establish a connection to a DuckDB database and load the spatial extension.

    Args:
        db_path (str): Path to the DuckDB database file.

    Returns:
        duckdb.DuckDBPyConnection: Connection to the DuckDB database.
    """
    con = duckdb.connect(db_path)
    is_spatial_installed = con.execute(
        """SELECT EXISTS (
        SELECT 1
        FROM duckdb_extensions()
        WHERE extension_name = 'spatial' AND installed
        )
        """
    ).fetchone()[0]
    if not is_spatial_installed:
        con.install_extension("spatial")
    con.load_extension("spatial")
    return con


def query_table_to_gdf(
    con: duckdb.DuckDBPyConnection,
    table_name: str,
    query: str = None,
) -> GeoDataFrame:
    """
    Query a DuckDB table and return the results as a GeoPandas DataFrame.

    Args:
        con (duckdb.DuckDBPyConnection): Connection to the DuckDB database.
        table_name (str): Name of the table to query.
        query (Optional[str]): SQL query to execute. Default is to fetch the first 10 rows.

    Returns:
        GeoDataFrame: Results of the query.
    """
    if query is None:
        query = "SELECT * FROM {table_name} LIMIT 10".format(table_name=table_name)
    df = con.execute(query).fetchdf()
    df["geometry"] = gpd.GeoSeries.from_wkt(df["geometry"])
    gdf = gpd.GeoDataFrame(df)
    return gdf


def load_data_to_table(
    con: duckdb.DuckDBPyConnection,
    data_source: Union[str, GeoDataFrame],
    table_name: str,
) -> None:
    """
    Load GeoJSON or GeoDataFrame into DuckDB.

    Args:
        con (duckdb.DuckDBPyConnection): Connection to the DuckDB database.
        data_source (Union[str, GeoDataFrame]): Path to a GeoJSON file or a
            GeoDataFrame.
        table_name (str): Name of the target table.
    """
    if con.execute(
        f"SELECT 1 FROM information_schema.tables WHERE table_name = '{table_name}'"
    ).fetchone():
        print(f"Table '{table_name}' already exists. Skipping data load.")
        return

    gdf = (
        gpd.read_file(data_source)
        if isinstance(data_source, str) and os.path.isfile(data_source)
        else data_source
    )
    if not isinstance(gdf, gpd.GeoDataFrame):
        raise ValueError("data_source must be a valid GeoJSON file path or GeoDataFrame.")

    # Convert geometry to WKT and ensure compatibility with DuckDB
    if "geometry" in gdf:
        gdf["geometry"] = gdf["geometry"].to_wkt()
    gdf = gdf.astype({col: "string" for col in gdf.select_dtypes("object").columns})

    con.register("temp_gdf", gdf)
    con.execute(f"CREATE TABLE {table_name} AS SELECT * FROM temp_gdf")


def load_multiple_datasets(
    con: duckdb.DuckDBPyConnection, datasets: List[Tuple[Union[str, GeoDataFrame], str]]
) -> None:
    """
    Load multiple GeoJSON files or GeoDataFrames into DuckDB.

    Args:
        con (duckdb.DuckDBPyConnection): Connection to the DuckDB database.
        datasets (List[Tuple[Union[str, GeoDataFrame], str]]): List of tuples where
            each tuple contains:
            - data_source (Union[str, GeoDataFrame]): Path to a GeoJSON file or a
                GeoDataFrame.
            - table_name (str): Name of the target table.
    """
    for data_source, table_name in datasets:
        load_data_to_table(con, data_source, table_name)
