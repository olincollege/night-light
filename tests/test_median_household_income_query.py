import os
from night_light.socioeconomic.median_household_income import (
    get_median_household_income,
)
from night_light.utils import query_geojson
from night_light.utils.fips import StateFIPS


def test_get_ma_median_household_income():
    """Test getting MA median household income"""
    data = get_median_household_income(state=StateFIPS.MASSACHUSETTS)
    assert data.shape[0] > 0
    assert "median_household_income" in data.columns
    data = data.dropna(subset=["median_household_income"])
    invalid_values = data[data["median_household_income"] < 0]
    assert invalid_values.empty


def test_ma_median_household_geojson():
    """Test saving MA median household income to a GeoJSON file"""
    data = get_median_household_income(state=StateFIPS.MASSACHUSETTS)
    geojson_filename = "test_ma_median_household_income.geojson"
    query_geojson.save_geojson(data, geojson_filename)
    saved_gdf = query_geojson.gpd.read_file(geojson_filename)

    assert data.crs == saved_gdf.crs
    assert set(data.columns) == set(saved_gdf.columns)
    assert data.index.equals(saved_gdf.index)
    assert data.shape == saved_gdf.shape

    os.remove(geojson_filename)
    assert not os.path.exists(geojson_filename)
