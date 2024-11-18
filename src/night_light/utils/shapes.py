from pygris import tracts
from pygris import places

from night_light.utils.fips import StateFIPS


def get_tract_shapes(state: StateFIPS, year: int = 2021):
    """Get tract shapes data"""
    return tracts(state=state.value, cb=True, cache=True, year=year)


def get_place_shapes(state: StateFIPS, year: int = 2021):
    """Get place shapes data"""
    return places(state=state.value, cb=True, cache=True, year=year)
