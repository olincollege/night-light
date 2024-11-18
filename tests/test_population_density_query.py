import os

from night_light.socioeconomic.population_density import get_population_density
from night_light.utils import query_geojson
from night_light.utils.fips import StateFIPS


def test_population_density_query():
    """Test querying population density data."""
    data = get_population_density(year=2021, state=StateFIPS.MASSACHUSETTS)
    assert not data.empty
    assert "GEOID" in data.columns
    assert "area_km2" in data.columns
    assert "total_population_density" in data.columns
    assert "senior_population_density" not in data.columns
    assert "youth_population_density" not in data.columns
    assert "disabled_population_density" not in data.columns


def test_senior_population_density_query():
    """Test querying senior population density data."""
    data = get_population_density(
        year=2021, state=StateFIPS.MASSACHUSETTS, seniors=True
    )
    assert not data.empty
    assert "GEOID" in data.columns
    assert "area_km2" in data.columns
    assert "total_population_density" in data.columns
    assert "senior_population_density" in data.columns
    assert "youth_population_density" not in data.columns
    assert "disabled_population_density" not in data.columns


def test_youth_population_density_query():
    """Test querying youth population density data."""
    data = get_population_density(year=2021, state=StateFIPS.MASSACHUSETTS, youths=True)
    assert not data.empty
    assert "GEOID" in data.columns
    assert "area_km2" in data.columns
    assert "total_population_density" in data.columns
    assert "senior_population_density" not in data.columns
    assert "youth_population_density" in data.columns
    assert "disabled_population_density" not in data.columns


def test_disabled_population_density_query():
    """Test querying disabled population density data."""
    data = get_population_density(
        year=2021, state=StateFIPS.MASSACHUSETTS, disabled=True
    )
    assert not data.empty
    assert "GEOID" in data.columns
    assert "area_km2" in data.columns
    assert "total_population_density" in data.columns
    assert "senior_population_density" not in data.columns
    assert "youth_population_density" not in data.columns
    assert "disabled_population_density" in data.columns


def test_all_population_density_query():
    """Test querying all population density data."""
    data = get_population_density(
        year=2021,
        state=StateFIPS.MASSACHUSETTS,
        seniors=True,
        youths=True,
        disabled=True,
    )
    assert not data.empty
    assert "GEOID" in data.columns
    assert "area_km2" in data.columns
    assert "total_population_density" in data.columns
    assert "senior_population_density" in data.columns
    assert "youth_population_density" in data.columns
    assert "disabled_population_density" in data.columns


def test_all_population_density_geojson():
    """Test saving all population density to a GeoJSON file"""
    data = get_population_density(
        year=2021,
        state=StateFIPS.MASSACHUSETTS,
        seniors=True,
        youths=True,
        disabled=True,
    )
    geojson_filename = "test_all_population_density.geojson"
    query_geojson.save_geojson(data, geojson_filename)
    saved_gdf = query_geojson.gpd.read_file(geojson_filename)

    assert data.crs == saved_gdf.crs
    assert set(data.columns) == set(saved_gdf.columns)
    assert data.index.equals(saved_gdf.index)
    assert data.shape == saved_gdf.shape

    os.remove(geojson_filename)
    assert not os.path.exists(geojson_filename)
