import 'dart:convert';
import 'dart:typed_data';

import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:health_os/core/networking/api_client.dart';
import 'package:health_os/core/networking/api_config.dart';
import 'package:health_os/features/authentication/data/authentication_api.dart';
import 'package:health_os/features/authentication/data/login_request.dart';
import 'package:health_os/features/authentication/data/register_user_request.dart';

void main() {
  test('valid login calls expected endpoint with email and password', () async {
    final adapter = _FakeAdapter(
      response: _JsonResponse(200, {
        'access_token': 'access-token',
        'refresh_token': 'refresh-token',
      }),
    );
    final api = _api(adapter);

    await api.login(
      const LoginRequest(email: 'leo@example.com', password: 'fake-secret'),
    );

    expect(adapter.lastOptions?.method, 'POST');
    expect(adapter.lastOptions?.path, '/api/v1/auth/login/');
    expect(adapter.lastBody, {
      'email': 'leo@example.com',
      'password': 'fake-secret',
    });
  });

  test('login response generates Session', () async {
    final api = _api(
      _FakeAdapter(
        response: _JsonResponse(200, {
          'access_token': 'access-token',
          'refresh_token': 'refresh-token',
        }),
      ),
    );

    final result = await api.login(
      const LoginRequest(email: 'leo@example.com', password: 'fake-secret'),
    );

    expect(result, isA<AuthenticationApiSuccess>());
    final success = result as AuthenticationApiSuccess;
    final session = success.response.toSession();
    expect(session.accessToken, 'access-token');
    expect(session.refreshToken, 'refresh-token');
  });

  test('401 maps to invalid credentials', () async {
    final api = _api(_FakeAdapter(response: _JsonResponse(401, {})));

    final result = await api.login(
      const LoginRequest(email: 'leo@example.com', password: 'wrong-secret'),
    );

    expect(result, isA<AuthenticationApiFailure>());
    expect(
      (result as AuthenticationApiFailure).errorType,
      AuthenticationErrorType.invalidCredentials,
    );
  });

  test('400 maps to invalid input', () async {
    final api = _api(_FakeAdapter(response: _JsonResponse(400, {})));

    final result = await api.login(
      const LoginRequest(email: 'leo@example.com', password: ''),
    );

    expect(
      (result as AuthenticationApiFailure).errorType,
      AuthenticationErrorType.invalidInput,
    );
  });

  test('network failure is mapped', () async {
    final api = _api(
      _FakeAdapter(
        exceptionBuilder: (options) => DioException.connectionError(
          requestOptions: options,
          reason: 'offline',
        ),
      ),
    );

    final result = await api.login(
      const LoginRequest(email: 'leo@example.com', password: 'fake-secret'),
    );

    expect(
      (result as AuthenticationApiFailure).errorType,
      AuthenticationErrorType.network,
    );
  });

  test('timeout is mapped', () async {
    final api = _api(
      _FakeAdapter(
        exceptionBuilder: (options) => DioException.connectionTimeout(
          timeout: const Duration(seconds: 10),
          requestOptions: options,
        ),
      ),
    );

    final result = await api.login(
      const LoginRequest(email: 'leo@example.com', password: 'fake-secret'),
    );

    expect(
      (result as AuthenticationApiFailure).errorType,
      AuthenticationErrorType.timeout,
    );
  });

  test('registration calls expected endpoint with full_name', () async {
    final adapter = _FakeAdapter(
      response: _JsonResponse(201, {
        'user_id': 'user-id',
        'email': 'leo@example.com',
        'full_name': 'Leandro Andre',
      }),
    );
    final api = _api(adapter);

    await api.register(
      const RegisterUserRequest(
        email: 'leo@example.com',
        fullName: 'Leandro Andre',
        password: 'fake-secret',
      ),
    );

    expect(adapter.lastOptions?.method, 'POST');
    expect(adapter.lastOptions?.path, '/api/v1/users/');
    expect(adapter.lastBody, {
      'email': 'leo@example.com',
      'full_name': 'Leandro Andre',
      'password': 'fake-secret',
    });
    expect(
      (adapter.lastBody as Map<String, dynamic>),
      isNot(contains('passwordConfirmation')),
    );
  });

  test('201 registration creates success response', () async {
    final api = _api(
      _FakeAdapter(
        response: _JsonResponse(201, {
          'user_id': 'user-id',
          'email': 'leo@example.com',
          'full_name': 'Leandro Andre',
        }),
      ),
    );

    final result = await api.register(
      const RegisterUserRequest(
        email: 'leo@example.com',
        fullName: 'Leandro Andre',
        password: 'fake-secret',
      ),
    );

    expect(result, isA<RegisterUserApiSuccess>());
    final success = result as RegisterUserApiSuccess;
    expect(success.response.userId, 'user-id');
    expect(success.response.email, 'leo@example.com');
    expect(success.response.fullName, 'Leandro Andre');
  });

  test('409 registration maps to user already exists', () async {
    final api = _api(
      _FakeAdapter(
        response: _JsonResponse(409, {'code': 'user_already_exists'}),
      ),
    );

    final result = await api.register(
      const RegisterUserRequest(
        email: 'leo@example.com',
        fullName: 'Leandro Andre',
        password: 'fake-secret',
      ),
    );

    expect(
      (result as RegisterUserApiFailure).errorType,
      AuthenticationErrorType.userAlreadyExists,
    );
  });

  test('400 registration maps to invalid input', () async {
    final api = _api(_FakeAdapter(response: _JsonResponse(400, {})));

    final result = await api.register(
      const RegisterUserRequest(email: 'invalid', fullName: '', password: ''),
    );

    expect(
      (result as RegisterUserApiFailure).errorType,
      AuthenticationErrorType.invalidInput,
    );
  });

  test('registration network failure is mapped', () async {
    final api = _api(
      _FakeAdapter(
        exceptionBuilder: (options) => DioException.connectionError(
          requestOptions: options,
          reason: 'offline',
        ),
      ),
    );

    final result = await api.register(
      const RegisterUserRequest(
        email: 'leo@example.com',
        fullName: 'Leandro Andre',
        password: 'fake-secret',
      ),
    );

    expect(
      (result as RegisterUserApiFailure).errorType,
      AuthenticationErrorType.network,
    );
  });

  test('registration timeout is mapped', () async {
    final api = _api(
      _FakeAdapter(
        exceptionBuilder: (options) => DioException.connectionTimeout(
          timeout: const Duration(seconds: 10),
          requestOptions: options,
        ),
      ),
    );

    final result = await api.register(
      const RegisterUserRequest(
        email: 'leo@example.com',
        fullName: 'Leandro Andre',
        password: 'fake-secret',
      ),
    );

    expect(
      (result as RegisterUserApiFailure).errorType,
      AuthenticationErrorType.timeout,
    );
  });
}

