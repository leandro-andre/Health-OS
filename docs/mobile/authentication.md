# Mobile Authentication

## Current Scope

The mobile app has the first functional authentication flow:

```text
Login Screen <-> Registration Screen

Login:
  Login Screen
    -> AuthenticationApi
    -> POST /api/v1/auth/login/
    -> Session
    -> SessionStorage
    -> Home

Registration:
  Registration Screen
    -> AuthenticationApi
    -> POST /api/v1/users/
    -> return to Login
```

Definitive authenticated routing is not implemented yet.
The current authenticated area is the initial Home screen.

## Auth Gate

`AuthGate` decides which root screen is rendered from the current authentication state:

- loading;
- unauthenticated;
- authenticated.

At startup, the app reads `SessionStorage`. While the read is pending, it shows an internal loading screen instead of briefly showing Login.

If a complete `Session` exists, the app shows Home. If no session exists, or if storage cannot be read safely, the app shows Login.

The app does not validate tokens remotely during startup and does not decode JWTs manually.

## Login

The login screen is the first feature UI in the mobile app.

It collects:

- email;
- password.

The password field is obscured and the password is used only for the login request.

The endpoint is:

```text
POST /api/v1/auth/login/
```

Errors are mapped to safe UI messages:

- 400: invalid input;
- 401: invalid credentials;
- network failure: service unavailable message;
- timeout: retry message.

The UI does not reveal whether the email exists.

## Registration

The registration screen collects:

- full name;
- email;
- password;
- password confirmation.

The endpoint is:

```text
POST /api/v1/users/
```

The request sent to the backend contains only:

```json
{
  "email": "leo@example.com",
  "full_name": "Leandro Andre",
  "password": "fake-secret"
}
```

`passwordConfirmation` exists only in the UI and is never sent to the backend.

On `201 Created`, the app returns to Login and shows:

```text
Conta criada com sucesso. Faca login para continuar.
```

Registration does not create a `Session`, does not store tokens, and does not log the user in automatically.

Registration errors are mapped to safe UI messages:

- 400: validation message;
- 409 with `user_already_exists`: existing account message;
- network failure: service unavailable message;
- timeout: retry message.

## Session

`Session` is immutable and stores only:

- access token;
- refresh token.

It does not decode JWT claims and does not store user profile, email, roles, permissions, or clinical data.

The string representation redacts token values.

## Storage

`SessionStorage` is the contract used by the app:

```dart
abstract interface class SessionStorage {
  Future<void> save(Session session);
  Future<Session?> read();
  Future<void> clear();
}
```

`SecureSessionStorage` implements the contract with `flutter_secure_storage`.

Access and refresh tokens are saved under centralized key names.

After successful login, the returned tokens are converted into `Session` and persisted through `SessionStorage`.

Registration never writes to `SessionStorage`. A session is created only by Login.

After Login saves a session, the global session state changes to authenticated and the app switches to Home without restart.

## Home

The authenticated area starts with the Home screen:

```text
Health OS
Seu Health OS
Acesso rapido
```

Home includes planned module cards marked as `Em breve` and a local `Sair` action.

Logout clears `SessionStorage`, updates the global state to unauthenticated, and returns to Login. It does not call the backend, revoke tokens, or use blacklist behavior.

## Authorization Header

Authenticated API calls receive:

```text
Authorization: Bearer <access_token>
```

The header is added by the networking layer when a valid `Session` exists.

Public authentication endpoints do not depend on the current access token:

- `POST /api/v1/auth/login/`;
- `POST /api/v1/auth/refresh/`;
- `POST /api/v1/users/`.

Tokens are sent only through headers or the refresh request body. They are not added to query strings and are not logged by the app.

## Automatic Refresh

The networking layer refreshes the access token for protected requests that return `401`.

The refresh endpoint is:

```text
POST /api/v1/auth/refresh/
```

The request is:

```json
{
  "refresh_token": "<token>"
}
```

The response is:

```json
{
  "access_token": "<new-token>"
}
```

After a successful refresh, the app preserves the current refresh token, replaces the access token, saves the updated `Session`, and repeats the original request once with the new access token.

The refresh endpoint does not refresh itself, Login does not trigger refresh, Registration does not trigger refresh, and a repeated request is not repeated again if it still returns `401`.

When refresh fails because the refresh token is invalid, expired, malformed, or rejected with `401`, `SessionStorage` is cleared and the global session state returns to unauthenticated. The app then renders Login again.

Network and timeout failures during refresh do not immediately clear the session, because they may be temporary transport problems.

## Partial Session

A session is valid only when both access token and refresh token exist.

If storage contains only one token, the session is treated as invalid, both keys are cleared, and `read()` returns `null`.

## Future Steps

- expand Home into definitive authenticated navigation.
- replace local-only logout with backend logout/revocation when that contract exists.

## Local Manual Flow

1. Start the Django backend.
2. Start Flutter with `--dart-define=API_BASE_URL=<backend-url>`.
3. Open Cadastro from Login.
4. Create an account.
5. Confirm the app returns to Login with the success message.
6. Authenticate with the created credentials.
