from generated.service_pb2 import ListCitiesMessage, CitiesList
from generated.service_pb2_grpc import WeatherServiceStub
import grpc
import sys
from typing import Iterable
from pprint import pprint


def connect_to_service(target: str) -> WeatherServiceStub:
    channel = grpc.insecure_channel("localhost:8080")
    stub = WeatherServiceStub(channel)
    return stub


def list_cities(service: WeatherServiceStub):
    request = ListCitiesMessage()
    cities_list = service.ListCities(request)
    print(", ".join(cities_list.cities))


def subscribe(service: WeatherServiceStub, cities: Iterable[str]):
    cities_list = CitiesList(cities=cities)

    for message in service.Subscribe(cities_list):
        pprint(message)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(
            f"usage: {sys.argv[0]} target list / {sys.argv[0]} target subscribe cities"
        )
        exit(1)

    service = connect_to_service(sys.argv[1])

    command = sys.argv[2]
    if command == "list":
        list_cities(service)
    elif command == "subscribe":
        subscribe(service, sys.argv[3:])
