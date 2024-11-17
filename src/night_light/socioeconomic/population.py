from pygris.data import get_census
from night_light.utils.fips import StateFIPS


def get_population(
    year: int = 2021, state: StateFIPS = StateFIPS.MASSACHUSETTS, **kwargs
):
    """
    Fetch population data for a given year and state using the ACS 5-year survey.

    This function retrieves population data for a specific state and year from the
    American Community Survey (ACS) 5-year dataset. It allows for additional filtering
    by specific population segments, including seniors, youths, and disabled
    individuals, if specified in the keyword arguments.

    Args:
        year (int, optional): The year for which to fetch the data. Defaults to 2021.
        state (StateFIPS, optional): The state for which to fetch the data, using FIPS
            code Enum. Defaults to StateFIPS.MASSACHUSETTS.

    Keyword Args:
        seniors (bool, optional): If True, fetches the senior population (ages 65+).
        youths (bool, optional): If True, fetches the youth population (ages 0-17).
        disabled (bool, optional): If True, fetches the disabled population.

    Returns:
        pd.DataFrame: A DataFrame containing the population data by census tract,
        with columns for:
            - "GEOID"
            - "total_population"
            - "senior_population" (if seniors=True)
            - "youth_population" (if youths=True)
            - "disabled_population" (if disabled=True)
    """
    seniors = kwargs.pop("seniors", False)
    youths = kwargs.pop("youths", False)
    disabled = kwargs.pop("disabled", False)
    variables = ["B01003_001E"]
    if seniors:
        variables.extend(
            [
                "B01001_020E",
                "B01001_021E",
                "B01001_022E",
                "B01001_023E",
                "B01001_024E",
                "B01001_025E",
                "B01001_044E",
                "B01001_045E",
                "B01001_046E",
                "B01001_047E",
                "B01001_048E",
                "B01001_049E",
            ]
        )
    if youths:
        variables.extend(
            [
                "B01001_003E",
                "B01001_004E",
                "B01001_005E",
                "B01001_006E",
                "B01001_027E",
                "B01001_028E",
                "B01001_029E",
                "B01001_030E",
            ]
        )

    if disabled:
        variables.append("B18101_001E")

    df = get_census(
        year=year,
        variables=variables,
        params={
            "for": "tract:*",
            "in": f"state:{state.value}",
        },
        dataset="acs/acs5",
        return_geoid=True,
        guess_dtypes=True,
    )

    df["total_population"] = df["B01003_001E"]
    df.drop(columns=["B01003_001E"], inplace=True)
    if seniors:
        df["senior_population"] = (
            df["B01001_020E"]
            + df["B01001_021E"]
            + df["B01001_022E"]
            + df["B01001_023E"]
            + df["B01001_024E"]
            + df["B01001_025E"]
            + df["B01001_044E"]
            + df["B01001_045E"]
            + df["B01001_046E"]
            + df["B01001_047E"]
            + df["B01001_048E"]
            + df["B01001_049E"]
        )
        df.drop(
            columns=[
                "B01001_020E",
                "B01001_021E",
                "B01001_022E",
                "B01001_023E",
                "B01001_024E",
                "B01001_025E",
                "B01001_044E",
                "B01001_045E",
                "B01001_046E",
                "B01001_047E",
                "B01001_048E",
                "B01001_049E",
            ],
            inplace=True,
        )
    if youths:
        df["youth_population"] = (
            df["B01001_003E"]
            + df["B01001_004E"]
            + df["B01001_005E"]
            + df["B01001_006E"]
            + df["B01001_027E"]
            + df["B01001_028E"]
            + df["B01001_029E"]
            + df["B01001_030E"]
        )
        df.drop(
            columns=[
                "B01001_003E",
                "B01001_004E",
                "B01001_005E",
                "B01001_006E",
                "B01001_027E",
                "B01001_028E",
                "B01001_029E",
                "B01001_030E",
            ],
            inplace=True,
        )
    if disabled:
        df["disabled_population"] = df["B18101_001E"]
        df.drop(columns=["B18101_001E"], inplace=True)

    return df
