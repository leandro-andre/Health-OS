# Feature 001

## Etapa 3

Implementar o módulo técnico System.

Estrutura:

health_os/modules/system

Criar endpoint

GET /api/v1/health/

Resposta:

{
    "status":"healthy",
    "service":"health-os-api",
    "version":"0.1.0",
    "checks":{
        "database":"healthy"
    }
}

Requisitos

- DRF
- verificar conexão banco
- HTTP 200
- HTTP 503 quando banco indisponível
- não expor informações sensíveis

Arquitetura

Presentation

↓

Application

↓

Infrastructure

A View deve ser extremamente fina.

Criar testes.

Executar:

pytest

python manage.py check

Não fazer commit.