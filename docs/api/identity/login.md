# Login API

## Status

Endpoints HTTP implementados.

## Login

```text
POST /api/v1/auth/login/
```

Request:

```json
{
  "email": "leo@example.com",
  "password": "fake-secret"
}
```

Response:

```text
200 OK
```

```json
{
  "access_token": "<token>",
  "refresh_token": "<token>"
}
```

Credenciais invalidas:

```text
401 Unauthorized
```

```json
{
  "error": {
    "code": "invalid_credentials",
    "message": "Invalid credentials"
  }
}
```

Usuario inexistente, credencial inexistente e senha incorreta retornam o mesmo contrato.

## Refresh

```text
POST /api/v1/auth/refresh/
```

Request:

```json
{
  "refresh_token": "<token>"
}
```

Response:

```text
200 OK
```

```json
{
  "access_token": "<novo-token>"
}
```

Refresh token invalido, expirado, malformado, com assinatura invalida ou com tipo incorreto:

```text
401 Unauthorized
```

```json
{
  "error": {
    "code": "invalid_refresh_token",
    "message": "Invalid refresh token"
  }
}
```

## Seguranca

- password e write-only no request de login;
- responses nao expoem password, password_hash ou Credential;
- access token e refresh token possuem tipos distintos;
- access token nao e aceito como refresh token;
- mensagens de erro nao revelam se o email existe.

## Fora Do Escopo

- logout;
- blacklist;
- revogacao persistente;
- rotacao avancada de refresh token;
- OAuth;
- social login;
- MFA;
- endpoint /me;
- roles e permissions.
