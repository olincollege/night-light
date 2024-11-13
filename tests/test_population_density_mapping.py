import os
import time

import folium

from night_light.socioeconomic.population_density import get_population_density
from night_light.utils import create_folium_map, open_html_file, Tooltip
from night_light.utils.fips import StateFIPS
from night_light.utils.mapping import Choropleth


def test_population_density_choropleth():
    """Test creating a population density choropleth map."""
    map_filename = "test_population_density_map.html"
    population_density_data = get_population_density(
        year=2021, state=StateFIPS.MASSACHUSETTS
    )

    density_layer = Choropleth(
        geo_data=population_density_data,
        name="Population Density Choropleth",
        data=population_density_data,
        columns=["GEOID", "total_population_density"],
        key_on="feature.properties.GEOID",
    )

    tooltip_layer = folium.GeoJson(
        population_density_data,
        name="Population Density Tooltips",
        style_function=lambda x: {"fillColor": "transparent", "color": "transparent"},
        tooltip=Tooltip(
            fields=["NAMELSAD", "total_population_density"],
            aliases=["Tract Name", "Density"],
        ),
    )

    create_folium_map(
        layers=[density_layer, tooltip_layer],
        center=[42.4072, -71.3824],
        zoom_start=9,
        map_filename=map_filename,
    )

    assert os.path.exists(map_filename)
    open_html_file(map_filename)
    time.sleep(1)
    os.remove(map_filename)
    assert not os.path.exists(map_filename)


def test_senior_population_density_choropleth():
    map_filename = "test_senior_population_density_map.html"
    population_density_data = get_population_density(
        year=2021, state=StateFIPS.MASSACHUSETTS, seniors=True
    )

    density_layer = Choropleth(
        geo_data=population_density_data,
        name="Senior Population Density Choropleth",
        data=population_density_data,
        columns=["GEOID", "senior_population_density"],
        key_on="feature.properties.GEOID",
    )

    tooltip_layer = folium.GeoJson(
        population_density_data,
        name="Senior Population Density Tooltips",
        style_function=lambda x: {"fillColor": "transparent", "color": "transparent"},
        tooltip=Tooltip(
            fields=["NAMELSAD", "senior_population_density"],
            aliases=["Tract Name", "Density"],
        ),
    )

    create_folium_map(
        layers=[density_layer, tooltip_layer],
        center=[42.4072, -71.3824],
        zoom_start=9,
        map_filename=map_filename,
    )

    assert os.path.exists(map_filename)
    open_html_file(map_filename)
    time.sleep(1)
    os.remove(map_filename)
    assert not os.path.exists(map_filename)


def test_youth_population_density_choropleth():
    """Test creating a youth population density choropleth map."""
    map_filename = "test_youth_population_density_map.html"
    population_density_data = get_population_density(
        year=2021, state=StateFIPS.MASSACHUSETTS, youths=True
    )

    density_layer = Choropleth(
        geo_data=population_density_data,
        name="Youth Population Density Choropleth",
        data=population_density_data,
        columns=["GEOID", "youth_population_density"],
        key_on="feature.properties.GEOID",
    )

    tooltip_layer = folium.GeoJson(
        population_density_data,
        name="Youth Population Density Tooltips",
        style_function=lambda x: {"fillColor": "transparent", "color": "transparent"},
        tooltip=Tooltip(
            fields=["NAMELSAD", "youth_population_density"],
            aliases=["Tract Name", "Density"],
        ),
    )

    create_folium_map(
        layers=[density_layer, tooltip_layer],
        center=[42.4072, -71.3824],
        zoom_start=9,
        map_filename=map_filename,
    )

    assert os.path.exists(map_filename)
    open_html_file(map_filename)
    time.sleep(1)
    os.remove(map_filename)
    assert not os.path.exists(map_filename)


def test_disabled_population_density_choropleth():
    """Test creating a disabled population density choropleth map."""
    map_filename = "test_disabled_population_density_map.html"
    population_density_data = get_population_density(
        year=2021, state=StateFIPS.MASSACHUSETTS, disabled=True
    )

    density_layer = Choropleth(
        geo_data=population_density_data,
        name="Disabled Population Density Choropleth",
        data=population_density_data,
        columns=["GEOID", "disabled_population_density"],
        key_on="feature.properties.GEOID",
    )

    tooltip_layer = folium.GeoJson(
        population_density_data,
        name="Disabled Population Density Tooltips",
        style_function=lambda x: {"fillColor": "transparent", "color": "transparent"},
        tooltip=Tooltip(
            fields=["NAMELSAD", "disabled_population_density"],
            aliases=["Tract Name", "Density"],
        ),
    )

    create_folium_map(
        layers=[density_layer, tooltip_layer],
        center=[42.4072, -71.3824],
        zoom_start=9,
        map_filename=map_filename,
    )

    assert os.path.exists(map_filename)
    open_html_file(map_filename)
    time.sleep(1)
    os.remove(map_filename)
    assert not os.path.exists(map_filename)


def test_vulnerable_population_density_choropleth():
    """Test creating a vulnerable population density choropleth map."""
    map_filename = "test_vulnerable_population_density_map.html"
    population_density_data = get_population_density(
        year=2021,
        state=StateFIPS.MASSACHUSETTS,
        seniors=True,
        youths=True,
        disabled=True,
    )
    population_density_data["vulnerable_population_density"] = (
        population_density_data["senior_population_density"]
        + population_density_data["youth_population_density"]
        + population_density_data["disabled_population_density"]
    )
    density_layer = Choropleth(
        geo_data=population_density_data,
        name="Vulnerable Population Density Choropleth",
        data=population_density_data,
        columns=["GEOID", "vulnerable_population_density"],
        key_on="feature.properties.GEOID",
        legend_name="Vulnerable Population Density",
    )

    tooltip_layer = folium.GeoJson(
        population_density_data,
        name="Vulnerable Population Density Tooltips",
        style_function=lambda x: {"fillColor": "transparent", "color": "transparent"},
        tooltip=Tooltip(
            fields=["NAMELSAD", "vulnerable_population_density"],
            aliases=["Tract Name", "Density"],
        ),
    )

    create_folium_map(
        layers=[density_layer, tooltip_layer],
        center=[42.4072, -71.3824],
        zoom_start=9,
        map_filename=map_filename,
    )

    assert os.path.exists(map_filename)
    open_html_file(map_filename)
    time.sleep(1)
    os.remove(map_filename)
    assert not os.path.exists(map_filename)
