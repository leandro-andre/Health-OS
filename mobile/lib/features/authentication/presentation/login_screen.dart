import 'package:flutter/material.dart';
import 'package:health_os/features/authentication/presentation/login_controller.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({
    required this.controller,
    this.registrationSuccessMessage,
    this.onCreateAccountPressed,
    super.key,
  });

  final LoginController controller;
  final String? registrationSuccessMessage;
  final VoidCallback? onCreateAccountPressed;

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _obscurePassword = true;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: widget.controller,
      builder: (context, _) {
        if (widget.controller.state == LoginScreenState.success) {
          return const SizedBox.shrink();
        }

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
                          'Entre para continuar',
                          textAlign: TextAlign.center,
                          style: Theme.of(context).textTheme.titleMedium,
                        ),
                        const SizedBox(height: 32),
                        if (widget.registrationSuccessMessage != null) ...[
                          Text(
                            widget.registrationSuccessMessage!,
                            key: const ValueKey('registration-success-message'),
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              color: Theme.of(context).colorScheme.primary,
                            ),
                          ),
                          const SizedBox(height: 16),
                        ],
                        TextFormField(
                          key: const ValueKey('login-email-field'),
                          controller: _emailController,
                          enabled: !widget.controller.isLoading,
                          keyboardType: TextInputType.emailAddress,
                          textInputAction: TextInputAction.next,
                          autofillHints: const [AutofillHints.email],
                          decoration: const InputDecoration(
                            labelText: 'E-mail',
                            border: OutlineInputBorder(),
                          ),
                          validator: _requiredValidator,
                        ),
                        const SizedBox(height: 16),
                        TextFormField(
                          key: const ValueKey('login-password-field'),
                          controller: _passwordController,
                          enabled: !widget.controller.isLoading,
                          obscureText: _obscurePassword,
                          textInputAction: TextInputAction.done,
                          onFieldSubmitted: (_) {
                            if (!widget.controller.isLoading) {
                              _submit();
                            }
                          },
                          autofillHints: const [AutofillHints.password],
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
                        const SizedBox(height: 20),
                        if (widget.controller.errorMessage != null) ...[
                          Text(
                            widget.controller.errorMessage!,
                            key: const ValueKey('login-error-message'),
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              color: Theme.of(context).colorScheme.error,
                            ),
                          ),
                          const SizedBox(height: 16),
                        ],
                        FilledButton(
                          key: const ValueKey('login-submit-button'),
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
                              : const Text('Entrar'),
                        ),
                        if (widget.onCreateAccountPressed != null) ...[
                          const SizedBox(height: 12),
                          TextButton(
                            key: const ValueKey('create-account-button'),
                            onPressed: widget.controller.isLoading
                                ? null
                                : widget.onCreateAccountPressed,
                            child: const Text('Criar conta'),
                          ),
                        ],
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

  void _togglePasswordVisibility() {
    setState(() {
      _obscurePassword = !_obscurePassword;
    });
  }

  Future<void> _submit() async {
    if (!(_formKey.currentState?.validate() ?? false)) {
      return;
    }

    await widget.controller.submit(
      email: _emailController.text.trim(),
      password: _passwordController.text,
    );
    _passwordController.clear();
  }
}
