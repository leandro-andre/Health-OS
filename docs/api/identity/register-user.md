# Register User API

## Status

Endpoint HTTP implementado.

## Metodo E URL

```text
POST /api/v1/users/
```

## Request

```json
{
  "email": "leo@example.com",
  "full_name": "Leandro Andre"
}
```

Campos:

- email: e-mail recebido pela API;
- full_name: nome completo recebido pela API.

Password ainda nao faz parte do endpoint de cadastro nesta etapa.

## Response De Sucesso

Status:

```text
201 Created
```

Body:

```json
{
  "user_id": "<uuid>",
  "email": "leo@example.com",
  "full_name": "Leandro Andre"
}
```

Os valores retornados refletem a normalizacao realizada pelo dominio.

A resposta nao expoe User Aggregate, UserModel, Domain Events ou objetos de Infrastructure.

## Erros

Payload estruturalmente invalido:

```text
400 Bad Request
```

Valores rejeitados pelo dominio:

```json
{
  "error": {
    "code": "invalid_user",
    "message": "<domain error>"
  }
}
```

E-mail ja cadastrado:

```text
409 Conflict
```

```json
{
  "error": {
    "code": "user_already_exists",
    "message": "User email already exists"
  }
}
```

## Relacao Com RegisterUser

A view implementada valida o payload, converte para RegisterUserInput, executa RegisterUser, monta a resposta com RegisterUserResponseSerializer e retorna 201 Created.

## Fora Do Escopo

- password no cadastro;
- login;
- JWT;
- access token;
- refresh token;
- logout;
- password reset;
- change password;
- OAuth;
- social login;
- MFA;
- email verification;
- politica avancada de senha;
- Outbox;
- Unit of Work.
