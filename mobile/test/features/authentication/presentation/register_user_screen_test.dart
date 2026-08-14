import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';

import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:health_os/core/networking/api_client.dart';
import 'package:health_os/core/networking/api_config.dart';
import 'package:health_os/features/authentication/data/authentication_api.dart';
import 'package:health_os/features/authentication/presentation/register_user_controller.dart';
import 'package:health_os/features/authentication/presentation/register_user_screen.dart';

void main() {
  testWidgets('registration screen renders expected fields', (tester) async {
    await tester.pumpWidget(_screen());

    expect(find.text('Nome completo'), findsOneWidget);
    expect(find.text('E-mail'), findsOneWidget);
    expect(find.text('Senha'), findsOneWidget);
    expect(find.text('Confirmacao de senha'), findsOneWidget);
    expect(find.text('Criar conta'), findsNWidgets(2));
    expect(find.text('Ja tenho conta'), findsOneWidget);
  });

  testWidgets('password fields are obscured', (tester) async {
    await tester.pumpWidget(_screen());

    final password = tester.widget<EditableText>(
      find.descendant(
        of: find.byKey(const ValueKey('register-password-field')),
        matching: find.byType(EditableText),
      ),
    );
    final confirmation = tester.widget<EditableText>(
      find.descendant(
        of: find.byKey(const ValueKey('register-password-confirmation-field')),
        matching: find.byType(EditableText),
      ),
    );

    expect(password.obscureText, isTrue);
    expect(confirmation.obscureText, isTrue);
  });

  testWidgets('empty submit does not call API', (tester) async {
    final adapter = _FakeAdapter();
    await tester.pumpWidget(_screen(adapter: adapter));

    await tester.tap(find.byKey(const ValueKey('register-submit-button')));
    await tester.pump();

    expect(adapter.callCount, 0);
  });

  testWidgets('different passwords block submit', (tester) async {
    final adapter = _FakeAdapter();
    await tester.pumpWidget(_screen(adapter: adapter));

    await _fillForm(tester, password: 'fake-secret', confirmation: 'different');
    await tester.tap(find.byKey(const ValueKey('register-submit-button')));
    await tester.pump();

    expect(find.text('As senhas nao conferem.'), findsOneWidget);
    expect(adapter.callCount, 0);
  });

  testWidgets('loading appears and submit button is disabled', (tester) async {
    final completer = Completer<ResponseBody>();
    final adapter = _FakeAdapter(responseCompleter: completer);
    await tester.pumpWidget(_screen(adapter: adapter));

    await _fillForm(tester);
    await tester.tap(find.byKey(const ValueKey('register-submit-button')));
    await tester.pump();

    final submitButton = tester.widget<FilledButton>(
      find.byKey(const ValueKey('register-submit-button')),
    );
    expect(find.byType(CircularProgressIndicator), findsOneWidget);
    expect(submitButton.onPressed, isNull);

    completer.complete(_successResponse().toResponseBody());
    await tester.pumpAndSettle();
  });

  testWidgets('409 shows friendly existing user message', (tester) async {
    await tester.pumpWidget(
      _screen(
        adapter: _FakeAdapter(
          response: _JsonResponse(409, {'code': 'user_already_exists'}),
        ),
      ),
    );

    await _fillForm(tester);
    await tester.tap(find.byKey(const ValueKey('register-submit-button')));
    await tester.pumpAndSettle();

    expect(find.text('Ja existe uma conta com este e-mail.'), findsOneWidget);
  });

  testWidgets('success calls callback and clears passwords', (tester) async {
    var registrationSucceeded = false;
    await tester.pumpWidget(
      _screen(
        onRegistrationSuccess: () {
          registrationSucceeded = true;
        },
      ),
    );

    await _fillForm(tester);
    await tester.tap(find.byKey(const ValueKey('register-submit-button')));
    await tester.pumpAndSettle();

    expect(registrationSucceeded, isTrue);
    expect(find.text('fake-secret'), findsNothing);
  });

  testWidgets('keyboard submit executes registration', (tester) async {
    final adapter = _FakeAdapter();
    await tester.pumpWidget(_screen(adapter: adapter));

    await _fillForm(tester);
    await tester.testTextInput.receiveAction(TextInputAction.done);
    await tester.pumpAndSettle();

    expect(adapter.callCount, 1);
  });

  testWidgets('back to login action calls callback', (tester) async {
    var wentBack = false;
    await tester.pumpWidget(
      _screen(
        onBackToLoginPressed: () {
          wentBack = true;
        },
      ),
    );

    await tester.tap(find.byKey(const ValueKey('back-to-login-button')));
    await tester.pump();

    expect(wentBack, isTrue);
  });
}

Future<void> _fillForm(
  WidgetTester tester, {
  String password = 'fake-secret',
  String confirmation = 'fake-secret',
}) async {
  await tester.enterText(
    find.byKey(const ValueKey('register-full-name-field')),
    'Leandro Andre',
  );
  await tester.enterText(
    find.byKey(const ValueKey('register-email-field')),
    'leo@example.com',
  );
  await tester.enterText(
    find.byKey(const ValueKey('register-password-field')),
    password,
  );
  await tester.enterText(
    find.byKey(const ValueKey('register-password-confirmation-field')),
    confirmation,
  );
}

Widget _screen({
  _FakeAdapter? adapter,
  VoidCallback? onRegistrationSuccess,
  VoidCallback? onBackToLoginPressed,
}) {
  final dio = Dio()..httpClientAdapter = adapter ?? _FakeAdapter();
  final apiClient = ApiClient(
    config: const ApiConfig(baseUrl: 'https://api.health-os.test'),
    dio: dio,
  );
  final controller = RegisterUserController(
    authenticationApi: AuthenticationApi(apiClient),
  );

  return MaterialApp(
    home: RegisterUserScreen(
      controller: controller,
      onRegistrationSuccess: onRegistrationSuccess ?? () {},
      onBackToLoginPressed: onBackToLoginPressed ?? () {},
    ),
  );
}

_JsonResponse _successResponse() {
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
