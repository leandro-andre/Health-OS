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

## Login

LoginUser autentica um usuario por email e senha.

Input:

- email: str
- password: str

Output:

- access_token: str
- refresh_token: str

Fluxo:

1. Criar Email a partir da entrada.
2. Buscar User por email.
3. Buscar password_hash por UserId.
4. Verificar a senha com PasswordHasher.verify(...).
5. Emitir tokens com TokenIssuer.
6. Retornar LoginUserOutput.

Usuario inexistente, credencial inexistente e senha incorreta produzem o mesmo erro publico:
InvalidCredentialsError.

Esse comportamento evita revelar qual parte da autenticacao falhou.

## Tokens

Application define TokenIssuer e TokenPair.

TokenIssuer recebe UserId e retorna access_token e refresh_token.

Infrastructure fornece JWTTokenIssuer usando PyJWT.

PyJWT foi escolhido por ser uma biblioteca madura, pequena e focada em JWT. Isso evita implementar assinatura, serializacao e validacao de JWT manualmente.

Configuracao:

- JWT_ALGORITHM: padrao HS256;
- JWT_SIGNING_KEY: chave de assinatura por ambiente;
- JWT_ACCESS_TOKEN_SECONDS: padrao 900 segundos;
- JWT_REFRESH_TOKEN_SECONDS: padrao 604800 segundos.

Se JWT_SIGNING_KEY nao for definido, a configuracao usa SECRET_KEY do Django como fallback nesta fase. O trade-off e simplicidade agora, com a recomendacao de usar segredo separado por ambiente antes de producao real.

Claims usadas:

- sub: UserId;
- iat: data de emissao;
- exp: data de expiracao;
- typ: access ou refresh.

Tokens nao carregam password, password_hash, informacoes clinicas ou email.

Access token e refresh token sao diferenciados por typ.

## HTTP

Login HTTP:

```text
POST /api/v1/auth/login/
```

Recebe email e password, executa LoginUser e retorna access_token e refresh_token.

Refresh HTTP:

```text
POST /api/v1/auth/refresh/
```

Recebe refresh_token valido e retorna novo access_token.

Presentation valida apenas estrutura HTTP, chama Application ou Infrastructure composta na borda e mapeia erros conhecidos.

## Seguranca

- plain password nunca deve ser persistida;
- plain password nao deve aparecer em logs;
- password hash nao aparece em LoginUserOutput;
- nomes de campos deixam claro que armazenam hash;
- repository nao expoe objeto Django para Application;
- LoginUser usa PasswordHasher.verify(...) e nao compara hashes manualmente;
- JWTTokenIssuer valida assinatura, expiracao e tipo do token;
- access token nao e aceito como refresh token;
- refresh token nao e aceito como access token;
- nenhum algoritmo criptografico proprio foi implementado.

## Fora Do Escopo

- logout;
- blacklist;
- token revocation;
- rotacao avancada de refresh token;
- recuperacao de senha;
- troca de senha;
- MFA;
- OAuth;
- social login;
- multiplos credential providers;
- sessao;
- permissions.
