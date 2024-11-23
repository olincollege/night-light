from pygris.data import get_census
from night_light.utils.fips import StateFIPS
from pygris import tracts
import geopandas as gpd


def get_median_household_income(
    year: int = 2021, state: StateFIPS = StateFIPS.MASSACHUSETTS
) -> gpd.GeoDataFrame:
    """
    Fetch median household income data using the ACS 5-year survey.

    Args:
        year (int): The year of the ACS survey.
        state (StateFIPS): The state to fetch data for.

    Returns:
        gpd.GeoDataFrame: A GeoDataFrame containing the median household income data.
    """
    df = get_census(
        year=year,
        variables=["B19013_001E"],
        params={
            "for": "tract:*",
            "in": f"state:{state.value}",
        },
        dataset="acs/acs5",
        return_geoid=True,
        guess_dtypes=True,
    )

    df["median_household_income"] = df["B19013_001E"]
    df.drop(columns=["B19013_001E"], inplace=True)

    gdf = tracts(state=state.value, year=year)
    gdf = gdf.merge(df, on="GEOID")

    return gdf
