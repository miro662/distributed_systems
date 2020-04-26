from generated.service_pb2 import ListCitiesMessage
from generated.service_pb2_grpc import WeatherServiceStub
import grpc
from pprint import pprint


if __name__ == "__main__":
    channel = grpc.insecure_channel("localhost:8080")
    stub = WeatherServiceStub(channel)

    request = ListCitiesMessage()
    cities_list = stub.ListCities(request)
    pprint(cities_list)
