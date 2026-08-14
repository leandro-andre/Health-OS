import 'package:flutter_test/flutter_test.dart';
import 'package:health_os/core/session/secure_session_storage.dart';
import 'package:health_os/core/session/session.dart';
import 'package:health_os/core/session/session_storage.dart';

void main() {
  test('SecureSessionStorage satisfies SessionStorage contract', () {
    final storage = SecureSessionStorage(
      storage: _MemorySecureStorageAdapter(),
    );

    expect(storage, isA<SessionStorage>());
  });

  test('save persists both tokens', () async {
    final adapter = _MemorySecureStorageAdapter();
    final storage = SecureSessionStorage(storage: adapter);

    await storage.save(
      const Session(accessToken: 'access-token', refreshToken: 'refresh-token'),
    );

    expect(adapter.values.values, contains('access-token'));
    expect(adapter.values.values, contains('refresh-token'));
  });

  test('read reconstructs Session', () async {
    final storage = SecureSessionStorage(
      storage: _MemorySecureStorageAdapter(),
    );

    await storage.save(
      const Session(accessToken: 'access-token', refreshToken: 'refresh-token'),
    );

    final session = await storage.read();

    expect(session?.accessToken, 'access-token');
    expect(session?.refreshToken, 'refresh-token');
  });

  test('read returns null when no session exists', () async {
    final storage = SecureSessionStorage(
      storage: _MemorySecureStorageAdapter(),
    );

    expect(await storage.read(), isNull);
  });

  test('clear removes both tokens', () async {
    final storage = SecureSessionStorage(
      storage: _MemorySecureStorageAdapter(),
    );

    await storage.save(
      const Session(accessToken: 'access-token', refreshToken: 'refresh-token'),
    );
    await storage.clear();

    expect(await storage.read(), isNull);
  });

  test('partial session is invalid and gets cleared', () async {
    final adapter = _MemorySecureStorageAdapter();
    final storage = SecureSessionStorage(storage: adapter);

    await adapter.write(
      key: 'health_os.session.access_token',
      value: 'access-token',
    );

    expect(await storage.read(), isNull);
    expect(adapter.values, isEmpty);
  });
}

final class _MemorySecureStorageAdapter implements SecureStorageAdapter {
  final Map<String, String> values = {};

  @override
  Future<void> delete({required String key}) async {
    values.remove(key);
  }

  @override
  Future<String?> read({required String key}) async {
    return values[key];
  }

  @override
  Future<void> write({required String key, required String value}) async {
    values[key] = value;
  }
}
