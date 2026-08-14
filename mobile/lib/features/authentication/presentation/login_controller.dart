import 'package:flutter/foundation.dart';
import 'package:health_os/core/session/session_storage.dart';
import 'package:health_os/features/authentication/data/authentication_api.dart';
import 'package:health_os/features/authentication/data/login_request.dart';

class LoginController extends ChangeNotifier {
  LoginController({
    required this.authenticationApi,
    required this.sessionStorage,
  });

  final AuthenticationApi authenticationApi;
  final SessionStorage sessionStorage;

  LoginScreenState _state = LoginScreenState.idle;
  String? _errorMessage;

  LoginScreenState get state => _state;

  String? get errorMessage => _errorMessage;

  bool get isLoading => _state == LoginScreenState.loading;

  Future<void> submit({required String email, required String password}) async {
    if (isLoading) {
      return;
    }

    _errorMessage = null;
    _setState(LoginScreenState.loading);

    final result = await authenticationApi.login(
      LoginRequest(email: email, password: password),
    );

    switch (result) {
      case AuthenticationApiSuccess(:final response):
        await sessionStorage.save(response.toSession());
        _errorMessage = null;
        _setState(LoginScreenState.success);
      case AuthenticationApiFailure(:final errorType):
        _errorMessage = _messageFor(errorType);
        _setState(LoginScreenState.error);
    }
  }

  void reset() {
    if (_state == LoginScreenState.idle && _errorMessage == null) {
      return;
    }

    _errorMessage = null;
    _setState(LoginScreenState.idle);
  }

  void _setState(LoginScreenState state) {
    _state = state;
    notifyListeners();
  }

  String _messageFor(AuthenticationErrorType errorType) {
    return switch (errorType) {
      AuthenticationErrorType.invalidCredentials =>
        'E-mail ou senha invalidos.',
      AuthenticationErrorType.invalidInput => 'Verifique os dados informados.',
      AuthenticationErrorType.userAlreadyExists =>
        'Nao foi possivel realizar o login agora.',
      AuthenticationErrorType.network =>
        'Nao foi possivel conectar ao Health OS.',
      AuthenticationErrorType.timeout =>
        'A conexao demorou demais. Tente novamente.',
      AuthenticationErrorType.unexpected =>
        'Nao foi possivel realizar o login agora.',
    };
  }
}

enum LoginScreenState { idle, loading, error, success }
