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

Hashing acontece antes da persistencia da credencial. CredentialRepository nao executa hashing.

## Credenciais

CredentialRepository e o contrato da Application para persistir e recuperar password_hash por UserId.

Infrastructure implementa esse contrato com DjangoCredentialRepository.

Credenciais sao persistidas separadamente de User:

- associacao por UserId;
- banco armazena somente password_hash;
- um User possui no maximo uma credencial de senha;
- CredentialModel e detalhe de Infrastructure.

## Seguranca

- plain password nunca deve ser persistida;
- plain password nao deve aparecer em logs;
- nomes de campos deixam claro que armazenam hash;
- repository nao expoe objeto Django para Application;
- nenhum algoritmo criptografico proprio foi implementado.

## Fora Do Escopo

- alteracao do POST /users/;
- password no RegisterUser;
- login;
- JWT;
- refresh token;
- logout;
- recuperacao de senha;
- troca de senha;
- MFA;
- OAuth;
- social login;
- multiplos credential providers;
- sessao;
- permissions.

Login ainda nao esta implementado.
