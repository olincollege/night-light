import requests

from night_light.utils import query_geojson

BOSTON_STREET_SEGMENTS_API_URL = "https://gisportal.boston.gov/arcgis/rest/services/SAM/Live_SAM_Address/FeatureServer/3/query"
BOSTON_STREET_SEGMENTS_GEOJSON_URL = "https://data.boston.gov/dataset/b9b8b634-f28a-410f-9727-b53d0d006308/resource/e850cfd2-2c6e-4af6-9ac4-e03019412d1e/download/boston_street_segments__sam_system_.geojson"

# MA Road inventory data dictionary for ref:
# https://www.mass.gov/doc/road-inventory-data-dictionary/download

BOSTON_STREET_SEGMENTS_QUERY = {
    "where": "1=1",
    "outFields": "*",
    "outSR": 4326,
    "f": "geojson",
}


def get_boston_street_segments():
    """
    Get Boston street segments data from the API (2000 records/request)
    """
    return query_geojson.fetch_geojson_data(
        url=BOSTON_STREET_SEGMENTS_API_URL, params=BOSTON_STREET_SEGMENTS_QUERY
    )


def save_boston_street_segments_geojson():
    """
    Save Boston street segments data as GeoJSON
    """
    with open("boston_street_segments.geojson", "wb") as geojson:
        geojson.write(requests.get(BOSTON_STREET_SEGMENTS_GEOJSON_URL).content)


if __name__ == "__main__":
    save_boston_street_segments_geojson()
