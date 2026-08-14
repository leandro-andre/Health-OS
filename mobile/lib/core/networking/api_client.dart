import 'package:dio/dio.dart';
import 'package:health_os/core/networking/api_config.dart';
import 'package:health_os/core/networking/api_result.dart';

class ApiClient {
  ApiClient({
    required ApiConfig config,
    Dio? dio,
    List<Interceptor> interceptors = const [],
  }) : _dio = dio ?? Dio() {
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

    _dio.interceptors.addAll(interceptors);
  }

  final Dio _dio;

  Dio get dio => _dio;

  Future<ApiResult> get(String path) async {
    try {
      final response = await _dio.get<Object?>(path);

      return _toResult(response);
    } on DioException catch (error) {
      return ApiFailure(_toError(error));
    }
  }

  Future<ApiResult> post(String path, {Map<String, Object?>? data}) async {
    try {
      final response = await _dio.post<Object?>(path, data: data);

      return _toResult(response);
    } on DioException catch (error) {
      return ApiFailure(_toError(error));
    }
  }

  ApiResult _toResult(Response<Object?> response) {
    final statusCode = response.statusCode ?? 0;

    if (statusCode < 200 || statusCode >= 300) {
      return ApiFailure(
        ApiError(
          type: ApiErrorType.http,
          statusCode: statusCode,
          data: response.data,
        ),
      );
    }

    if (!_isJsonLike(response.data)) {
      return const ApiFailure(ApiError(type: ApiErrorType.unexpectedPayload));
    }

    return ApiSuccess(data: response.data, statusCode: statusCode);
  }

  ApiError _toError(DioException error) {
    return switch (error.type) {
      DioExceptionType.connectionTimeout ||
      DioExceptionType.sendTimeout ||
      DioExceptionType.receiveTimeout => const ApiError(
        type: ApiErrorType.timeout,
      ),
      _ => const ApiError(type: ApiErrorType.connection),
    };
  }

  bool _isJsonLike(Object? data) {
    return data == null ||
        data is Map<String, dynamic> ||
        data is List<dynamic>;
  }
}
