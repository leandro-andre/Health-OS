import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:health_os/core/session/session.dart';
import 'package:health_os/core/session/session_storage.dart';

class SecureSessionStorage implements SessionStorage {
  SecureSessionStorage({SecureStorageAdapter? storage})
    : _storage = storage ?? const FlutterSecureStorageAdapter();

  static const _accessTokenKey = 'health_os.session.access_token';
  static const _refreshTokenKey = 'health_os.session.refresh_token';

  final SecureStorageAdapter _storage;

  @override
  Future<void> save(Session session) async {
    await _storage.write(key: _accessTokenKey, value: session.accessToken);
    await _storage.write(key: _refreshTokenKey, value: session.refreshToken);
  }

  @override
  Future<Session?> read() async {
    final accessToken = await _storage.read(key: _accessTokenKey);
    final refreshToken = await _storage.read(key: _refreshTokenKey);

    if (accessToken == null && refreshToken == null) {
      return null;
    }

    if (accessToken == null || refreshToken == null) {
      await clear();
      return null;
    }

    return Session(accessToken: accessToken, refreshToken: refreshToken);
  }

  @override
  Future<void> clear() async {
    await _storage.delete(key: _accessTokenKey);
    await _storage.delete(key: _refreshTokenKey);
  }
}

abstract interface class SecureStorageAdapter {
  Future<void> write({required String key, required String value});

  Future<String?> read({required String key});

  Future<void> delete({required String key});
}

final class FlutterSecureStorageAdapter implements SecureStorageAdapter {
  const FlutterSecureStorageAdapter([
    this._storage = const FlutterSecureStorage(),
  ]);

  final FlutterSecureStorage _storage;

  @override
  Future<void> write({required String key, required String value}) {
    return _storage.write(key: key, value: value);
  }

  @override
  Future<String?> read({required String key}) {
    return _storage.read(key: key);
  }

  @override
  Future<void> delete({required String key}) {
    return _storage.delete(key: key);
  }
}
