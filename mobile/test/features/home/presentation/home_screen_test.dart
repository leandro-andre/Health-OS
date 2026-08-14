import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:health_os/features/home/presentation/home_screen.dart';

void main() {
  testWidgets('Home shows Health OS title and planned sections', (
    tester,
  ) async {
    await tester.pumpWidget(_screen());

    expect(find.text('Health OS'), findsOneWidget);
    expect(find.text('Ola'), findsOneWidget);
    expect(find.text('Seu Health OS'), findsOneWidget);
    expect(find.text('Acesso rapido'), findsOneWidget);
  });

  testWidgets('Home shows planned modules as unavailable', (tester) async {
    await tester.pumpWidget(_screen());

    expect(find.text('Saude'), findsOneWidget);
    expect(find.text('Metas'), findsOneWidget);
    expect(find.text('Habitos'), findsOneWidget);
    expect(find.text('Exercicios'), findsOneWidget);
    expect(find.text('Em breve'), findsNWidgets(4));
  });

  testWidgets('Home exposes logout action', (tester) async {
    var loggedOut = false;
    await tester.pumpWidget(
      _screen(
        onLogoutPressed: () {
          loggedOut = true;
        },
      ),
    );

    await tester.tap(find.byKey(const ValueKey('home-logout-button')));
    await tester.pump();

    expect(loggedOut, isTrue);
  });

  testWidgets('Home does not render tokens', (tester) async {
    await tester.pumpWidget(_screen());

    expect(find.text('access-token'), findsNothing);
    expect(find.text('refresh-token'), findsNothing);
  });
}

Widget _screen({VoidCallback? onLogoutPressed}) {
  return MaterialApp(
    home: HomeScreen(onLogoutPressed: onLogoutPressed ?? () {}),
  );
}
