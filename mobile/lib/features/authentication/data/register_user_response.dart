final class RegisterUserResponse {
  const RegisterUserResponse({
    required this.userId,
    required this.email,
    required this.fullName,
  });

  factory RegisterUserResponse.fromJson(Map<String, dynamic> json) {
    final userId = json['user_id'];
    final email = json['email'];
    final fullName = json['full_name'];

    if (userId is! String || email is! String || fullName is! String) {
      throw const FormatException('Invalid register user response payload.');
    }

    return RegisterUserResponse(
      userId: userId,
      email: email,
      fullName: fullName,
    );
  }

  final String userId;
  final String email;
  final String fullName;
}
