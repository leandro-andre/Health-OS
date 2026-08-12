# User Aggregate

## Contexto

User pertence ao bounded context Identity e representa a identidade logica de uma pessoa dentro do Health OS.

Dados de saude nao pertencem ao User. Informacoes clinicas, perfil de saude e demais dados assistenciais devem viver em modulos proprios do dominio.

## Aggregate Root

### User

User e o Aggregate Root de Identity para a identidade logica de uma pessoa.

Responsabilidade:

- representar a identidade do usuario;
- manter sua identidade interna;
- manter seu e-mail;
- manter seu nome;
- proteger as invariantes relacionadas a identidade.

Estado implementado:

- id: UserId
- email: Email
- full_name: FullName

## Value Objects

### UserId

UserId:

- representa a identidade do User;
- encapsula UUID;
- possui igualdade por valor;
- e imutavel.

### Email

Email:

- e imutavel;
- possui igualdade por valor;
- remove whitespace externo;
- normaliza para lowercase;
- rejeita vazio;
- rejeita formatos claramente invalidos.

A unicidade de e-mail nao e responsabilidade do Value Object. A persistencia atual tambem protege essa regra com constraint unica no banco de dados.

### FullName

FullName:

- e imutavel;
- possui igualdade por valor;
- normaliza whitespace;
- rejeita vazio;
- aceita nomes com uma unica palavra;
- evita regras culturais excessivamente rigidas.

## Domain Events

### UserRegistered

UserRegistered e emitido quando um User e registrado de forma valida.

Payload implementado:

- user_id
- email

O evento preserva os metadados herdados do Shared Kernel:

- event_id
- occurred_at

## Criacao Do Aggregate

A criacao de um novo Aggregate utiliza uma factory semantica:

```python
User.register(...)
```

A criacao valida registra exatamente um UserRegistered.

## Reidratacao

User pode ser reconstituido a partir da persistencia com:

```python
User.restore(...)
```

A reidratacao recebe UserId, Email e FullName, mas nao registra UserRegistered. A persistencia concreta e responsabilidade da camada de infraestrutura.

## Persistencia

A persistencia do User foi implementada na infraestrutura com Django ORM.

- UserRepository e o contrato da camada application;
- DjangoUserRepository implementa esse contrato;
- UserModel e detalhe de infraestrutura e nao representa o dominio;
- UserModel persiste UUID como chave primaria, e-mail unico e full_name;
- reidratacao via persistencia usa User.restore(...) e nao gera UserRegistered;
- a unicidade de e-mail tambem e protegida pelo banco;
- SQLite e utilizado atualmente;
- os campos e migrations permanecem portaveis para PostgreSQL.

## Invariantes

1. User sempre possui UserId.
2. User sempre possui Email valido.
3. User sempre possui FullName valido.
4. A identidade do Aggregate nao pode ser alterada.
5. O registro valido de User produz UserRegistered.

## Alteracoes Futuras

E-mail podera ser alterado futuramente.

Nome podera ser alterado futuramente.

Essas operacoes nao fazem parte da Feature 005 atual.

Possiveis operacoes futuras:

```python
User.change_email(...)
User.change_name(...)
```

## Fora Do Escopo

- autenticacao;
- senha;
- JWT;
- OAuth;
- login social;
- recuperacao de senha;
- verificacao de e-mail;
- roles;
- permissions;
- serializers;
- endpoints;
- casos de uso;
- perfil de saude;
- dados clinicos.

## Decisoes Arquiteturais

- dominio independente de Django e DRF;
- User e Aggregate Root, nao Django Model;
- UserId, Email e FullName sao Value Objects;
- regras pertencentes ao proprio valor ficam nos Value Objects;
- regras que dependem de outros usuarios, como unicidade de e-mail, nao pertencem ao Aggregate isoladamente;
- UserRepository e um contrato da camada application;
- implementacoes concretas de persistencia pertencem a infraestrutura;
- Django ORM e detalhe de infraestrutura;
- UserModel nao representa nem substitui User;
- abstracoes prematuras devem ser evitadas.

## Status Da Feature

Feature 005 - User Repository & Persistence

- [x] Domain Design
- [x] Value Objects
- [x] User Aggregate
- [x] UserRegistered
- [x] UserRepository
- [x] UserModel
- [x] UserMapper
- [x] DjangoUserRepository
- [x] Migration inicial
- [x] Testes de integracao
- [x] Quality gates
- [x] Code Review
