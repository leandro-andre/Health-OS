import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';

import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:health_os/core/networking/api_client.dart';
import 'package:health_os/core/networking/api_config.dart';
import 'package:health_os/features/authentication/data/authentication_api.dart';
import 'package:health_os/features/authentication/presentation/register_user_controller.dart';

void main() {
  test('registration controller does not depend on SessionStorage', () {
    final source = File(
      'lib/features/authentication/presentation/register_user_controller.dart',
    ).readAsStringSync();

    expect(source, isNot(contains('core/session')));
    expect(source, isNot(contains('SessionStorage')));
  });

  test(
    'successful registration reaches success without saving Session',
    () async {
      final controller = _controller(
        adapter: _FakeAdapter(response: _registrationSuccessResponse()),
      );

      await controller.submit(
        fullName: 'Leandro Andre',
        email: 'leo@example.com',
        password: 'fake-secret',
      );

      expect(controller.state, RegisterUserScreenState.success);
      expect(controller.createdUser?.userId, 'user-id');
      expect(controller.errorMessage, isNull);
    },
  );

  test('existing user shows friendly error', () async {
    final controller = _controller(
      adapter: _FakeAdapter(
        response: _JsonResponse(409, {'code': 'user_already_exists'}),
      ),
    );

    await controller.submit(
      fullName: 'Leandro Andre',
      email: 'leo@example.com',
      password: 'fake-secret',
    );

    expect(controller.state, RegisterUserScreenState.error);
    expect(controller.errorMessage, 'Ja existe uma conta com este e-mail.');
  });

  test('invalid input shows validation error', () async {
    final controller = _controller(
      adapter: _FakeAdapter(response: const _JsonResponse(400, {})),
    );

    await controller.submit(fullName: '', email: 'invalid', password: '');

    expect(controller.state, RegisterUserScreenState.error);
    expect(controller.errorMessage, 'Verifique os dados informados.');
  });

  test('network failure shows unavailable message', () async {
    final controller = _controller(
      adapter: _FakeAdapter(
        exceptionBuilder: (options) => DioException.connectionError(
          requestOptions: options,
          reason: 'offline',
        ),
      ),
    );

    await controller.submit(
      fullName: 'Leandro Andre',
      email: 'leo@example.com',
      password: 'fake-secret',
    );

    expect(controller.state, RegisterUserScreenState.error);
    expect(controller.errorMessage, 'Nao foi possivel conectar ao Health OS.');
  });

  test('timeout shows retry message', () async {
    final controller = _controller(
      adapter: _FakeAdapter(
        exceptionBuilder: (options) => DioException.connectionTimeout(
          timeout: const Duration(seconds: 10),
          requestOptions: options,
        ),
      ),
    );

    await controller.submit(
      fullName: 'Leandro Andre',
      email: 'leo@example.com',
      password: 'fake-secret',
    );

    expect(controller.state, RegisterUserScreenState.error);
    expect(
      controller.errorMessage,
      'A conexao demorou demais. Tente novamente.',
    );
  });

  test('loading state prevents duplicate submits', () async {
    final completer = Completer<ResponseBody>();
    final adapter = _FakeAdapter(responseCompleter: completer);
    final controller = _controller(adapter: adapter);

    final firstSubmit = controller.submit(
      fullName: 'Leandro Andre',
      email: 'leo@example.com',
      password: 'fake-secret',
    );
    await Future<void>.delayed(Duration.zero);
    final secondSubmit = controller.submit(
      fullName: 'Leandro Andre',
      email: 'leo@example.com',
      password: 'fake-secret',
    );

    completer.complete(_registrationSuccessResponse().toResponseBody());
    await Future.wait([firstSubmit, secondSubmit]);

    expect(adapter.callCount, 1);
  });
}

RegisterUserController _controller({required _FakeAdapter adapter}) {
  final dio = Dio()..httpClientAdapter = adapter;
  final apiClient = ApiClient(
    config: const ApiConfig(baseUrl: 'https://api.health-os.test'),
    dio: dio,
  );

  return RegisterUserController(
    authenticationApi: AuthenticationApi(apiClient),
  );
}

_JsonResponse _registrationSuccessResponse() {
  return const _JsonResponse(201, {
    'user_id': 'user-id',
    'email': 'leo@example.com',
    'full_name': 'Leandro Andre',
  });
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
  }) : response = response ?? _registrationSuccessResponse();

  final _JsonResponse response;
  final DioException Function(RequestOptions options)? exceptionBuilder;
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

    return responseCompleter == null
        ? response.toResponseBody()
        : responseCompleter!.future;
  }
}
