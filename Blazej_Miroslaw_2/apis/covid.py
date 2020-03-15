import json
from dataclasses import dataclass
from functools import reduce
from pprint import pprint
from typing import Iterable, Dict

import urllib3


@dataclass
class CovidData:
    cases: int
    deaths: int
    recovered: int

    @classmethod
    def from_api_data(cls, api_data: Dict) -> 'CovidData':
        return CovidData(
            cases=api_data['cases'],
            deaths=api_data['deaths'],
            recovered=api_data['recovered']
        )

    @property
    def mortality(self):
        return self.deaths / self.cases

    @property
    def recoverability(self):
        return self.recovered / self.cases


ALL_ENDPOINT_URL = "https://coronavirus-19-api.herokuapp.com/all"
COUNTRIES_ENDPOINT_URL = "https://coronavirus-19-api.herokuapp.com/countries"


def get_countries() -> Iterable[str]:
    """ Retrieves list of available countries
    :return: List of countries
    """

    json_data = _get_covid_countries_data()
    return (country_data['country'] for country_data in json_data)


def get_data_in_country(country_name: str) -> CovidData or None:
    """ Retrieves data for given country
    :param country_name: Name of country
    :return: CovidData for this country if exists or None if it does not exist
    """
    json_data = _get_covid_countries_data()
    json_data_in_countries = (
        country_data for country_data in json_data
        if country_data['country'] == country_name
    )
    try:
        json_data_in_country = next(json_data_in_countries)
    except StopIteration:
        return None
    return CovidData.from_api_data(json_data_in_country)


def get_world_data_from_countries_endpoint() -> CovidData:
    """ Retrieves data for all countries by adding per-country data
    :return: Data for all countries
    """
    def sum_covid_data(lhs: CovidData, rhs: CovidData) -> CovidData:
        return CovidData(
            cases=lhs.cases+rhs.cases,
            deaths=lhs.deaths+rhs.deaths,
            recovered=lhs.recovered+rhs.recovered
        )

    json_data = _get_covid_countries_data()
    covid_data = (CovidData.from_api_data(country_data) for country_data in json_data)
    total_data = reduce(sum_covid_data, covid_data, CovidData(cases=0, deaths=0, recovered=0))
    return total_data


def get_world_data_from_all_endpoint() -> CovidData:
    """ Retrieves data for all countries by using all countries endpoint
    :return: Data for all countries
    """
    json_data = _get_covid_all_data()
    return CovidData.from_api_data(json_data)


def _get_covid_countries_data():
    return __get_json_data(COUNTRIES_ENDPOINT_URL)


def _get_covid_all_data():
    return __get_json_data(ALL_ENDPOINT_URL)


def __get_json_data(url: str):
    http = urllib3.PoolManager()
    r = http.request("GET", url)
    data = r.data
    json_data = json.loads(data)
    return json_data


if __name__ == '__main__':
    pprint(get_world_data_from_countries_endpoint())
    pprint(get_world_data_from_all_endpoint())
    pprint(get_world_data_from_countries_endpoint() == get_world_data_from_all_endpoint())

