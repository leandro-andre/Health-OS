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

`AuthGate` owns the runtime choice between loading, unauthenticated, and authenticated roots. The app swaps the rendered root based on session state instead of introducing a router package for this small flow. Authenticated users now land on the Home feature.

`core/` is reserved for code that is truly shared across features. It should stay small and grow only when real behavior requires shared networking, storage, configuration, or error handling.

`features/` is where product capabilities will grow. Each feature can introduce its own presentation, application, domain, or data responsibilities when those responsibilities become necessary.

The mobile app intentionally avoids global `domain/`, `data/`, and `presentation/` directories at the root. This keeps feature code local and avoids large technical buckets.

Dependencies are added only when a feature needs them. The mobile app currently uses Flutter, Dio for HTTP, `flutter_secure_storage` for token storage, `flutter_lints`, and `flutter_test`. It does not add state management packages, routing packages, JWT helpers, or code generation yet.

The Django API is already versioned under `/api/v1/`. Mobile integration currently covers registration, login, secure storage of tokens returned by login, Authorization headers for protected calls, and automatic access-token refresh.

Tests are present from the bootstrap so every future feature has a working quality baseline.

## Networking

Shared networking lives in:

```text
lib/core/networking/
  api_client.dart
  api_config.dart
  api_result.dart
```

Dio is the HTTP client. It was introduced because authentication will soon need consistent timeouts, JSON handling, interceptors, and refresh-token behavior.

`ApiConfig` centralizes the API base URL and timeout values. The base URL is read with `--dart-define=API_BASE_URL=...`; the default is only for Android emulator local development.

Configured defaults:

- connect timeout: 10 seconds;
- send timeout: 10 seconds;
- receive timeout: 20 seconds;
- headers: Accept and Content-Type set to application/json.

Authenticated requests use a small Dio interceptor in `core/networking`.

The interceptor:

- reads `SessionStorage`;
- adds `Authorization: Bearer <access_token>` to protected requests;
- excludes Login, Refresh, and Registration from authorization and refresh handling;
- refreshes the access token once when a protected request returns `401`;
- saves the updated `Session`;
- repeats the original request at most one time;
- clears the session only when refresh fails due to invalid authentication state.

Refresh transport failures, such as timeout or connection errors, do not clear the session immediately.

Network errors are represented with a small neutral model:

- connection failure;
- timeout;
- HTTP error response;
- unexpected payload.

Feature-specific API error mapping, such as invalid credentials, belongs inside the future Authentication feature and not in core networking.

## Session

Authenticated session infrastructure lives in:

```text
lib/core/session/
  session.dart
  session_storage.dart
  secure_session_storage.dart
```

`Session` stores only the access token and refresh token. It does not decode JWT claims and does not include user profile, email, roles, permissions, or clinical data.

`SessionStorage` is the app-facing contract for saving, reading, and clearing a session. The rest of the app should depend on this contract instead of depending directly on secure storage plugins.

`SecureSessionStorage` is the concrete implementation backed by `flutter_secure_storage`.

If only one token exists, the session is considered invalid. The storage clears both keys and returns `null` to avoid ambiguous authentication state.

The UI reads only the global authentication state exposed by `SessionController`; it does not receive tokens as navigation arguments.

`SessionController` wraps `SessionStorage` and is responsible for:

- loading startup state;
- saving authenticated state after login;
- clearing local session on logout;
- exposing invalid session state after refresh failure.

Dio adds Authorization automatically for protected requests and refreshes expired access tokens when possible. When refresh invalidates the session, networking signals through `SessionController` instead of knowing about widgets or `Navigator`.

## Authentication Feature

The first feature UI lives in:

```text
lib/features/authentication/
  data/
  presentation/
```

`data/` contains the login and registration request/response mapping. `AuthenticationApi` calls `POST /api/v1/auth/login/` and `POST /api/v1/users/` through the shared `ApiClient`.

`presentation/` contains the login and registration screens plus small controllers for each flow. `LoginController` coordinates the screen, API call, `Session` creation, and `SessionStorage` persistence. `RegisterUserController` coordinates account creation and never stores passwords, sessions, or tokens.

Both login and registration screens support idle, loading, error, and success states. After login success, the global session state becomes authenticated and the app shows Home. After registration success, the app returns to Login with a short success message.

## Home Feature

The authenticated entry point lives in:

```text
lib/features/home/
  presentation/
```

`HomeScreen` is static in this step. It shows a generic greeting, an introductory Health OS summary, planned module cards, and local logout.

The planned cards are clearly marked as `Em breve` and do not navigate to unavailable modules.

Home does not read tokens, profile data, clinical data, or authentication presentation internals.
