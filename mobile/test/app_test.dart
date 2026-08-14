import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';

import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:health_os/app/app.dart';
import 'package:health_os/app/auth_gate.dart';
import 'package:health_os/core/networking/access_token_refresher.dart';
import 'package:health_os/core/networking/api_client.dart';
import 'package:health_os/core/networking/api_config.dart';
import 'package:health_os/core/session/session_controller.dart';
import 'package:health_os/core/session/session.dart';
import 'package:health_os/core/session/session_storage.dart';
import 'package:health_os/features/authentication/data/authentication_api.dart';
import 'package:health_os/features/authentication/presentation/login_controller.dart';
import 'package:health_os/features/authentication/presentation/register_user_controller.dart';

void main() {
  testWidgets('HealthOSApp shows initial loading while Session is read', (
    tester,
  ) async {
    final readCompleter = Completer<Session?>();

    await tester.pumpWidget(
      HealthOSApp(
        sessionStorage: _MemorySessionStorage(readCompleter: readCompleter),
      ),
    );

    expect(find.byKey(const ValueKey('auth-loading-screen')), findsOneWidget);

    readCompleter.complete(null);
    await tester.pumpAndSettle();
  });

  testWidgets('without Session renders the login screen', (tester) async {
    await tester.pumpWidget(_app());
    await tester.pumpAndSettle();

    expect(find.byType(MaterialApp), findsOneWidget);
    expect(find.text('Health OS'), findsOneWidget);
    expect(find.text('Entrar'), findsOneWidget);
  });

  testWidgets('with Session renders Home', (tester) async {
    await tester.pumpWidget(_app(session: _session()));
    await tester.pumpAndSettle();

    expect(find.text('Seu Health OS'), findsOneWidget);
    expect(find.text('Acesso rapido'), findsOneWidget);
    expect(find.text('Sair'), findsOneWidget);
    expect(find.text('access-token'), findsNothing);
    expect(find.text('refresh-token'), findsNothing);
  });

  testWidgets('successful login switches to Home', (tester) async {
    final adapter = _FakeAdapter(
      responses: [
        const _JsonResponse(200, {
          'access_token': 'access-token',
          'refresh_token': 'refresh-token',
        }),
      ],
    );
    final storage = _MemorySessionStorage();

    await tester.pumpWidget(_app(adapter: adapter, sessionStorage: storage));
    await tester.pumpAndSettle();

    await tester.enterText(
      find.byKey(const ValueKey('login-email-field')),
      'leo@example.com',
    );
    await tester.enterText(
      find.byKey(const ValueKey('login-password-field')),
      'fake-secret',
    );
    await tester.tap(find.byKey(const ValueKey('login-submit-button')));
    await tester.pumpAndSettle();

    expect(find.text('Seu Health OS'), findsOneWidget);
    expect(storage.savedSession?.accessToken, 'access-token');
  });

  testWidgets('logout clears Session and returns to Login', (tester) async {
    final storage = _MemorySessionStorage(session: _session());

    await tester.pumpWidget(_app(sessionStorage: storage));
    await tester.pumpAndSettle();

    await tester.tap(find.byKey(const ValueKey('home-logout-button')));
    await tester.pumpAndSettle();

    expect(find.text('Entrar'), findsOneWidget);
    expect(storage.savedSession, isNull);
  });

  testWidgets('session invalidation returns to Login', (tester) async {
    final sessionController = SessionController(
      storage: _MemorySessionStorage(session: _session()),
    );
    await sessionController.load();
    final authenticationApi = _authenticationApi();
    final loginController = LoginController(
      authenticationApi: authenticationApi,
      sessionStorage: sessionController,
    );

    await tester.pumpWidget(
      MaterialApp(
        home: AuthGate(
          sessionController: sessionController,
          loginController: loginController,
          registerUserController: RegisterUserController(
            authenticationApi: authenticationApi,
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    await sessionController.invalidate();
    await tester.pumpAndSettle();

    expect(find.text('Entrar'), findsOneWidget);
    expect(find.text('Seu Health OS'), findsNothing);
  });

  testWidgets('registration stays accessible from Login', (tester) async {
    await tester.pumpWidget(_app());
    await tester.pumpAndSettle();

    await tester.tap(find.byKey(const ValueKey('create-account-button')));
    await tester.pumpAndSettle();

    expect(find.text('Criar conta'), findsNWidgets(2));
    expect(find.text('Nome completo'), findsOneWidget);

    await tester.tap(find.byKey(const ValueKey('back-to-login-button')));
    await tester.pumpAndSettle();

    expect(find.text('Entrar'), findsOneWidget);
    expect(find.text('Nome completo'), findsNothing);
  });
}

AuthenticationApi _authenticationApi() {
  final dio = Dio()..httpClientAdapter = _FakeAdapter();
  final apiClient = ApiClient(
    config: const ApiConfig(baseUrl: 'https://api.health-os.test'),
    dio: dio,
  );

  return AuthenticationApi(apiClient);
}

Widget _app({
  Session? session,
  SessionStorage? sessionStorage,
  _FakeAdapter? adapter,
  Dio? authenticatedDio,
  AccessTokenRefresher? accessTokenRefresher,
}) {
  final dio =
      authenticatedDio ??
      (Dio()..httpClientAdapter = adapter ?? _FakeAdapter());

  return HealthOSApp(
    sessionStorage: sessionStorage ?? _MemorySessionStorage(session: session),
    authenticatedDio: dio,
    accessTokenRefresher:
        accessTokenRefresher ??
        _FakeAccessTokenRefresher(const AccessTokenRefreshTransportFailure()),
  );
}

Session _session() {
  return const Session(
    accessToken: 'access-token',
    refreshToken: 'refresh-token',
  );
}

final class _MemorySessionStorage implements SessionStorage {
  _MemorySessionStorage({Session? session, this.readCompleter})
    : savedSession = session;

  Session? savedSession;
  final Completer<Session?>? readCompleter;

  @override
  Future<void> clear() async {
    savedSession = null;
  }

  @override
  Future<Session?> read() async {
    final completer = readCompleter;
    if (completer != null && !completer.isCompleted) {
      savedSession = await completer.future;
    }

    return savedSession;
  }

  @override
  Future<void> save(Session session) async {
    savedSession = session;
  }
}

final class _FakeAccessTokenRefresher implements AccessTokenRefresher {
  const _FakeAccessTokenRefresher(this.result);

  final AccessTokenRefreshResult result;

  @override
  Future<AccessTokenRefreshResult> refresh(String refreshToken) async {
    return result;
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
  _FakeAdapter({List<_JsonResponse>? responses})
    : _responses = [
        ...?responses,
        const _JsonResponse(200, {'ok': true}),
      ];

  final List<_JsonResponse> _responses;

  @override
  void close({bool force = false}) {}

  @override
  Future<ResponseBody> fetch(
    RequestOptions options,
    Stream<Uint8List>? requestStream,
    Future<void>? cancelFuture,
  ) async {
    return _responses.removeAt(0).toResponseBody();
  }
}
