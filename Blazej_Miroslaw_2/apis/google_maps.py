import json

import urllib3

from apis.keys import GOOGLE_MAPS_API_KEY

GOOGLE_MAPS_GEOCODING_URL = (
    f"https://maps.googleapis.com/maps/api/geocode/json?&key={GOOGLE_MAPS_API_KEY}"
)


def get_country_by_geocode(address: str) -> str:
    return _get_country_from_geocode(f"&address={address}")


def get_country_by_reverse_geocode(lat: float, lng: float) -> str:
    return _get_country_from_geocode(f"&latlng={lat},{lng}")


def _get_country_from_geocode(params: str) -> str:
    http = urllib3.PoolManager()
    google_maps_response = http.request("GET", GOOGLE_MAPS_GEOCODING_URL + params)
    response_json = json.loads(google_maps_response.data)
    address_components = response_json["results"][0]["address_components"]
    country_component = next(
        component for component in address_components if "country" in component["types"]
    )
    return country_component["long_name"]
