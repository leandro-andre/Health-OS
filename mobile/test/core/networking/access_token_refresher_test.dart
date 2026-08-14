import 'dart:convert';
import 'dart:typed_data';

import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:health_os/core/networking/access_token_refresher.dart';
import 'package:health_os/core/networking/api_config.dart';

void main() {
  test('refresh posts refresh_token to refresh endpoint', () async {
    final adapter = _FakeAdapter(
      response: const _JsonResponse(200, {'access_token': 'new-access'}),
    );
    final refresher = _refresher(adapter);

    await refresher.refresh('refresh-token');

    expect(adapter.lastOptions?.method, 'POST');
    expect(adapter.lastOptions?.path, '/api/v1/auth/refresh/');
    expect(adapter.lastBody, {'refresh_token': 'refresh-token'});
  });

  test('successful refresh returns new access token', () async {
    final refresher = _refresher(
      _FakeAdapter(
        response: const _JsonResponse(200, {'access_token': 'new-access'}),
      ),
    );

    final result = await refresher.refresh('refresh-token');

    expect(result, isA<AccessTokenRefreshSuccess>());
    expect((result as AccessTokenRefreshSuccess).accessToken, 'new-access');
  });

  test('401 refresh maps to invalid session', () async {
    final refresher = _refresher(
      _FakeAdapter(response: const _JsonResponse(401, {})),
    );

    final result = await refresher.refresh('refresh-token');

    expect(result, isA<AccessTokenRefreshInvalidSession>());
  });

  test('400 refresh maps to invalid session', () async {
    final refresher = _refresher(
      _FakeAdapter(response: const _JsonResponse(400, {})),
    );

    final result = await refresher.refresh('refresh-token');

    expect(result, isA<AccessTokenRefreshInvalidSession>());
  });

  test('network failure maps to transport failure', () async {
    final refresher = _refresher(
      _FakeAdapter(
        exceptionBuilder: (options) => DioException.connectionError(
          requestOptions: options,
          reason: 'offline',
        ),
      ),
    );

    final result = await refresher.refresh('refresh-token');

    expect(result, isA<AccessTokenRefreshTransportFailure>());
  });
}

DioAccessTokenRefresher _refresher(_FakeAdapter adapter) {
  final dio = Dio()..httpClientAdapter = adapter;
  return DioAccessTokenRefresher(
    config: const ApiConfig(baseUrl: 'https://api.health-os.test'),
    dio: dio,
  );
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
          response ?? const _JsonResponse(200, {'access_token': 'new-access'});

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
