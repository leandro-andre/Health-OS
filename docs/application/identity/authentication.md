# Authentication

## Contexto

Autenticacao por senha e uma capacidade separada do User Aggregate no bounded context Identity.

User representa a identidade logica do usuario e nao armazena senha, hash de senha ou credenciais.

## Password Hashing

Application define PasswordHasher:

```python
class PasswordHasher(Protocol):
    def hash(self, plain_password: str) -> str: ...
    def verify(self, plain_password: str, password_hash: str) -> bool: ...
```

Infrastructure fornece DjangoPasswordHasher, baseado nas APIs oficiais de password hashing do Django.

## Credenciais

CredentialRepository e o contrato da Application para persistir e recuperar password_hash por UserId.

Infrastructure implementa esse contrato com DjangoCredentialRepository e persiste apenas password_hash em Credential separada, associada a UserId.

Um User possui no maximo uma credencial de senha.

## Cadastro

RegisterUser recebe password como entrada, gera password_hash com PasswordHasher, persiste User, persiste Credential e somente depois publica Domain Events.

Senha em texto puro nunca e persistida. A API de cadastro nunca retorna password ou password_hash.

## Seguranca

- plain password nunca deve ser persistida;
- plain password nao deve aparecer em logs;
- hash de senha nao e reversivel;
- comparacao usa API segura da infraestrutura;
- nenhum algoritmo criptografico proprio foi implementado.

## Fora Do Escopo

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

Login e tokens ainda nao estao implementados. JWT e tokens pertencem a Feature 009.
