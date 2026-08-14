import 'package:dio/dio.dart';
import 'package:health_os/core/networking/access_token_refresher.dart';
import 'package:health_os/core/session/session.dart';
import 'package:health_os/core/session/session_controller.dart';
import 'package:health_os/core/session/session_storage.dart';

class AuthInterceptor extends Interceptor {
  AuthInterceptor({
    required this.authenticatedDio,
    required this.sessionStorage,
    required this.accessTokenRefresher,
    this.sessionController,
  });

  static const _retriedKey = 'health_os.auth.retried_after_refresh';
  static const _publicPaths = {
    '/api/v1/auth/login/',
    '/api/v1/auth/refresh/',
    '/api/v1/users/',
  };

  final Dio authenticatedDio;
  final SessionStorage sessionStorage;
  final AccessTokenRefresher accessTokenRefresher;
  final SessionController? sessionController;
  Future<_RefreshOutcome>? _refreshInFlight;

  @override
  void onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    if (!_isPublicPath(options.path)) {
      final session = await sessionStorage.read();
      if (session != null) {
        options.headers['Authorization'] = 'Bearer ${session.accessToken}';
      }
    }

    handler.next(options);
  }

  @override
  void onResponse(
    Response<dynamic> response,
    ResponseInterceptorHandler handler,
  ) async {
    if (!_shouldRefresh(response)) {
      handler.next(response);
      return;
    }

    final refreshOutcome = await _refreshSession();
    switch (refreshOutcome) {
      case _RefreshSucceeded(:final session):
        final retriedResponse = await _retry(response.requestOptions, session);
        handler.resolve(retriedResponse);
      case _RefreshFailed():
        handler.next(response);
    }
  }

  Future<_RefreshOutcome> _refreshSession() {
    final currentRefresh = _refreshInFlight;
    if (currentRefresh != null) {
      return currentRefresh;
    }

    final refresh = _runRefresh();
    _refreshInFlight = refresh;
    refresh.whenComplete(() {
      if (identical(_refreshInFlight, refresh)) {
        _refreshInFlight = null;
      }
    });

    return refresh;
  }

  Future<_RefreshOutcome> _runRefresh() async {
    final session = await sessionStorage.read();
    if (session == null) {
      return const _RefreshFailed();
    }

    final result = await accessTokenRefresher.refresh(session.refreshToken);

    switch (result) {
      case AccessTokenRefreshSuccess(:final accessToken):
        final newSession = Session(
          accessToken: accessToken,
          refreshToken: session.refreshToken,
        );
        await sessionStorage.save(newSession);
        return _RefreshSucceeded(newSession);
      case AccessTokenRefreshInvalidSession():
        final controller = sessionController;
        if (controller == null) {
          await sessionStorage.clear();
        } else {
          await controller.invalidate();
        }
        return const _RefreshFailed();
      case AccessTokenRefreshTransportFailure():
        return const _RefreshFailed();
    }
  }

  Future<Response<dynamic>> _retry(
    RequestOptions requestOptions,
    Session session,
  ) {
    final retryOptions = Options(
      method: requestOptions.method,
      headers: {
        ...requestOptions.headers,
        'Authorization': 'Bearer ${session.accessToken}',
      },
      responseType: requestOptions.responseType,
      contentType: requestOptions.contentType,
      validateStatus: requestOptions.validateStatus,
      sendTimeout: requestOptions.sendTimeout,
      receiveTimeout: requestOptions.receiveTimeout,
      extra: {...requestOptions.extra, _retriedKey: true},
    );

    return authenticatedDio.request<dynamic>(
      requestOptions.path,
      data: requestOptions.data,
      queryParameters: requestOptions.queryParameters,
      options: retryOptions,
      cancelToken: requestOptions.cancelToken,
      onSendProgress: requestOptions.onSendProgress,
      onReceiveProgress: requestOptions.onReceiveProgress,
    );
  }

  bool _shouldRefresh(Response<dynamic> response) {
    return response.statusCode == 401 &&
        !_isPublicPath(response.requestOptions.path) &&
        response.requestOptions.extra[_retriedKey] != true;
  }

  bool _isPublicPath(String path) => _publicPaths.contains(path);
}

sealed class _RefreshOutcome {
  const _RefreshOutcome();
}

final class _RefreshSucceeded extends _RefreshOutcome {
  const _RefreshSucceeded(this.session);

  final Session session;
}

final class _RefreshFailed extends _RefreshOutcome {
  const _RefreshFailed();
}
