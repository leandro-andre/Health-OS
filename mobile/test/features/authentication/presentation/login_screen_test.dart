import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';

import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:health_os/core/networking/api_client.dart';
import 'package:health_os/core/networking/api_config.dart';
import 'package:health_os/core/session/session.dart';
import 'package:health_os/core/session/session_storage.dart';
import 'package:health_os/features/authentication/data/authentication_api.dart';
import 'package:health_os/features/authentication/presentation/login_controller.dart';
import 'package:health_os/features/authentication/presentation/login_screen.dart';

void main() {
  testWidgets('login screen renders email and password fields', (tester) async {
    await tester.pumpWidget(_screen());

    expect(find.text('E-mail'), findsOneWidget);
    expect(find.text('Senha'), findsOneWidget);
    expect(find.text('Entrar'), findsOneWidget);
  });

  testWidgets('password field is obscured', (tester) async {
    await tester.pumpWidget(_screen());

    final editableText = tester.widget<EditableText>(
      find.descendant(
        of: find.byKey(const ValueKey('login-password-field')),
        matching: find.byType(EditableText),
      ),
    );

    expect(editableText.obscureText, isTrue);
  });

  testWidgets('empty submit does not execute login', (tester) async {
    final adapter = _FakeAdapter();
    await tester.pumpWidget(_screen(adapter: adapter));

    await tester.tap(find.byKey(const ValueKey('login-submit-button')));
    await tester.pump();

    expect(adapter.callCount, 0);
  });

  testWidgets('loading appears and submit button is disabled', (tester) async {
    final completer = Completer<ResponseBody>();
    final adapter = _FakeAdapter(responseCompleter: completer);
    await tester.pumpWidget(_screen(adapter: adapter));

    await tester.enterText(
      find.byKey(const ValueKey('login-email-field')),
      'leo@example.com',
    );
    await tester.enterText(
      find.byKey(const ValueKey('login-password-field')),
      'fake-secret',
    );
    await tester.tap(find.byKey(const ValueKey('login-submit-button')));
    await tester.pump();

    final submitButton = tester.widget<FilledButton>(
      find.byKey(const ValueKey('login-submit-button')),
    );
    expect(find.byType(CircularProgressIndicator), findsOneWidget);
    expect(submitButton.onPressed, isNull);

    completer.complete(_successResponse().toResponseBody());
    await tester.pumpAndSettle();
  });

  testWidgets('error appears after failed login', (tester) async {
    await tester.pumpWidget(
      _screen(adapter: _FakeAdapter(response: _JsonResponse(401, {}))),
    );

    await tester.enterText(
      find.byKey(const ValueKey('login-email-field')),
      'leo@example.com',
    );
    await tester.enterText(
      find.byKey(const ValueKey('login-password-field')),
      'wrong-secret',
    );
    await tester.tap(find.byKey(const ValueKey('login-submit-button')));
    await tester.pumpAndSettle();

    expect(find.text('E-mail ou senha invalidos.'), findsOneWidget);
  });

  testWidgets('successful submit stores Session without rendering tokens', (
    tester,
  ) async {
    await tester.pumpWidget(_screen());

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

    expect(find.text('access-token'), findsNothing);
    expect(find.text('refresh-token'), findsNothing);
  });

  testWidgets('keyboard submit executes login', (tester) async {
    final adapter = _FakeAdapter();
    await tester.pumpWidget(_screen(adapter: adapter));

    await tester.enterText(
      find.byKey(const ValueKey('login-email-field')),
      'leo@example.com',
    );
    await tester.enterText(
      find.byKey(const ValueKey('login-password-field')),
      'fake-secret',
    );
    await tester.testTextInput.receiveAction(TextInputAction.done);
    await tester.pumpAndSettle();

    expect(adapter.callCount, 1);
  });

  testWidgets('password is not rendered as free text', (tester) async {
    await tester.pumpWidget(_screen());

    await tester.enterText(
      find.byKey(const ValueKey('login-password-field')),
      'fake-secret',
    );
    await tester.pump();

    final textValues = tester
        .widgetList<Text>(find.byType(Text))
        .map((text) => text.data)
        .whereType<String>();

    expect(textValues, isNot(contains('fake-secret')));
  });
}

Widget _screen({_FakeAdapter? adapter, SessionStorage? sessionStorage}) {
  final dio = Dio()..httpClientAdapter = adapter ?? _FakeAdapter();
  final apiClient = ApiClient(
    config: const ApiConfig(baseUrl: 'https://api.health-os.test'),
    dio: dio,
  );
  final controller = LoginController(
    authenticationApi: AuthenticationApi(apiClient),
    sessionStorage: sessionStorage ?? _MemorySessionStorage(),
  );

  return MaterialApp(home: LoginScreen(controller: controller));
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

_JsonResponse _successResponse() {
  return const _JsonResponse(200, {
    'access_token': 'access-token',
    'refresh_token': 'refresh-token',
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
  _FakeAdapter({_JsonResponse? response, this.responseCompleter})
    : response = response ?? _successResponse();

  final _JsonResponse response;
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

    return responseCompleter == null
        ? response.toResponseBody()
        : responseCompleter!.future;
  }
}
