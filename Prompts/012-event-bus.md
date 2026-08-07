# Feature 001

## Etapa 6

Implementar Event Bus interno.

Implementação:

- síncrona
- in-memory
- sem Celery
- sem Redis
- sem RabbitMQ

Criar:

Protocol EventBus

Protocol EventHandler

Implementação concreta.

Criar testes para:

- registro
- publicação
- múltiplos handlers
- ordem
- exceções

Executar

pytest

mypy

ruff

Não fazer commit.