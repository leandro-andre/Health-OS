# Register User

## Objetivo

RegisterUser orquestra o cadastro de um novo User no bounded context Identity.

Ele nao implementa regras de infraestrutura, nao usa Django ORM e nao conhece handlers concretos de eventos.

## Input

RegisterUserInput contem:

- email: str
- full_name: str
- password: str

UserId nao e fornecido pelo cliente. A senha existe somente durante a execucao do caso de uso e nunca e enviada ao User Aggregate.

## Output

RegisterUserOutput retorna:

- user_id: UserId
- email: str
- full_name: str

O output nao expoe User Aggregate, Django Model, credencial, senha, password_hash, Event Bus concreto ou objeto de infraestrutura.

## Dependencias

RegisterUser recebe explicitamente:

- UserRepository;
- UserIdGenerator;
- EventBus;
- PasswordHasher;
- CredentialRepository.

Application depende apenas desses contratos.

## Fluxo

1. Validar Email e FullName criando Value Objects.
2. Verificar se ja existe User com o e-mail informado.
3. Gerar UserId.
4. Criar o Aggregate com User.register(...).
5. Gerar password_hash com PasswordHasher.
6. Persistir User via UserRepository.add(user).
7. Persistir credencial via CredentialRepository.add(user.id, password_hash).
8. Publicar os Domain Events produzidos pelo Aggregate.
9. Retornar RegisterUserOutput.

## Email Existente

Email continua responsavel apenas por validade e normalizacao do valor.

Se ja existir User para o e-mail normalizado, RegisterUser levanta UserAlreadyExistsError.

Nesse cenario:

- UserId nao e gerado;
- senha nao e enviada ao PasswordHasher;
- UserRepository.add(...) nao e chamado;
- CredentialRepository.add(...) nao e chamado;
- nenhum Domain Event e publicado.

## Persistencia E Credenciais

RegisterUser persiste o User e, separadamente, a credencial associada ao UserId.

Senha em texto puro nunca e persistida. Apenas password_hash e enviado ao CredentialRepository.

User Aggregate permanece sem senha e sem hash.

## Domain Events

UserRegistered nasce no dominio durante User.register(...).

RegisterUser nao instancia UserRegistered diretamente. Eventos sao publicados somente depois que User e Credential foram persistidos.

Depois de uma publicacao bem-sucedida, os eventos pendentes sao removidos do Aggregate usando a API publica do Shared Kernel.

## Falhas

Se PasswordHasher falhar, nada e persistido e nenhum evento e publicado.

Se UserRepository.add(user) falhar, credencial nao e persistida e nenhum evento e publicado.

Se CredentialRepository.add(...) falhar, nenhum evento e publicado e a excecao e propagada.

Persistencia de User e Credential ainda nao esta protegida por Unit of Work.

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
