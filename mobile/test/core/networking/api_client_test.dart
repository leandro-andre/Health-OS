import 'dart:convert';
import 'dart:typed_data';

import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:health_os/core/networking/api_client.dart';
import 'package:health_os/core/networking/api_config.dart';
import 'package:health_os/core/networking/api_result.dart';

void main() {
  test('base URL and headers are configured', () {
    final dio = Dio();
    ApiClient(config: _config(), dio: dio);

    expect(dio.options.baseUrl, 'https://api.health-os.test');
    expect(dio.options.headers['Accept'], 'application/json');
    expect(dio.options.headers['Content-Type'], 'application/json');
  });

  test('JSON POST is sent correctly', () async {
    final adapter = _FakeAdapter(response: _JsonResponse(200, {'ok': true}));
    final dio = Dio()..httpClientAdapter = adapter;
    final client = ApiClient(config: _config(), dio: dio);

    await client.post(
      '/api/v1/users/',
      data: {'email': 'leo@example.com', 'full_name': 'Leandro Andre'},
    );

    expect(adapter.lastOptions?.method, 'POST');
    expect(adapter.lastOptions?.path, '/api/v1/users/');
    expect(adapter.lastHeaders['accept'], ['application/json']);
    expect(adapter.lastHeaders['content-type'], ['application/json']);
    expect(adapter.lastBody, {
      'email': 'leo@example.com',
      'full_name': 'Leandro Andre',
    });
  });

  test('successful JSON response is returned', () async {
    final client = _client(response: _JsonResponse(200, {'status': 'ok'}));

    final result = await client.get('/api/v1/health/');

    expect(result, isA<ApiSuccess>());
    final success = result as ApiSuccess;
    expect(success.statusCode, 200);
    expect(success.data, {'status': 'ok'});
  });

  test('HTTP error response is represented', () async {
    final client = _client(
      response: _JsonResponse(401, {
        'error': {'code': 'invalid_credentials'},
      }),
    );

    final result = await client.post('/api/v1/auth/login/');

    expect(result, isA<ApiFailure>());
    final failure = result as ApiFailure;
    expect(failure.error.type, ApiErrorType.http);
    expect(failure.error.statusCode, 401);
    expect(failure.error.data, {
      'error': {'code': 'invalid_credentials'},
    });
  });

  test('timeout is converted to timeout error', () async {
    final client = _client(
      exceptionBuilder: (options) => DioException.connectionTimeout(
        timeout: const Duration(seconds: 10),
        requestOptions: options,
      ),
    );

    final result = await client.get('/api/v1/health/');

    expect(result, isA<ApiFailure>());
    expect((result as ApiFailure).error.type, ApiErrorType.timeout);
  });

  test('connection failure is converted to connection error', () async {
    final client = _client(
      exceptionBuilder: (options) => DioException.connectionError(
        requestOptions: options,
        reason: 'offline',
      ),
    );

    final result = await client.get('/api/v1/health/');

    expect(result, isA<ApiFailure>());
    expect((result as ApiFailure).error.type, ApiErrorType.connection);
  });

  test('unexpected payload is represented', () async {
    final client = _client(response: _PlainResponse(200, 'not json'));

    final result = await client.get('/api/v1/health/');

    expect(result, isA<ApiFailure>());
    expect((result as ApiFailure).error.type, ApiErrorType.unexpectedPayload);
  });
}

ApiClient _client({
  _AdapterResponse? response,
  DioException Function(RequestOptions options)? exceptionBuilder,
}) {
  final dio = Dio()
    ..httpClientAdapter = _FakeAdapter(
      response: response,
      exceptionBuilder: exceptionBuilder,
    );

  return ApiClient(config: _config(), dio: dio);
}

ApiConfig _config() {
  return const ApiConfig(baseUrl: 'https://api.health-os.test');
}

sealed class _AdapterResponse {
  const _AdapterResponse();

  ResponseBody toResponseBody();
}

final class _JsonResponse extends _AdapterResponse {
  const _JsonResponse(this.statusCode, this.body);

  final int statusCode;
  final Object? body;

  @override
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

final class _PlainResponse extends _AdapterResponse {
  const _PlainResponse(this.statusCode, this.body);

  final int statusCode;
  final String body;

  @override
  ResponseBody toResponseBody() {
    return ResponseBody.fromString(
      body,
      statusCode,
      headers: {
        Headers.contentTypeHeader: ['text/plain'],
      },
    );
  }
}

final class _FakeAdapter implements HttpClientAdapter {
  _FakeAdapter({_AdapterResponse? response, this.exceptionBuilder})
    : response = response ?? const _JsonResponse(200, {'ok': true});

  final _AdapterResponse response;
  final DioException Function(RequestOptions options)? exceptionBuilder;
  RequestOptions? lastOptions;
  Object? lastBody;
  Map<String, List<String>> lastHeaders = {};

  @override
  void close({bool force = false}) {}

  @override
  Future<ResponseBody> fetch(
    RequestOptions options,
    Stream<Uint8List>? requestStream,
    Future<void>? cancelFuture,
  ) async {
    lastOptions = options;
    lastHeaders = options.headers.map(
      (key, value) => MapEntry(key.toLowerCase(), [value.toString()]),
    );

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
