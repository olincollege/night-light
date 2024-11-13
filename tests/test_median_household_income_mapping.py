import os
import time

import folium

from night_light.socioeconomic.median_household_income import (
    get_median_household_income,
)
from night_light.utils import create_folium_map, open_html_file, Tooltip
from night_light.utils.fips import StateFIPS
from night_light.utils.mapping import Choropleth


def test_ma_median_household_income_choropleth():
    """Test creating MA median household income choropleth map."""
    map_filename = "test_ma_median_household_income_map.html"
    median_income_data = get_median_household_income(
        year=2021, state=StateFIPS.MASSACHUSETTS
    )
    median_income_data = median_income_data.dropna(subset=["median_household_income"])

    income_layer = Choropleth(
        geo_data=median_income_data,
        name="Median Household Income Choropleth",
        data=median_income_data,
        columns=["GEOID", "median_household_income"],
        key_on="feature.properties.GEOID",
    )

    tooltip_layer = folium.GeoJson(
        median_income_data,
        name="Median Household Income Tooltips",
        style_function=lambda x: {"fillColor": "transparent", "color": "transparent"},
        tooltip=Tooltip(
            fields=["NAMELSAD", "median_household_income"],
            aliases=["Tract Name", "Median Household Income"],
        ),
    )

    create_folium_map(
        layers=[income_layer, tooltip_layer],
        center=[42.4072, -71.3824],
        zoom_start=9,
        map_filename=map_filename,
    )

    assert os.path.exists(map_filename)
    open_html_file(map_filename)
    time.sleep(1)
    os.remove(map_filename)
    assert not os.path.exists(map_filename)
