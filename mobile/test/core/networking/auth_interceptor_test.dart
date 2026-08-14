import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';

import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:health_os/core/networking/access_token_refresher.dart';
import 'package:health_os/core/networking/api_client.dart';
import 'package:health_os/core/networking/api_config.dart';
import 'package:health_os/core/networking/api_result.dart';
import 'package:health_os/core/networking/auth_interceptor.dart';
import 'package:health_os/core/session/session.dart';
import 'package:health_os/core/session/session_storage.dart';

void main() {
  test('access token is included in authenticated calls', () async {
    final adapter = _QueueAdapter([
      const _JsonResponse(200, {'ok': true}),
    ]);
    final storage = _MemorySessionStorage(
      session: const Session(
        accessToken: 'access-token',
        refreshToken: 'refresh-token',
      ),
    );
    final client = _client(adapter: adapter, sessionStorage: storage);

    await client.get('/api/v1/profile/');

    expect(adapter.requests.single.headers['authorization'], [
      'Bearer access-token',
    ]);
  });

  test('without Session Authorization is not added', () async {
    final adapter = _QueueAdapter([
      const _JsonResponse(200, {'ok': true}),
    ]);
    final client = _client(adapter: adapter);

    await client.get('/api/v1/profile/');

    expect(adapter.requests.single.headers, isNot(contains('authorization')));
  });

  test('protected 401 refreshes and repeats original request', () async {
    final adapter = _QueueAdapter([
      const _JsonResponse(401, {'detail': 'expired'}),
      const _JsonResponse(200, {'ok': true}),
    ]);
    final storage = _MemorySessionStorage(
      session: const Session(
        accessToken: 'old-access',
        refreshToken: 'refresh-token',
      ),
    );
    final refresher = _FakeAccessTokenRefresher(
      result: const AccessTokenRefreshSuccess('new-access'),
    );
    final client = _client(
      adapter: adapter,
      sessionStorage: storage,
      refresher: refresher,
    );

    final result = await client.get('/api/v1/profile/');

    expect(result, isA<ApiSuccess>());
    expect(refresher.callCount, 1);
    expect(refresher.refreshTokens, ['refresh-token']);
    expect(storage.savedSession?.accessToken, 'new-access');
    expect(storage.savedSession?.refreshToken, 'refresh-token');
    expect(adapter.requests, hasLength(2));
    expect(adapter.requests.last.headers['authorization'], [
      'Bearer new-access',
    ]);
  });

  test('refresh happens at most once for one request', () async {
    final adapter = _QueueAdapter([
      const _JsonResponse(401, {'detail': 'expired'}),
      const _JsonResponse(401, {'detail': 'expired'}),
    ]);
    final storage = _MemorySessionStorage(
      session: const Session(
        accessToken: 'old-access',
        refreshToken: 'refresh-token',
      ),
    );
    final refresher = _FakeAccessTokenRefresher(
      result: const AccessTokenRefreshSuccess('new-access'),
    );
    final client = _client(
      adapter: adapter,
      sessionStorage: storage,
      refresher: refresher,
    );

    final result = await client.get('/api/v1/profile/');

    expect(result, isA<ApiFailure>());
    expect((result as ApiFailure).error.statusCode, 401);
    expect(refresher.callCount, 1);
    expect(adapter.requests, hasLength(2));
  });

  test('login 401 does not refresh', () async {
    final adapter = _QueueAdapter([const _JsonResponse(401, {})]);
    final refresher = _FakeAccessTokenRefresher(
      result: const AccessTokenRefreshSuccess('new-access'),
    );
    final client = _client(
      adapter: adapter,
      sessionStorage: _MemorySessionStorage(
        session: const Session(
          accessToken: 'old-access',
          refreshToken: 'refresh-token',
        ),
      ),
      refresher: refresher,
    );

    await client.post('/api/v1/auth/login/');

    expect(refresher.callCount, 0);
    expect(adapter.requests, hasLength(1));
  });

  test('refresh 401 does not recurse', () async {
    final adapter = _QueueAdapter([const _JsonResponse(401, {})]);
    final refresher = _FakeAccessTokenRefresher(
      result: const AccessTokenRefreshSuccess('new-access'),
    );
    final client = _client(
      adapter: adapter,
      sessionStorage: _MemorySessionStorage(
        session: const Session(
          accessToken: 'old-access',
          refreshToken: 'refresh-token',
        ),
      ),
      refresher: refresher,
    );

    await client.post('/api/v1/auth/refresh/');

    expect(refresher.callCount, 0);
  });

  test('invalid refresh clears Session', () async {
    final adapter = _QueueAdapter([const _JsonResponse(401, {})]);
    final storage = _MemorySessionStorage(
      session: const Session(
        accessToken: 'old-access',
        refreshToken: 'refresh-token',
      ),
    );
    final client = _client(
      adapter: adapter,
      sessionStorage: storage,
      refresher: _FakeAccessTokenRefresher(
        result: const AccessTokenRefreshInvalidSession(),
      ),
    );

    await client.get('/api/v1/profile/');

    expect(storage.savedSession, isNull);
  });

  test('network failure during refresh does not clear Session', () async {
    final adapter = _QueueAdapter([const _JsonResponse(401, {})]);
    final storage = _MemorySessionStorage(
      session: const Session(
        accessToken: 'old-access',
        refreshToken: 'refresh-token',
      ),
    );
    final client = _client(
      adapter: adapter,
      sessionStorage: storage,
      refresher: _FakeAccessTokenRefresher(
        result: const AccessTokenRefreshTransportFailure(),
      ),
    );

    await client.get('/api/v1/profile/');

    expect(storage.savedSession?.accessToken, 'old-access');
  });

  test('non 401 error does not refresh', () async {
    final adapter = _QueueAdapter([const _JsonResponse(403, {})]);
    final refresher = _FakeAccessTokenRefresher(
      result: const AccessTokenRefreshSuccess('new-access'),
    );
    final client = _client(
      adapter: adapter,
      sessionStorage: _MemorySessionStorage(
        session: const Session(
          accessToken: 'old-access',
          refreshToken: 'refresh-token',
        ),
      ),
      refresher: refresher,
    );

    await client.get('/api/v1/profile/');

    expect(refresher.callCount, 0);
  });

  test('simultaneous 401 responses share one refresh', () async {
    final adapter = _QueueAdapter([
      const _JsonResponse(401, {}),
      const _JsonResponse(401, {}),
      const _JsonResponse(200, {'first': true}),
      const _JsonResponse(200, {'second': true}),
    ]);
    final refreshCompleter = Completer<AccessTokenRefreshResult>();
    final refresher = _FakeAccessTokenRefresher(completer: refreshCompleter);
    final client = _client(
      adapter: adapter,
      sessionStorage: _MemorySessionStorage(
        session: const Session(
          accessToken: 'old-access',
          refreshToken: 'refresh-token',
        ),
      ),
      refresher: refresher,
    );

    final first = client.get('/api/v1/profile/');
    final second = client.get('/api/v1/settings/');
    while (adapter.requests.length < 2 || refresher.callCount < 1) {
      await Future<void>.delayed(Duration.zero);
    }
    await Future<void>.delayed(Duration.zero);

    refreshCompleter.complete(const AccessTokenRefreshSuccess('new-access'));
    await Future.wait([first, second]);

    expect(refresher.callCount, 1);
    expect(adapter.requests, hasLength(4));
  });
}

