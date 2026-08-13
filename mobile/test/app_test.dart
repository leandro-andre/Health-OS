import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:health_os/app/app.dart';

void main() {
  testWidgets('HealthOSApp renders the bootstrap screen', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const HealthOSApp());

    expect(find.byType(MaterialApp), findsOneWidget);
    expect(find.text('Health OS'), findsOneWidget);
  });
}
