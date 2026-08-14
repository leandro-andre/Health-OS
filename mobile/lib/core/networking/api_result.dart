enum ApiErrorType { connection, timeout, http, unexpectedPayload }

sealed class ApiResult {
  const ApiResult();
}

final class ApiSuccess extends ApiResult {
  const ApiSuccess({required this.data, required this.statusCode});

  final Object? data;
  final int statusCode;
}

final class ApiFailure extends ApiResult {
  const ApiFailure(this.error);

  final ApiError error;
}

final class ApiError {
  const ApiError({required this.type, this.statusCode, this.data});

  final ApiErrorType type;
  final int? statusCode;
  final Object? data;
}
