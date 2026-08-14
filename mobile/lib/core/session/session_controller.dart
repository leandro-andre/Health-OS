import 'package:flutter/foundation.dart';
import 'package:health_os/core/session/session.dart';
import 'package:health_os/core/session/session_storage.dart';

class SessionController extends ChangeNotifier implements SessionStorage {
  SessionController({required this.storage});

  final SessionStorage storage;

  AuthenticationState _state = AuthenticationState.loading;
  Session? _session;

  AuthenticationState get state => _state;

  Session? get session => _session;

  bool get isLoading => _state == AuthenticationState.loading;

  bool get isAuthenticated => _state == AuthenticationState.authenticated;

  Future<void> load() async {
    _setState(AuthenticationState.loading);

    try {
      _session = await storage.read();
      _setState(
        _session == null
            ? AuthenticationState.unauthenticated
            : AuthenticationState.authenticated,
      );
    } on Object {
      _session = null;
      _setState(AuthenticationState.unauthenticated);
    }
  }

  @override
  Future<Session?> read() async {
    try {
      _session = await storage.read();
      if (_state != AuthenticationState.loading) {
        _setState(
          _session == null
              ? AuthenticationState.unauthenticated
              : AuthenticationState.authenticated,
        );
      }
      return _session;
    } on Object {
      _session = null;
      if (_state != AuthenticationState.loading) {
        _setState(AuthenticationState.unauthenticated);
      }
      return null;
    }
  }

  @override
  Future<void> save(Session session) async {
    await storage.save(session);
    _session = session;
    _setState(AuthenticationState.authenticated);
  }

  @override
  Future<void> clear() async {
    await storage.clear();
    _session = null;
    _setState(AuthenticationState.unauthenticated);
  }

  Future<void> invalidate() => clear();

  void _setState(AuthenticationState state) {
    _state = state;
    notifyListeners();
  }
}

enum AuthenticationState { loading, unauthenticated, authenticated }
