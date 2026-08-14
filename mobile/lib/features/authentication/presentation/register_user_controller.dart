import 'package:flutter/foundation.dart';
import 'package:health_os/features/authentication/data/authentication_api.dart';
import 'package:health_os/features/authentication/data/register_user_request.dart';
import 'package:health_os/features/authentication/data/register_user_response.dart';

class RegisterUserController extends ChangeNotifier {
  RegisterUserController({required this.authenticationApi});

  final AuthenticationApi authenticationApi;

  RegisterUserScreenState _state = RegisterUserScreenState.idle;
  String? _errorMessage;
  RegisterUserResponse? _createdUser;

  RegisterUserScreenState get state => _state;

  String? get errorMessage => _errorMessage;

  RegisterUserResponse? get createdUser => _createdUser;

  bool get isLoading => _state == RegisterUserScreenState.loading;

  Future<void> submit({
    required String fullName,
    required String email,
    required String password,
  }) async {
    if (isLoading) {
      return;
    }

    _createdUser = null;
    _errorMessage = null;
    _setState(RegisterUserScreenState.loading);

    final result = await authenticationApi.register(
      RegisterUserRequest(email: email, fullName: fullName, password: password),
    );

    switch (result) {
      case RegisterUserApiSuccess(:final response):
        _createdUser = response;
        _errorMessage = null;
        _setState(RegisterUserScreenState.success);
      case RegisterUserApiFailure(:final errorType):
        _createdUser = null;
        _errorMessage = _messageFor(errorType);
        _setState(RegisterUserScreenState.error);
    }
  }

  void reset() {
    _createdUser = null;
    _errorMessage = null;
    _setState(RegisterUserScreenState.idle);
  }

  void _setState(RegisterUserScreenState state) {
    _state = state;
    notifyListeners();
  }

  String _messageFor(AuthenticationErrorType errorType) {
    return switch (errorType) {
      AuthenticationErrorType.invalidCredentials ||
      AuthenticationErrorType.invalidInput => 'Verifique os dados informados.',
      AuthenticationErrorType.userAlreadyExists =>
        'Ja existe uma conta com este e-mail.',
      AuthenticationErrorType.network =>
        'Nao foi possivel conectar ao Health OS.',
      AuthenticationErrorType.timeout =>
        'A conexao demorou demais. Tente novamente.',
      AuthenticationErrorType.unexpected =>
        'Nao foi possivel criar a conta agora.',
    };
  }
}

enum RegisterUserScreenState { idle, loading, error, success }