AuthenticationApi _api(_FakeAdapter adapter) {
  final dio = Dio()..httpClientAdapter = adapter;
  final apiClient = ApiClient(
    config: const ApiConfig(baseUrl: 'https://api.health-os.test'),
    dio: dio,
  );

  return AuthenticationApi(apiClient);
}

final class _JsonResponse {
  const _JsonResponse(this.statusCode, this.body);

  final int statusCode;
  final Object? body;

  ResponseBody toResponseBody() {
    return ResponseBody.fromString(
      jsonEncode(body),
      statusCode,
      headers: {
        Headers.contentTypeHeader: ['application/json'],
      },
    );
  }
}

final class _FakeAdapter implements HttpClientAdapter {
  _FakeAdapter({_JsonResponse? response, this.exceptionBuilder})
    : response =
          response ??
          const _JsonResponse(200, {
            'access_token': 'access-token',
            'refresh_token': 'refresh-token',
          });

  final _JsonResponse response;
  final DioException Function(RequestOptions options)? exceptionBuilder;
  RequestOptions? lastOptions;
  Object? lastBody;

  @override
  void close({bool force = false}) {}

  @override
  Future<ResponseBody> fetch(
    RequestOptions options,
    Stream<Uint8List>? requestStream,
    Future<void>? cancelFuture,
  ) async {
    lastOptions = options;

    if (requestStream != null) {
      final bodyBytes = await requestStream.expand((chunk) => chunk).toList();
      lastBody = jsonDecode(utf8.decode(bodyBytes));
    }

    final exception = exceptionBuilder?.call(options);
    if (exception != null) {
      throw exception;
    }

    return response.toResponseBody();
  }
}
