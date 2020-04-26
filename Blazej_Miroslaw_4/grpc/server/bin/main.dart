import 'dart:async';

import 'package:grpc/src/server/call.dart';
import 'package:rxdart/streams.dart';
import 'package:server/generated/service.pbgrpc.dart';
import 'package:grpc/grpc.dart' as grpc;

class WeatherService extends WeatherServiceBase {
  final World world;
  final Stream eventsStream;

  WeatherService(World world):
    world = world,
    eventsStream = world.weatherChangesStream.asBroadcastStream(),
    super();

  @override
  Future<CitiesList> listCities(ServiceCall call, ListCitiesMessage request) {
    var response = CitiesList();
    response.cities.addAll(world.cityNames);
    return Future.value(response);
  }

  @override
  Stream<WeatherData> subscribe(ServiceCall call, CitiesList request) {
    return eventsStream.where(
      (change) => request.cities.contains(change.city)
    );
  }
}

class World {
  final List<City> cities;

  World(this.cities);

  Iterable<String> get cityNames => cities.map((city) => city.name);

  Stream<WeatherData> get weatherChangesStream => MergeStream(
    cities.map((city) => city.weatherChangesStream)
  );
}

class City {
  final String name;
  WeatherData _weatherData;

  final StreamController<WeatherData> weatherChangesStreamController = StreamController<WeatherData>();

  City(this.name);

  Stream<WeatherData> get weatherChangesStream => weatherChangesStreamController.stream;

  WeatherData get weatherData => _weatherData;
  set weatherData(WeatherData data) {
    _weatherData = data;

    var changedData = data.clone();
    changedData.city = name;
    weatherChangesStreamController.add(changedData);
  }
}

Future<void> main(List<String> args) async {
  final krk = City('Kraków');
  final world = World([
    krk,
    City('Warszawa'),
    City('Poznań')
  ]);

  final server = grpc.Server([WeatherService(world)]);
  await server.serve(port: 8080);
  Future.delayed(Duration(seconds: 15), () {
    krk.weatherData = WeatherData()
      ..weatherType = WeatherType.CLEAR
      ..temperature = 15.0
      ..humidity = 10.0;
  });
  print('Server listening...');
}
