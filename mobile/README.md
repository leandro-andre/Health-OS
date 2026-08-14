# Health OS Mobile

Flutter application for the Health OS mobile MVP.

## Requirements

- Flutter 3.47.0 stable
- Dart 3.13.0
- Android SDK for Android builds
- Xcode for iOS builds on macOS

## Run

```bash
flutter pub get
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000
```

Use `http://127.0.0.1:8000` for desktop targets and a reachable LAN address for physical devices.

## Current Auth Flow

The mobile app currently supports:

- Cadastro through `POST /api/v1/users/`;
- Login through `POST /api/v1/auth/login/`;
- secure local Session storage;
- automatic Authorization and access-token refresh;
- Auth Gate startup routing;
- authenticated Home;
- local logout.

The Home still uses static content. Profile data, health modules, backend logout, token revocation, and `/me` are outside the current scope.

## Analyze

```bash
flutter analyze
```

## Format

```bash
dart format --set-exit-if-changed lib test
```

## Test

```bash
flutter test
```

## Manual Smoke Test

1. Start the Django backend.
2. Run the app with `API_BASE_URL`.
3. Open Cadastro and create a user.
4. Confirm the app returns to Login with success feedback.
5. Log in with the created credentials.
6. Confirm Home appears.
7. Close and reopen the app to confirm the local session is restored.
8. Tap Sair and confirm Login appears.
