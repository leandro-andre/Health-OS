import 'package:flutter_test/flutter_test.dart';
import 'package:health_os/core/session/session.dart';
import 'package:health_os/core/session/session_controller.dart';
import 'package:health_os/core/session/session_storage.dart';

void main() {
  test('without Session starts unauthenticated', () async {
    final controller = SessionController(storage: _MemorySessionStorage());

    await controller.load();

    expect(controller.state, AuthenticationState.unauthenticated);
    expect(controller.session, isNull);
  });

  test('with Session starts authenticated', () async {
    final controller = SessionController(
      storage: _MemorySessionStorage(session: _session()),
    );

    await controller.load();

    expect(controller.state, AuthenticationState.authenticated);
    expect(controller.session?.accessToken, 'access-token');
  });

  test('save marks session as authenticated', () async {
    final storage = _MemorySessionStorage();
    final controller = SessionController(storage: storage);

    await controller.save(_session());

    expect(controller.state, AuthenticationState.authenticated);
    expect(storage.savedSession?.refreshToken, 'refresh-token');
  });

  test('logout clears Session and marks unauthenticated', () async {
    final storage = _MemorySessionStorage(session: _session());
    final controller = SessionController(storage: storage);

    await controller.clear();

    expect(controller.state, AuthenticationState.unauthenticated);
    expect(controller.session, isNull);
    expect(storage.savedSession, isNull);
  });

  test('invalidation clears Session and marks unauthenticated', () async {
    final storage = _MemorySessionStorage(session: _session());
    final controller = SessionController(storage: storage);

    await controller.invalidate();

    expect(controller.state, AuthenticationState.unauthenticated);
    expect(storage.savedSession, isNull);
  });

  test('storage read error fails closed as unauthenticated', () async {
    final controller = SessionController(
      storage: _ThrowingReadSessionStorage(),
    );

    await controller.load();

    expect(controller.state, AuthenticationState.unauthenticated);
    expect(controller.session, isNull);
  });
}

Session _session() {
  return const Session(
    accessToken: 'access-token',
    refreshToken: 'refresh-token',
  );
}

final class _MemorySessionStorage implements SessionStorage {
  _MemorySessionStorage({Session? session}) : savedSession = session;

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

final class _ThrowingReadSessionStorage implements SessionStorage {
  @override
  Future<void> clear() async {}

  @override
  Future<Session?> read() {
    throw StateError('storage unavailable');
  }

  @override
  Future<void> save(Session session) async {}
}
