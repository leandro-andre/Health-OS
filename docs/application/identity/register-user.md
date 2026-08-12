# Register User

## Objetivo

RegisterUser orquestra o cadastro de um novo User no bounded context Identity.

Ele nao implementa regras de infraestrutura, nao usa Django ORM e nao conhece handlers concretos de eventos.

## Input

RegisterUserInput contem:

- email: str
- full_name: str

UserId nao e fornecido pelo cliente. Password ainda nao faz parte de RegisterUser nesta etapa.

## Output

RegisterUserOutput retorna:

- user_id: UserId
- email: str
- full_name: str

O output nao expoe User Aggregate, Django Model, credencial, Event Bus concreto ou objeto de infraestrutura.

## Dependencias

RegisterUser recebe explicitamente:

- UserRepository;
- UserIdGenerator;
- EventBus.

Application depende apenas desses contratos.

## Fluxo

1. Validar Email e FullName criando Value Objects.
2. Verificar se ja existe User com o e-mail informado.
3. Gerar UserId.
4. Criar o Aggregate com User.register(...).
5. Persistir User via UserRepository.add(user).
6. Publicar os Domain Events produzidos pelo Aggregate.
7. Retornar RegisterUserOutput.

## Email Existente

Email continua responsavel apenas por validade e normalizacao do valor.

Se ja existir User para o e-mail normalizado, RegisterUser levanta UserAlreadyExistsError.

Nesse cenario:

- UserId nao e gerado;
- UserRepository.add(...) nao e chamado;
- nenhum Domain Event e publicado.

## Domain Events

UserRegistered nasce no dominio durante User.register(...).

RegisterUser nao instancia UserRegistered diretamente. Eventos sao publicados somente depois que User foi persistido.

Depois de uma publicacao bem-sucedida, os eventos pendentes sao removidos do Aggregate usando a API publica do Shared Kernel.

## Fora Do Escopo

- password no RegisterUser;
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
