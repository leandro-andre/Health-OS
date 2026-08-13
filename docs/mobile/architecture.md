# Mobile Architecture

Health OS mobile is a Flutter application for the Android and iOS MVP.

The app starts with a feature-first structure compatible with pragmatic Clean Architecture:

```text
lib/
  app/
    app.dart
  core/
  features/
  main.dart
```

`main.dart` stays small and only starts `HealthOSApp`.

`HealthOSApp` owns the Flutter root and MaterialApp configuration.

`core/` is reserved for code that is truly shared across features. It should stay small and grow only when real behavior requires shared networking, storage, configuration, or error handling.

`features/` is where product capabilities will grow. Each feature can introduce its own presentation, application, domain, or data responsibilities when those responsibilities become necessary.

The mobile app intentionally avoids global `domain/`, `data/`, and `presentation/` directories at the root. This keeps feature code local and avoids large technical buckets.

Dependencies are added only when a feature needs them. This bootstrap uses Flutter itself plus `flutter_lints` and `flutter_test`; it does not add HTTP clients, state management, routing, secure storage, JWT helpers, code generation, or backend integration yet.

The Django API is already versioned under `/api/v1/`. Mobile integration with registration, login, access tokens, and refresh tokens will be introduced in later authentication-flow steps.

Tests are present from the bootstrap so every future feature has a working quality baseline.
