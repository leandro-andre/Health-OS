import 'package:flutter/material.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({required this.onLogoutPressed, super.key});

  final VoidCallback onLogoutPressed;

  static const _plannedModules = [
    _HomeModule(
      title: 'Saude',
      description: 'Perfil, medidas e historico clinico.',
      icon: Icons.favorite_border,
    ),
    _HomeModule(
      title: 'Metas',
      description: 'Objetivos pessoais e progresso.',
      icon: Icons.flag_outlined,
    ),
    _HomeModule(
      title: 'Habitos',
      description: 'Rotinas e acompanhamento diario.',
      icon: Icons.repeat_outlined,
    ),
    _HomeModule(
      title: 'Exercicios',
      description: 'Plano de movimento e atividades.',
      icon: Icons.directions_run_outlined,
    ),
  ];

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 520),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          'Health OS',
                          style: theme.textTheme.headlineMedium,
                        ),
                      ),
                      IconButton(
                        key: const ValueKey('home-logout-button'),
                        tooltip: 'Sair',
                        onPressed: onLogoutPressed,
                        icon: const Icon(Icons.logout_outlined),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text('Ola', style: theme.textTheme.titleLarge),
                  const SizedBox(height: 24),
                  const _HomeSummaryCard(),
                  const SizedBox(height: 28),
                  Text('Acesso rapido', style: theme.textTheme.titleMedium),
                  const SizedBox(height: 12),
                  for (final module in _plannedModules) ...[
                    _ModuleCard(module: module),
                    const SizedBox(height: 12),
                  ],
                  const SizedBox(height: 28),
                  OutlinedButton.icon(
                    key: const ValueKey('logout-button'),
                    onPressed: onLogoutPressed,
                    icon: const Icon(Icons.logout_outlined),
                    label: const Text('Sair'),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _HomeSummaryCard extends StatelessWidget {
  const _HomeSummaryCard();

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Seu Health OS', style: theme.textTheme.titleLarge),
            const SizedBox(height: 8),
            Text(
              'Este sera o ponto de entrada para seus modulos de saude. '
              'Nenhum dado pessoal ou clinico esta conectado ainda.',
              style: theme.textTheme.bodyMedium,
            ),
          ],
        ),
      ),
    );
  }
}

class _ModuleCard extends StatelessWidget {
  const _ModuleCard({required this.module});

  final _HomeModule module;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Icon(module.icon, semanticLabel: module.title),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(module.title, style: theme.textTheme.titleMedium),
                  const SizedBox(height: 2),
                  Text(
                    module.description,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: theme.textTheme.bodySmall,
                  ),
                ],
              ),
            ),
            const SizedBox(width: 8),
            DecoratedBox(
              decoration: BoxDecoration(
                border: Border.all(color: colorScheme.outlineVariant),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                child: Text('Em breve', style: theme.textTheme.labelSmall),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

final class _HomeModule {
  const _HomeModule({
    required this.title,
    required this.description,
    required this.icon,
  });

  final String title;
  final String description;
  final IconData icon;
}
