import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';

import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:health_os/core/networking/api_client.dart';
import 'package:health_os/core/networking/api_config.dart';
import 'package:health_os/core/session/session.dart';
import 'package:health_os/core/session/session_storage.dart';
import 'package:health_os/features/authentication/data/authentication_api.dart';
import 'package:health_os/features/authentication/presentation/login_controller.dart';

void main() {
  test('successful login saves Session', () async {
    final sessionStorage = _MemorySessionStorage();
    final controller = _controller(
      sessionStorage: sessionStorage,
      adapter: _FakeAdapter(
        response: _JsonResponse(200, {
          'access_token': 'access-token',
          'refresh_token': 'refresh-token',
        }),
      ),
    );

    await controller.submit(email: 'leo@example.com', password: 'fake-secret');

    expect(controller.state, LoginScreenState.success);
    expect(sessionStorage.savedSession?.accessToken, 'access-token');
    expect(sessionStorage.savedSession?.refreshToken, 'refresh-token');
  });

  test('invalid credentials do not save Session', () async {
    final sessionStorage = _MemorySessionStorage();
    final controller = _controller(
      sessionStorage: sessionStorage,
      adapter: _FakeAdapter(response: _JsonResponse(401, {})),
    );

    await controller.submit(email: 'leo@example.com', password: 'wrong-secret');

    expect(controller.state, LoginScreenState.error);
    expect(controller.errorMessage, 'E-mail ou senha invalidos.');
    expect(sessionStorage.savedSession, isNull);
  });

  test('network failure does not save Session', () async {
    final sessionStorage = _MemorySessionStorage();
    final controller = _controller(
      sessionStorage: sessionStorage,
      adapter: _FakeAdapter(
        exceptionBuilder: (options) => DioException.connectionError(
          requestOptions: options,
          reason: 'offline',
        ),
      ),
    );

    await controller.submit(email: 'leo@example.com', password: 'fake-secret');

    expect(controller.state, LoginScreenState.error);
    expect(controller.errorMessage, 'Nao foi possivel conectar ao Health OS.');
    expect(sessionStorage.savedSession, isNull);
  });

  test('timeout does not save Session', () async {
    final sessionStorage = _MemorySessionStorage();
    final controller = _controller(
      sessionStorage: sessionStorage,
      adapter: _FakeAdapter(
        exceptionBuilder: (options) => DioException.connectionTimeout(
          timeout: const Duration(seconds: 10),
          requestOptions: options,
        ),
      ),
    );

    await controller.submit(email: 'leo@example.com', password: 'fake-secret');

    expect(controller.state, LoginScreenState.error);
    expect(
      controller.errorMessage,
      'A conexao demorou demais. Tente novamente.',
    );
    expect(sessionStorage.savedSession, isNull);
  });

  test('loading state prevents duplicate submits', () async {
    final completer = Completer<ResponseBody>();
    final adapter = _FakeAdapter(responseCompleter: completer);
    final controller = _controller(
      sessionStorage: _MemorySessionStorage(),
      adapter: adapter,
    );

    final firstSubmit = controller.submit(
      email: 'leo@example.com',
      password: 'fake-secret',
    );
    await Future<void>.delayed(Duration.zero);
    final secondSubmit = controller.submit(
      email: 'leo@example.com',
      password: 'fake-secret',
    );

    completer.complete(
      _JsonResponse(200, {
        'access_token': 'access-token',
        'refresh_token': 'refresh-token',
      }).toResponseBody(),
    );
    await Future.wait([firstSubmit, secondSubmit]);

    expect(adapter.callCount, 1);
  });

  test('retry clears previous error while loading', () async {
    final completer = Completer<ResponseBody>();
    final adapter = _FakeAdapter(response: _JsonResponse(401, {}));
    final controller = _controller(
      sessionStorage: _MemorySessionStorage(),
      adapter: adapter,
    );

    await controller.submit(email: 'leo@example.com', password: 'wrong-secret');
    expect(controller.errorMessage, 'E-mail ou senha invalidos.');

    adapter.responseCompleterOverride = completer;
    final retry = controller.submit(
      email: 'leo@example.com',
      password: 'fake-secret',
    );
    await Future<void>.delayed(Duration.zero);

    expect(controller.state, LoginScreenState.loading);
    expect(controller.errorMessage, isNull);

    completer.complete(
      _JsonResponse(200, {
        'access_token': 'access-token',
        'refresh_token': 'refresh-token',
      }).toResponseBody(),
    );
    await retry;
  });
}

LoginController _controller({
  required SessionStorage sessionStorage,
  required _FakeAdapter adapter,
}) {
  final dio = Dio()..httpClientAdapter = adapter;
  final apiClient = ApiClient(
    config: const ApiConfig(baseUrl: 'https://api.health-os.test'),
    dio: dio,
  );

  return LoginController(
    authenticationApi: AuthenticationApi(apiClient),
    sessionStorage: sessionStorage,
  );
}

final class _MemorySessionStorage implements SessionStorage {
  Session? savedSession;

  @override
  Future<void> clear() async {
    savedSession = null;
  }

  @override
  Future<Session?> read() async {
    return savedSession;
  }

  @override
  Future<void> save(Session session) async {
    savedSession = session;
  }
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
  _FakeAdapter({
    _JsonResponse? response,
    this.exceptionBuilder,
    this.responseCompleter,
  }) : response =
           response ??
           const _JsonResponse(200, {
             'access_token': 'access-token',
             'refresh_token': 'refresh-token',
           });

  final _JsonResponse response;
  final DioException Function(RequestOptions options)? exceptionBuilder;
  Completer<ResponseBody>? responseCompleterOverride;
  final Completer<ResponseBody>? responseCompleter;
  int callCount = 0;

  @override
  void close({bool force = false}) {}

  @override
  Future<ResponseBody> fetch(
    RequestOptions options,
    Stream<Uint8List>? requestStream,
    Future<void>? cancelFuture,
  ) async {
    callCount++;
    final exception = exceptionBuilder?.call(options);
    if (exception != null) {
      throw exception;
    }

    final completer = responseCompleterOverride ?? responseCompleter;

    return completer == null ? response.toResponseBody() : completer.future;
  }
}
