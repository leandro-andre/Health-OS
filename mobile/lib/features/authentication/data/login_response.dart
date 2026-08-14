import 'package:health_os/core/session/session.dart';

final class LoginResponse {
  const LoginResponse({required this.accessToken, required this.refreshToken});

  factory LoginResponse.fromJson(Map<String, dynamic> json) {
    final accessToken = json['access_token'];
    final refreshToken = json['refresh_token'];

    if (accessToken is! String || refreshToken is! String) {
      throw const FormatException('Invalid login response payload.');
    }

    return LoginResponse(accessToken: accessToken, refreshToken: refreshToken);
  }

  final String accessToken;
  final String refreshToken;

  Session toSession() {
    return Session(accessToken: accessToken, refreshToken: refreshToken);
  }
}
