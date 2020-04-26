import 'package:grpc/src/server/call.dart';
import 'package:server/generated/service.pbgrpc.dart';
import 'package:grpc/grpc.dart' as grpc;

class WeatherService extends WeatherServiceBase {
  @override
  Future<CitiesList> listCities(ServiceCall call, ListCitiesMessage request) {
    var response = CitiesList();
    response.cities.add('Kraków');
    return Future.value(response);
  }

  @override
  Stream<WeatherData> subscribe(ServiceCall call, CitiesList request) {
    // TODO: implement subscribe
    return null;
  }
  
}

Future<void> main(List<String> args) async {
  final server = grpc.Server([WeatherService()]);
  await server.serve(port: 8080);
  print('Server listening...');
}
