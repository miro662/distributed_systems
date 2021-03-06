from generated.service_pb2 import ListCitiesMessage, CitiesList, WeatherData
from generated.service_pb2_grpc import WeatherServiceStub
import grpc
import sys
import time
import functools
from typing import Iterable
from pprint import pprint


def connect_to_service(target: str) -> WeatherServiceStub:
    channel = grpc.insecure_channel(target)
    stub = WeatherServiceStub(channel)
    return stub


def list_cities(service: WeatherServiceStub):
    request = ListCitiesMessage()
    cities_list = service.ListCities(request)
    print(", ".join(cities_list.cities))


def subscribe_wrapper(wrapped):
    close_stream = False
    reestablishment_time = 0.25
    while not close_stream:
        try:
            for message in wrapped():
                reestablishment_time = 0.25
                yield message
            close_stream = True
        except KeyboardInterrupt:
            close_stream = True
        except grpc.RpcError as e:
            print(f"connection error, re-establishment attempt in {reestablishment_time}...", file=sys.stderr)
            time.sleep(reestablishment_time)
            reestablishment_time *= 2


def subscribe(service: WeatherServiceStub, cities: Iterable[str]):
    cities_list = CitiesList(cities=cities)
    for message in subscribe_wrapper(functools.partial(service.Subscribe, cities_list)):
        print_message(message)


def print_message(message: WeatherData):
    print(f"city: {message.city}")
    if hasattr(message, "weatherType"):
        print(f"type: {message.weatherType}")
    if hasattr(message, "temperature"):
        print(f"temperature: {message.temperature}")
    if hasattr(message, "humidity"):
        print(f"humidity: {message.humidity}")
    print()


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
