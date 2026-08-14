import 'package:flutter/material.dart';
import 'package:health_os/features/authentication/presentation/register_user_controller.dart';

class RegisterUserScreen extends StatefulWidget {
  const RegisterUserScreen({
    required this.controller,
    required this.onRegistrationSuccess,
    required this.onBackToLoginPressed,
    super.key,
  });

  final RegisterUserController controller;
  final VoidCallback onRegistrationSuccess;
  final VoidCallback onBackToLoginPressed;

  @override
  State<RegisterUserScreen> createState() => _RegisterUserScreenState();
}

class _RegisterUserScreenState extends State<RegisterUserScreen> {
  final _formKey = GlobalKey<FormState>();
  final _fullNameController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _passwordConfirmationController = TextEditingController();
  bool _obscurePassword = true;
  bool _obscurePasswordConfirmation = true;

  @override
  void dispose() {
    _fullNameController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    _passwordConfirmationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: widget.controller,
      builder: (context, _) {
        return Scaffold(
          body: SafeArea(
            child: Center(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(24),
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 420),
                  child: Form(
                    key: _formKey,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(
                          'Health OS',
                          textAlign: TextAlign.center,
                          style: Theme.of(context).textTheme.headlineMedium,
                        ),
                        const SizedBox(height: 12),
                        Text(
                          'Criar conta',
                          textAlign: TextAlign.center,
                          style: Theme.of(context).textTheme.titleMedium,
                        ),
                        const SizedBox(height: 32),
                        TextFormField(
                          key: const ValueKey('register-full-name-field'),
                          controller: _fullNameController,
                          enabled: !widget.controller.isLoading,
                          textInputAction: TextInputAction.next,
                          autofillHints: const [AutofillHints.name],
                          decoration: const InputDecoration(
                            labelText: 'Nome completo',
                            border: OutlineInputBorder(),
                          ),
                          validator: _requiredValidator,
                        ),
                        const SizedBox(height: 16),
                        TextFormField(
                          key: const ValueKey('register-email-field'),
                          controller: _emailController,
                          enabled: !widget.controller.isLoading,
                          keyboardType: TextInputType.emailAddress,
                          textInputAction: TextInputAction.next,
                          autofillHints: const [AutofillHints.email],
                          decoration: const InputDecoration(
                            labelText: 'E-mail',
                            border: OutlineInputBorder(),
                          ),
                          validator: _emailValidator,
                        ),
                        const SizedBox(height: 16),
                        TextFormField(
                          key: const ValueKey('register-password-field'),
                          controller: _passwordController,
                          enabled: !widget.controller.isLoading,
                          obscureText: _obscurePassword,
                          textInputAction: TextInputAction.next,
                          autofillHints: const [AutofillHints.newPassword],
                          decoration: InputDecoration(
                            labelText: 'Senha',
                            border: const OutlineInputBorder(),
                            suffixIcon: IconButton(
                              tooltip: _obscurePassword
                                  ? 'Mostrar senha'
                                  : 'Ocultar senha',
                              onPressed: widget.controller.isLoading
                                  ? null
                                  : _togglePasswordVisibility,
                              icon: Icon(
                                _obscurePassword
                                    ? Icons.visibility_outlined
                                    : Icons.visibility_off_outlined,
                              ),
                            ),
                          ),
                          validator: _requiredValidator,
                        ),
                        const SizedBox(height: 16),
                        TextFormField(
                          key: const ValueKey(
                            'register-password-confirmation-field',
                          ),
                          controller: _passwordConfirmationController,
                          enabled: !widget.controller.isLoading,
                          obscureText: _obscurePasswordConfirmation,
                          textInputAction: TextInputAction.done,
                          onFieldSubmitted: (_) {
                            if (!widget.controller.isLoading) {
                              _submit();
                            }
                          },
                          autofillHints: const [AutofillHints.newPassword],
                          decoration: InputDecoration(
                            labelText: 'Confirmacao de senha',
                            border: const OutlineInputBorder(),
                            suffixIcon: IconButton(
                              tooltip: _obscurePasswordConfirmation
                                  ? 'Mostrar confirmacao'
                                  : 'Ocultar confirmacao',
                              onPressed: widget.controller.isLoading
                                  ? null
                                  : _togglePasswordConfirmationVisibility,
                              icon: Icon(
                                _obscurePasswordConfirmation
                                    ? Icons.visibility_outlined
                                    : Icons.visibility_off_outlined,
                              ),
                            ),
                          ),
                          validator: _passwordConfirmationValidator,
                        ),
                        const SizedBox(height: 20),
                        if (widget.controller.errorMessage != null) ...[
                          Text(
                            widget.controller.errorMessage!,
                            key: const ValueKey('register-error-message'),
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              color: Theme.of(context).colorScheme.error,
                            ),
                          ),
                          const SizedBox(height: 16),
                        ],
                        FilledButton(
                          key: const ValueKey('register-submit-button'),
                          onPressed: widget.controller.isLoading
                              ? null
                              : _submit,
                          child: widget.controller.isLoading
                              ? const SizedBox.square(
                                  dimension: 20,
                                  child: CircularProgressIndicator(
                                    strokeWidth: 2,
                                  ),
                                )
                              : const Text('Criar conta'),
                        ),
                        const SizedBox(height: 12),
                        TextButton(
                          key: const ValueKey('back-to-login-button'),
                          onPressed: widget.controller.isLoading
                              ? null
                              : widget.onBackToLoginPressed,
                          child: const Text('Ja tenho conta'),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
        );
      },
    );
  }

  String? _requiredValidator(String? value) {
    if (value == null || value.trim().isEmpty) {
      return 'Campo obrigatorio.';
    }

    return null;
  }

  String? _emailValidator(String? value) {
    final requiredError = _requiredValidator(value);
    if (requiredError != null) {
      return requiredError;
    }

    final trimmed = value!.trim();
    if (!trimmed.contains('@') || !trimmed.contains('.')) {
      return 'E-mail invalido.';
    }

    return null;
  }

  String? _passwordConfirmationValidator(String? value) {
    final requiredError = _requiredValidator(value);
    if (requiredError != null) {
      return requiredError;
    }

    if (value != _passwordController.text) {
      return 'As senhas nao conferem.';
    }

    return null;
  }

  void _togglePasswordVisibility() {
    setState(() {
      _obscurePassword = !_obscurePassword;
    });
  }

  void _togglePasswordConfirmationVisibility() {
    setState(() {
      _obscurePasswordConfirmation = !_obscurePasswordConfirmation;
    });
  }

  Future<void> _submit() async {
    if (!(_formKey.currentState?.validate() ?? false)) {
      return;
    }

    await widget.controller.submit(
      fullName: _fullNameController.text.trim(),
      email: _emailController.text.trim(),
      password: _passwordController.text,
    );

    _passwordController.clear();
    _passwordConfirmationController.clear();

    if (widget.controller.state == RegisterUserScreenState.success) {
      widget.onRegistrationSuccess();
    }
  }
}
