# Register User

## Objetivo

RegisterUser e o caso de uso da camada application responsavel por orquestrar o registro de um novo User no bounded context Identity.

Ele nao implementa regras de infraestrutura, nao usa Django ORM, nao conhece handlers concretos de eventos e nao envolve HTTP nesta Feature.

## Input

RegisterUserInput contem apenas dados primitivos apropriados para entrada do caso de uso:

- email: str
- full_name: str

O UserId nao e fornecido pelo cliente. Ele e gerado pelo caso de uso atraves de uma dependencia explicita.

## Output

RegisterUserOutput retorna:

- user_id: UserId

O output nao expoe User Aggregate, Django Model, Event Bus concreto ou qualquer objeto de infraestrutura.

## Dependencias

RegisterUser recebe explicitamente:

- UserRepository;
- UserIdGenerator;
- EventBus.

UserRepository e o contrato de persistencia da camada application.

UserIdGenerator e um contrato pequeno e testavel para gerar UserId. Implementacoes concretas permanecem fora do dominio.

EventBus e o contrato da camada shared application. A implementacao concreta atual e sincrona, process-local e in-memory, mas permanece fora da camada application.

## Fluxo

1. Validar Email e FullName criando os Value Objects.
2. Verificar se ja existe User com o e-mail informado.
3. Gerar UserId.
4. Criar o Aggregate com User.register(...).
5. Persistir User via UserRepository.add(user).
6. Publicar os Domain Events produzidos pelo Aggregate.
7. Retornar RegisterUserOutput.

## Email Existente

Email continua responsavel apenas por validade e normalizacao do valor.

RegisterUser consulta UserRepository.get_by_email(...) depois de criar o Value Object Email. Se ja existir User para o e-mail normalizado, o caso de uso levanta UserAlreadyExistsError.

Nesse cenario:

- UserId nao e gerado;
- UserRepository.add(...) nao e chamado;
- nenhum Domain Event e publicado.

A constraint unica do banco continua sendo a ultima linha de defesa contra duplicidade.

## Persistencia

Persistencia acontece antes da publicacao dos eventos.

RegisterUser persiste o Aggregate com UserRepository.add(user). A implementacao concreta pode usar Django ORM, mas isso e detalhe de infraestrutura.

## Domain Events

UserRegistered nasce no dominio durante User.register(...).

RegisterUser nao instancia UserRegistered diretamente e nao conhece detalhes especificos desse evento. O caso de uso apenas publica os eventos pendentes produzidos pelo Aggregate, preservando a ordem em que foram registrados.

Depois de uma publicacao bem-sucedida, os eventos pendentes sao removidos do Aggregate usando a API publica do Shared Kernel.

## Falhas

Se UserRepository.add(user) falhar, nenhum evento e publicado.

Se um handler do Event Bus falhar, a excecao e propagada ao chamador. Nao ha retry, compensacao, fila, Outbox ou Unit of Work nesta Feature.

Persistencia e publicacao ainda nao possuem garantia transacional distribuida ou atomica.

## Limitacoes Atuais

- Event Bus e sincrono e process-local;
- persistencia e publicacao nao possuem Outbox;
- HTTP ainda nao faz parte desta Feature;
- nao ha handler real de UserRegistered nesta Feature.

## Fora Do Escopo

- HTTP;
- serializer;
- endpoint;
- autenticacao;
- senha;
- JWT;
- OAuth;
- login;
- confirmacao de email;
- envio de e-mail;
- handler real de UserRegistered;
- Outbox;
- Unit of Work;
- retry;
- filas;
- alteracao de User.

## Status Da Feature

Feature 006 - Register User Use Case

- [x] RegisterUserInput
- [x] RegisterUserOutput
- [x] UserIdGenerator
- [x] UserAlreadyExistsError
- [x] verificacao de e-mail existente
- [x] criacao do User Aggregate
- [x] persistencia via UserRepository
- [x] publicacao de Domain Events via EventBus
- [x] limpeza de eventos apos publicacao bem-sucedida
- [x] teste unitario
- [x] teste integrado minimo
- [x] Quality gates
- [x] Code Review
