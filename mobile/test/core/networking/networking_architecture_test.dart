import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

void main() {
  test('core networking does not depend on features or widgets', () {
    final networkingFiles = Directory('lib/core/networking')
        .listSync(recursive: true)
        .whereType<File>()
        .where((file) => file.path.endsWith('.dart'));

    final featureViolations = [
      for (final file in networkingFiles)
        if (file.readAsStringSync().contains('package:health_os/features/'))
          file.path,
    ];
    final widgetViolations = [
      for (final file in networkingFiles)
        if (file.readAsStringSync().contains('package:flutter/material.dart') ||
            file.readAsStringSync().contains('package:flutter/widgets.dart'))
          file.path,
    ];

    expect(featureViolations, isEmpty);
    expect(widgetViolations, isEmpty);
  });
}
