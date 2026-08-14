import 'package:health_os/core/session/session.dart';

abstract interface class SessionStorage {
  Future<void> save(Session session);

  Future<Session?> read();

  Future<void> clear();
}
