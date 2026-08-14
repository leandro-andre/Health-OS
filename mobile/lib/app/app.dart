import 'dart:async';

import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:health_os/app/auth_gate.dart';
import 'package:health_os/core/networking/access_token_refresher.dart';
import 'package:health_os/core/networking/api_client.dart';
import 'package:health_os/core/networking/api_config.dart';
import 'package:health_os/core/networking/auth_interceptor.dart';
import 'package:health_os/core/session/secure_session_storage.dart';
import 'package:health_os/core/session/session_controller.dart';
import 'package:health_os/core/session/session_storage.dart';
import 'package:health_os/features/authentication/data/authentication_api.dart';
import 'package:health_os/features/authentication/presentation/login_controller.dart';
import 'package:health_os/features/authentication/presentation/register_user_controller.dart';

class HealthOSApp extends StatefulWidget {
  const HealthOSApp({
    this.sessionStorage,
    this.accessTokenRefresher,
    this.authenticatedDio,
    super.key,
  });

  final SessionStorage? sessionStorage;
  final AccessTokenRefresher? accessTokenRefresher;
  final Dio? authenticatedDio;

  @override
  State<HealthOSApp> createState() => _HealthOSAppState();
}

class _HealthOSAppState extends State<HealthOSApp> {
  late final SessionController _sessionController;
  late final LoginController _loginController;
  late final RegisterUserController _registerUserController;

  @override
  void initState() {
    super.initState();
    final apiConfig = ApiConfig.fromEnvironment();
    final sessionStorage = widget.sessionStorage ?? SecureSessionStorage();
    _sessionController = SessionController(storage: sessionStorage);
    final authenticatedDio = widget.authenticatedDio ?? Dio();
    final accessTokenRefresher =
        widget.accessTokenRefresher ??
        DioAccessTokenRefresher(config: apiConfig);
    final apiClient = ApiClient(
      config: apiConfig,
      dio: authenticatedDio,
      interceptors: [
        AuthInterceptor(
          authenticatedDio: authenticatedDio,
          sessionStorage: _sessionController,
          accessTokenRefresher: accessTokenRefresher,
          sessionController: _sessionController,
        ),
      ],
    );
    final authenticationApi = AuthenticationApi(apiClient);

    _loginController = LoginController(
      authenticationApi: authenticationApi,
      sessionStorage: _sessionController,
    );
    _registerUserController = RegisterUserController(
      authenticationApi: authenticationApi,
    );
    unawaited(_sessionController.load());
  }

  @override
  void dispose() {
    _sessionController.dispose();
    _loginController.dispose();
    _registerUserController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Health OS',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF1D7A8C)),
        scaffoldBackgroundColor: const Color(0xFFF7FAFA),
        cardTheme: const CardThemeData(
          margin: EdgeInsets.zero,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.all(Radius.circular(8)),
          ),
        ),
        useMaterial3: true,
      ),
      home: AuthGate(
        sessionController: _sessionController,
        loginController: _loginController,
        registerUserController: _registerUserController,
      ),
    );
  }
}
