final class RegisterUserRequest {
  const RegisterUserRequest({
    required this.email,
    required this.fullName,
    required this.password,
  });

  final String email;
  final String fullName;
  final String password;

  Map<String, Object?> toJson() {
    return {'email': email, 'full_name': fullName, 'password': password};
  }
}
