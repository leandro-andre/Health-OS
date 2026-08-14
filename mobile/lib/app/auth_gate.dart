import 'package:flutter/material.dart';
import 'package:health_os/core/session/session_controller.dart';
import 'package:health_os/features/authentication/presentation/login_controller.dart';
import 'package:health_os/features/authentication/presentation/login_screen.dart';
import 'package:health_os/features/authentication/presentation/register_user_controller.dart';
import 'package:health_os/features/authentication/presentation/register_user_screen.dart';
import 'package:health_os/features/home/presentation/home_screen.dart';

class AuthGate extends StatefulWidget {
  const AuthGate({
    required this.sessionController,
    required this.loginController,
    required this.registerUserController,
    super.key,
  });

  final SessionController sessionController;
  final LoginController loginController;
  final RegisterUserController registerUserController;

  @override
  State<AuthGate> createState() => _AuthGateState();
}

class _AuthGateState extends State<AuthGate> {
  bool _isRegistering = false;
  String? _registrationSuccessMessage;

  @override
  void initState() {
    super.initState();
    widget.sessionController.addListener(_handleAuthenticationStateChanged);
  }

  @override
  void didUpdateWidget(AuthGate oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.sessionController != widget.sessionController) {
      oldWidget.sessionController.removeListener(
        _handleAuthenticationStateChanged,
      );
      widget.sessionController.addListener(_handleAuthenticationStateChanged);
    }
  }

  @override
  void dispose() {
    widget.sessionController.removeListener(_handleAuthenticationStateChanged);
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: widget.sessionController,
      builder: (context, _) {
        return switch (widget.sessionController.state) {
          AuthenticationState.loading => const _AuthGateLoadingScreen(),
          AuthenticationState.authenticated => HomeScreen(
            onLogoutPressed: _logout,
          ),
          AuthenticationState.unauthenticated =>
            _isRegistering
                ? RegisterUserScreen(
                    controller: widget.registerUserController,
                    onRegistrationSuccess: _showLoginAfterRegistration,
                    onBackToLoginPressed: _showLogin,
                  )
                : LoginScreen(
                    controller: widget.loginController,
                    registrationSuccessMessage: _registrationSuccessMessage,
                    onCreateAccountPressed: _showRegistration,
                  ),
        };
      },
    );
  }

  void _handleAuthenticationStateChanged() {
    if (widget.sessionController.state == AuthenticationState.unauthenticated) {
      widget.loginController.reset();
      if (mounted) {
        setState(() {
          _isRegistering = false;
        });
      }
    }

    if (widget.sessionController.state == AuthenticationState.authenticated &&
        mounted) {
      setState(() {
        _isRegistering = false;
        _registrationSuccessMessage = null;
      });
    }
  }

  void _showRegistration() {
    setState(() {
      _registrationSuccessMessage = null;
      widget.registerUserController.reset();
      _isRegistering = true;
    });
  }

  void _showLogin() {
    setState(() {
      _isRegistering = false;
    });
  }

  void _showLoginAfterRegistration() {
    setState(() {
      _registrationSuccessMessage =
          'Conta criada com sucesso. Faca login para continuar.';
      widget.registerUserController.reset();
      _isRegistering = false;
    });
  }

  Future<void> _logout() => widget.sessionController.clear();
}

class _AuthGateLoadingScreen extends StatelessWidget {
  const _AuthGateLoadingScreen();

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      key: ValueKey('auth-loading-screen'),
      body: Center(child: CircularProgressIndicator()),
    );
  }
}
