# Register User API

## Status

Endpoint HTTP implementado na Feature 007.

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

O serializer de entrada valida apenas a estrutura HTTP basica e produz RegisterUserInput. Ele nao duplica regras de dominio.

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

A representacao de resposta e preparada na Presentation e nao expoe User Aggregate, UserModel, Domain Events ou objetos de Infrastructure.

Os valores retornados refletem a normalizacao realizada pelo dominio.

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

A view implementada:

1. validar o payload com RegisterUserRequestSerializer;
2. converter o payload valido para RegisterUserInput;
3. executar RegisterUser;
4. montar a resposta com RegisterUserResponseSerializer usando RegisterUserOutput;
5. retornar 201 Created.

## Composition Root

A Presentation possui uma factory explicita para compor:

```python
RegisterUser(
    user_repository=DjangoUserRepository(),
    user_id_generator=UUIDUserIdGenerator(),
    event_bus=InMemoryEventBus(),
)
```

Essa composicao fica na borda da aplicacao. O caso de uso continua dependendo apenas de contratos.

## Responsabilidades

Presentation:

- receber e validar a estrutura HTTP basica;
- converter dados para RegisterUserInput;
- compor implementacoes concretas;
- preparar a representacao HTTP planejada.

Domain:

- normalizar e validar Email;
- normalizar e validar FullName;
- proteger invariantes do User;
- criar UserRegistered durante User.register(...).

## Fora Do Escopo

- autenticacao;
- senha;
- JWT;
- OAuth;
- login;
- throttling;
- permissions;
- envio de e-mail;
- handlers de UserRegistered.