ApiClient _client({
  required _QueueAdapter adapter,
  SessionStorage? sessionStorage,
  AccessTokenRefresher? refresher,
}) {
  final dio = Dio()..httpClientAdapter = adapter;
  return ApiClient(
    config: const ApiConfig(baseUrl: 'https://api.health-os.test'),
    dio: dio,
    interceptors: [
      AuthInterceptor(
        authenticatedDio: dio,
        sessionStorage: sessionStorage ?? _MemorySessionStorage(),
        accessTokenRefresher:
            refresher ??
            _FakeAccessTokenRefresher(
              result: const AccessTokenRefreshTransportFailure(),
            ),
      ),
    ],
  );
}

final class _MemorySessionStorage implements SessionStorage {
  _MemorySessionStorage({Session? session}) : savedSession = session;

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

final class _FakeAccessTokenRefresher implements AccessTokenRefresher {
  _FakeAccessTokenRefresher({this.result, this.completer});

  final AccessTokenRefreshResult? result;
  final Completer<AccessTokenRefreshResult>? completer;
  final refreshTokens = <String>[];
  int callCount = 0;

  @override
  Future<AccessTokenRefreshResult> refresh(String refreshToken) async {
    callCount++;
    refreshTokens.add(refreshToken);

    if (completer != null) {
      return completer!.future;
    }

    return result ?? const AccessTokenRefreshTransportFailure();
  }
}

final class _RecordedRequest {
  const _RecordedRequest({required this.path, required this.headers});

  final String path;
  final Map<String, List<String>> headers;
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

final class _QueueAdapter implements HttpClientAdapter {
  _QueueAdapter(List<_JsonResponse> responses) : _responses = [...responses];

  final List<_JsonResponse> _responses;
  final requests = <_RecordedRequest>[];

  @override
  void close({bool force = false}) {}

  @override
  Future<ResponseBody> fetch(
    RequestOptions options,
    Stream<Uint8List>? requestStream,
    Future<void>? cancelFuture,
  ) async {
    requests.add(
      _RecordedRequest(
        path: options.path,
        headers: options.headers.map(
          (key, value) => MapEntry(key.toLowerCase(), [value.toString()]),
        ),
      ),
    );

    if (_responses.isEmpty) {
      return const _JsonResponse(500, {}).toResponseBody();
    }

    return _responses.removeAt(0).toResponseBody();
  }
}
