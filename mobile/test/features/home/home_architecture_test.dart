import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

void main() {
  test('home feature does not depend on authentication internals', () {
    final homeFiles = Directory('lib/features/home')
        .listSync(recursive: true)
        .whereType<File>()
        .where((file) => file.path.endsWith('.dart'));

    final violations = [
      for (final file in homeFiles)
        if (file.readAsStringSync().contains('features/authentication/'))
          file.path,
    ];

    expect(violations, isEmpty);
  });
}
