import os
import time

from night_light.crosswalks import create_map
from test.conftest import BOSTON_CENTER_COORD


def open_html_file(file_path: str | os.PathLike[str]):
    file_path = os.path.abspath(file_path)

    if os.name == "posix":
        os.system(
            f"open '{file_path}'"
            if "Darwin" in os.uname().sysname
            else f"xdg-open '{file_path}'"
        )
    elif os.name == "nt":
        os.system(f"start {file_path}")
    else:
        print("Unsupported operating system")


def test_boston_crosswalk_map(boston_crosswalk):
    """Test creating a map of the Boston crosswalk"""
    map_filename = "test_boston_crosswalk.html"
    create_map.create_folium_map(
        gdf=boston_crosswalk,
        zoom_start=12,
        center=BOSTON_CENTER_COORD,
        map_filename=map_filename,
    )
    assert os.path.exists(map_filename)
    open_html_file(map_filename)
    time.sleep(1)
    os.remove(map_filename)
    assert not os.path.exists(map_filename)
