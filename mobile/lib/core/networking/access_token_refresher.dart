import 'package:dio/dio.dart';
import 'package:health_os/core/networking/api_config.dart';

abstract interface class AccessTokenRefresher {
  Future<AccessTokenRefreshResult> refresh(String refreshToken);
}

sealed class AccessTokenRefreshResult {
  const AccessTokenRefreshResult();
}

final class AccessTokenRefreshSuccess extends AccessTokenRefreshResult {
  const AccessTokenRefreshSuccess(this.accessToken);

  final String accessToken;
}

final class AccessTokenRefreshInvalidSession extends AccessTokenRefreshResult {
  const AccessTokenRefreshInvalidSession();
}

final class AccessTokenRefreshTransportFailure
    extends AccessTokenRefreshResult {
  const AccessTokenRefreshTransportFailure();
}

final class DioAccessTokenRefresher implements AccessTokenRefresher {
  DioAccessTokenRefresher({required ApiConfig config, Dio? dio})
    : _dio = dio ?? Dio() {
    _dio.options = BaseOptions(
      baseUrl: config.baseUrl,
      connectTimeout: config.connectTimeout,
      receiveTimeout: config.receiveTimeout,
      sendTimeout: config.sendTimeout,
      responseType: ResponseType.json,
      validateStatus: (_) => true,
      headers: const {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
    );
  }

  final Dio _dio;

  @override
  Future<AccessTokenRefreshResult> refresh(String refreshToken) async {
    try {
      final response = await _dio.post<Object?>(
        '/api/v1/auth/refresh/',
        data: {'refresh_token': refreshToken},
      );

      final statusCode = response.statusCode ?? 0;
      if (statusCode == 400 || statusCode == 401) {
        return const AccessTokenRefreshInvalidSession();
      }

      if (statusCode < 200 || statusCode >= 300) {
        return const AccessTokenRefreshTransportFailure();
      }

      final data = response.data;
      if (data is! Map<String, dynamic>) {
        return const AccessTokenRefreshInvalidSession();
      }

      final accessToken = data['access_token'];
      if (accessToken is! String || accessToken.isEmpty) {
        return const AccessTokenRefreshInvalidSession();
      }

      return AccessTokenRefreshSuccess(accessToken);
    } on DioException catch (error) {
      return switch (error.type) {
        DioExceptionType.connectionTimeout ||
        DioExceptionType.sendTimeout ||
        DioExceptionType.receiveTimeout =>
          const AccessTokenRefreshTransportFailure(),
        _ => const AccessTokenRefreshTransportFailure(),
      };
    }
  }
}
