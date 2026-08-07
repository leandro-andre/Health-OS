# User Aggregate

## Contexto

User pertence ao bounded context Identity e representa a identidade lógica de uma pessoa dentro do Health OS.

Dados de saúde não pertencem ao User. Informações clínicas, perfil de saúde e demais dados assistenciais devem viver em módulos próprios do domínio.

## Aggregate Root

### User

Responsabilidade:

- representar a identidade do usuário;
- manter sua identidade interna;
- manter seu e-mail;
- manter seu nome;
- proteger as invariantes relacionadas à identidade.

Estado inicialmente planejado:

- id: UserId
- email: Email
- full_name: FullName

## Value Objects

### UserId

UserId:

- representa a identidade do User;
- encapsula UUID;
- possui igualdade por valor;
- é imutável.

### Email

Email:

- é imutável;
- possui igualdade por valor;
- remove whitespace externo;
- normaliza para lowercase;
- rejeita vazio;
- rejeita formatos claramente inválidos.

A unicidade de e-mail não é responsabilidade do Value Object. Essa regra será tratada posteriormente na camada apropriada, pois depende de outros usuários.

### FullName

FullName:

- é imutável;
- possui igualdade por valor;
- normaliza whitespace;
- rejeita vazio;
- aceita nomes com uma única palavra;
- evita regras culturais excessivamente rígidas.

## Domain Events

Evento planejado:

### UserRegistered

Payload inicialmente planejado:

- user_id
- email

UserRegistered será implementado na próxima etapa da Feature 004.

## Criação do Aggregate

A decisão planejada é utilizar uma factory semântica:

```python
User.register(...)
```

A criação válida deverá registrar UserRegistered.

Essa implementação ocorrerá na próxima etapa da Feature 004.

## Invariantes

1. User sempre possui UserId.
2. User sempre possui Email válido.
3. User sempre possui FullName válido.
4. A identidade do Aggregate não pode ser alterada.
5. O registro válido de User deverá produzir UserRegistered.

## Alterações Futuras

E-mail poderá ser alterado futuramente.

Nome poderá ser alterado futuramente.

Essas operações não fazem parte da Feature 004 atual.

Possíveis operações futuras:

```python
User.change_email(...)
User.change_name(...)
```

## Fora Do Escopo

- autenticação;
- senha;
- JWT;
- OAuth;
- login social;
- recuperação de senha;
- verificação de e-mail;
- roles;
- permissions;
- persistência Django;
- repositories;
- serializers;
- endpoints;
- casos de uso;
- perfil de saúde;
- dados clínicos.

## Decisões Arquiteturais

- domínio independente de Django e DRF;
- User é Aggregate Root, não Django Model;
- UserId, Email e FullName são Value Objects;
- regras pertencentes ao próprio valor ficam nos Value Objects;
- regras que dependem de outros usuários, como unicidade de e-mail, não pertencem ao Aggregate isoladamente;
- abstrações prematuras devem ser evitadas.

## Status Da Feature

Feature 004 — User Aggregate

- [x] Domain Design
- [x] Value Objects
- [ ] User Aggregate
- [ ] UserRegistered
- [ ] Testes finais
- [ ] Quality gates
- [ ] Code Review
