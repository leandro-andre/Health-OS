import 'package:flutter_test/flutter_test.dart';
import 'package:health_os/core/session/session.dart';

void main() {
  test('Session stores access and refresh tokens', () {
    const session = Session(
      accessToken: 'access-token',
      refreshToken: 'refresh-token',
    );

    expect(session.accessToken, 'access-token');
    expect(session.refreshToken, 'refresh-token');
  });

  test('Session string representation does not expose tokens', () {
    const session = Session(
      accessToken: 'access-token',
      refreshToken: 'refresh-token',
    );

    expect(session.toString(), isNot(contains('access-token')));
    expect(session.toString(), isNot(contains('refresh-token')));
  });
}
