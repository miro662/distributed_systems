import 'dart:async';
import 'dart:io';
import 'dart:convert';

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

  City operator[](String cityName) => cities.where((city) => city.name == cityName).first;
}

class City {
  final String name;
  WeatherData _weatherData = WeatherData();

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

void handleCommand(String command, World world) {
  final splitCommand = command.trimRight().split(' ');
  final commandName = splitCommand[0];

  if (commandName == 'help') {
    print('Available commands:');
    print('help - prints this message');
    print('cities - prints available cities');
    print('alter <city_name> <param> <value> - change params in city');
  } else if (commandName == 'alter') {
    if (splitCommand.length != 4) {
      print('insufficient parameters');
      return;
    }

    final cityName = splitCommand[1];
    if (!world.cityNames.contains(cityName)) {
      print('City $cityName does not exist');
      return;
    }
    final city = world[cityName];

    final paramName = splitCommand[2];
    final paramValue = splitCommand[3];

    var weatherData = city.weatherData;
    if (paramName == 'temperature') {
      var newTemperature = double.tryParse(paramValue);
      if (newTemperature == null) {
        print('Invalid temperature value');
        return;
      }
      weatherData.temperature = newTemperature;
      city.weatherData = weatherData;
    } else if (paramName == 'humidity') {
      var newHumidity = double.tryParse(paramValue);
      if (newHumidity == null) {
        print('Invalid humidity value');
        return;
      }
      weatherData.humidity = newHumidity;
      city.weatherData = weatherData;
    } else if (paramName == 'type') {
      switch (paramValue) {
        case 'clear':
          weatherData.weatherType = WeatherType.CLEAR;
          break;
        case 'cloudy':
          weatherData.weatherType = WeatherType.CLOUDY;
          break;
        case 'rain':
          weatherData.weatherType = WeatherType.RAIN;
          break;
        case 'thunderstorm':
          weatherData.weatherType = WeatherType.THUNDERSTORM;
          break;
        default:
          print('Unsupported type $paramValue, supported: clear/cloudy/rain/thunderstorm');
          return;
      }
      city.weatherData = weatherData;
    } else {
      print('Unknown param: $paramName, supported: type/temperature/humidity');
    }
  } else {
    print('Unsupported command: $commandName');
  }
} 

Future<void> main(List<String> args) async {
  final world = World([
    City('Kraków'),
    City('Warszawa'),
    City('Poznań'),
    City('Wrocław'),
    City('Łódź'),
    City('Gdańsk'),
  ]);

  final server = grpc.Server([WeatherService(world)]);
  await Future.wait([
    server.serve(port: 8080),
    stdin.map((x) => handleCommand(utf8.decode(x), world)).drain()
  ]);
  // Future.delayed(Duration(seconds: 15), () {
  //   world['Kraków'].weatherData = WeatherData()
  //     ..weatherType = WeatherType.CLEAR
  //     ..temperature = 15.0
  //     ..humidity = 10.0;
  // });
  print('Server listening...');
}
