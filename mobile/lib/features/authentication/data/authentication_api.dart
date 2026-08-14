import 'package:health_os/core/networking/api_client.dart';
import 'package:health_os/core/networking/api_result.dart';
import 'package:health_os/features/authentication/data/login_request.dart';
import 'package:health_os/features/authentication/data/login_response.dart';
import 'package:health_os/features/authentication/data/register_user_request.dart';
import 'package:health_os/features/authentication/data/register_user_response.dart';

class AuthenticationApi {
  const AuthenticationApi(this._apiClient);

  final ApiClient _apiClient;

  Future<AuthenticationApiResult> login(LoginRequest request) async {
    final result = await _apiClient.post(
      '/api/v1/auth/login/',
      data: request.toJson(),
    );

    return switch (result) {
      ApiSuccess(:final data) => _toLoginResponse(data),
      ApiFailure(:final error) => AuthenticationApiFailure(_toError(error)),
    };
  }

  Future<RegisterUserApiResult> register(RegisterUserRequest request) async {
    final result = await _apiClient.post(
      '/api/v1/users/',
      data: request.toJson(),
    );

    return switch (result) {
      ApiSuccess(:final data) => _toRegisterUserResponse(data),
      ApiFailure(:final error) => RegisterUserApiFailure(_toError(error)),
    };
  }

  AuthenticationApiResult _toLoginResponse(Object? data) {
    if (data is! Map<String, dynamic>) {
      return const AuthenticationApiFailure(AuthenticationErrorType.unexpected);
    }

    try {
      return AuthenticationApiSuccess(LoginResponse.fromJson(data));
    } on FormatException {
      return const AuthenticationApiFailure(AuthenticationErrorType.unexpected);
    }
  }

  RegisterUserApiResult _toRegisterUserResponse(Object? data) {
    if (data is! Map<String, dynamic>) {
      return const RegisterUserApiFailure(AuthenticationErrorType.unexpected);
    }

    try {
      return RegisterUserApiSuccess(RegisterUserResponse.fromJson(data));
    } on FormatException {
      return const RegisterUserApiFailure(AuthenticationErrorType.unexpected);
    }
  }

  AuthenticationErrorType _toError(ApiError error) {
    return switch (error.type) {
      ApiErrorType.connection => AuthenticationErrorType.network,
      ApiErrorType.timeout => AuthenticationErrorType.timeout,
      ApiErrorType.unexpectedPayload => AuthenticationErrorType.unexpected,
      ApiErrorType.http => switch (error.statusCode) {
        400 => AuthenticationErrorType.invalidInput,
        401 => AuthenticationErrorType.invalidCredentials,
        409 => AuthenticationErrorType.userAlreadyExists,
        _ => AuthenticationErrorType.unexpected,
      },
    };
  }
}

enum AuthenticationErrorType {
  invalidCredentials,
  invalidInput,
  userAlreadyExists,
  network,
  timeout,
  unexpected,
}

sealed class AuthenticationApiResult {
  const AuthenticationApiResult();
}

final class AuthenticationApiSuccess extends AuthenticationApiResult {
  const AuthenticationApiSuccess(this.response);

  final LoginResponse response;
}

final class AuthenticationApiFailure extends AuthenticationApiResult {
  const AuthenticationApiFailure(this.errorType);

  final AuthenticationErrorType errorType;
}

sealed class RegisterUserApiResult {
  const RegisterUserApiResult();
}

final class RegisterUserApiSuccess extends RegisterUserApiResult {
  const RegisterUserApiSuccess(this.response);

  final RegisterUserResponse response;
}

final class RegisterUserApiFailure extends RegisterUserApiResult {
  const RegisterUserApiFailure(this.errorType);

  final AuthenticationErrorType errorType;
}
