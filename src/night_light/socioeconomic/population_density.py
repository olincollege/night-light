from night_light.socioeconomic.population import get_population
from night_light.utils.fips import StateFIPS
from night_light.utils.shapes import get_tract_shapes


def get_population_density(
    year: int = 2021, state: StateFIPS = StateFIPS.MASSACHUSETTS, **kwargs
):
    """
    Calculate population density using ACS 5-year survey data.

    This function retrieves population data and geographic shapes for census tracts
    within the specified state, calculates the area of each tract, and computes
    population density. Additional segments of the population (seniors, youths, and
    disabled individuals) can be included if specified, providing corresponding density
    values.

    Args:
        year (int, optional): The year for which to fetch the population data. Defaults
            to 2021.
        state (StateFIPS, optional): The state for which to calculate population
            density, specified using FIPS code Enum. Defaults to
            `StateFIPS.MASSACHUSETTS`.

    Keyword Args:
        seniors (bool, optional): If True, includes senior population density (ages
            65+).
        youths (bool, optional): If True, includes youth population density (ages 0-17).
        disabled (bool, optional): If True, includes disabled population density.

    Returns:
        gpd.GeoDataFrame: A GeoDataFrame containing population density data by census
        tract, with columns for:
            - "GEOID"
            - "area_km2"
            - "total_population_density"
            - "senior_population_density" (if seniors=True)
            - "youth_population_density" (if youths=True)
            - "disabled_population_density" (if disabled=True)
    """
    df_pop = get_population(year, state, **kwargs)
    tract_shapes = get_tract_shapes(state)
    tract_shapes.to_crs("EPSG:3857", inplace=True)
    tract_shapes["area_km2"] = tract_shapes.area / 1e6

    df_pop_density = tract_shapes.merge(df_pop, how="inner", on="GEOID")
    if kwargs.get("seniors"):
        df_pop_density["senior_population_density"] = (
            df_pop_density["senior_population"] / tract_shapes["area_km2"]
        )

    if kwargs.get("youths"):
        df_pop_density["youth_population_density"] = (
            df_pop_density["youth_population"] / tract_shapes["area_km2"]
        )

    if kwargs.get("disabled"):
        df_pop_density["disabled_population_density"] = (
            df_pop_density["disabled_population"] / tract_shapes["area_km2"]
        )

    df_pop_density["total_population_density"] = (
        df_pop_density["total_population"] / tract_shapes["area_km2"]
    )

    return df_pop_density.to_crs("EPSG:4326")
