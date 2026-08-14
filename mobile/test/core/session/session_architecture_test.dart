import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

void main() {
  test('core session does not depend on features or presentation widgets', () {
    final sessionFiles = Directory('lib/core/session')
        .listSync(recursive: true)
        .whereType<File>()
        .where((file) => file.path.endsWith('.dart'));

    final featureViolations = [
      for (final file in sessionFiles)
        if (file.readAsStringSync().contains('package:health_os/features/'))
          file.path,
    ];
    final widgetViolations = [
      for (final file in sessionFiles)
        if (file.readAsStringSync().contains('package:flutter/material.dart') ||
            file.readAsStringSync().contains('package:flutter/widgets.dart'))
          file.path,
    ];

    expect(featureViolations, isEmpty);
    expect(widgetViolations, isEmpty);
  });
}
