# Health OS

Health OS is a health tracking platform built with Domain-Driven Design, Clean Architecture, and a Modular Monolith backend.

The current backend foundation includes Django, DRF, OpenAPI documentation, a technical System module, shared domain primitives, an in-memory Event Bus, security defaults, and quality gates.

## Stack

- Python 3.13
- Django 5.2 LTS
- Django REST Framework
- SQLite for local development
- django-environ
- django-cors-headers
- drf-spectacular
- pytest / pytest-django / pytest-cov
- Ruff
- mypy
- pre-commit

## Architecture

The backend follows Clean Architecture boundaries inside a modular monolith:

```text
Presentation
|
v
Application
|
v
Infrastructure
```

Domain code is framework-independent:

- Domain does not import Django.
- Domain does not import DRF.
- Application does not import Presentation.
- Application does not depend on Infrastructure.

These rules are enforced with AST-based architecture tests.

## Project Structure

```text
health-os/
|-- backend/
|   |-- config/
|   |   |-- settings/
|   |   |-- correlation.py
|   |   |-- logging.py
|   |   |-- middleware.py
|   |   |-- urls.py
|   |   |-- asgi.py
|   |   `-- wsgi.py
|   |-- health_os/
|   |   |-- modules/
|   |   |   `-- system/
|   |   |       |-- application/
|   |   |       |-- infrastructure/
|   |   |       |-- presentation/
|   |   |       `-- tests/
|   |   `-- shared/
|   |       |-- application/
|   |       |-- domain/
|   |       `-- infrastructure/
|   |-- tests/
|   `-- manage.py
|-- design/
|-- docs/
|-- infra/
|-- mobile/
|-- product/
|-- scripts/
|-- .env.example
|-- .pre-commit-config.yaml
|-- pyproject.toml
|-- requirements.txt
`-- README.md
```

## Modules

### System

Technical module responsible for operational endpoints.

Available endpoint:

```text
GET /api/v1/health/
```

Healthy response:

```json
{
  "status": "healthy",
  "service": "health-os-api",
  "version": "0.1.0",
  "checks": {
    "database": "healthy"
  }
}
```

The health check verifies database connectivity and returns HTTP `503` when the database is unavailable. It does not expose sensitive infrastructure details.

## Shared

### Shared Domain

Reusable domain primitives:

- `DomainEvent`
- `Entity`
- `DomainError`

`Entity` stores, registers, clears, and pulls domain events without depending on Django, DRF, or infrastructure.

### Event Bus

The internal Event Bus is:

- synchronous
- in-memory
- process-local
- free of Celery, Redis, and RabbitMQ

Contracts:

- `EventBus`
- `EventHandler`

Concrete implementation:

- `InMemoryEventBus`

Handlers run in registration order. Handler exceptions are propagated and stop the remaining handlers for that event publication.

## Installation

From the repository root:

```bash
python -m venv .venv
```

Activate the virtual environment:

```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a local environment file when needed:

```bash
cp .env.example .env
```

## Environment

Available settings modules:

```text
config.settings.local
config.settings.production
config.settings.test
```

Main environment variables:

```text
SECRET_KEY
DEBUG
ALLOWED_HOSTS
DATABASE_URL
CORS_ALLOWED_ORIGINS
CSRF_TRUSTED_ORIGINS
LOG_LEVEL
```

Production settings require a real `SECRET_KEY` and explicit `ALLOWED_HOSTS`.

## Running

Run migrations:

```bash
cd backend
python manage.py migrate
```

Start the development server:

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/api/v1/health/
```

## OpenAPI

OpenAPI is provided by drf-spectacular.

Schema:

```text
GET /api/v1/schema/
```

Swagger UI:

```text
GET /api/v1/docs/
```

API title:

```text
Health OS API
```

API version:

```text
0.1.0
```

## Security

Configured security foundation:

- secure production cookies
- HSTS in production
- HTTPS redirect in production
- explicit `ALLOWED_HOSTS`
- CORS allow-list
- CSRF trusted origins
- content type nosniff
- same-origin referrer policy
- correlation id middleware
- logging with correlation id

Correlation id header:

```text
X-Correlation-ID
```

## Quality

Run tests:

```bash
pytest
```

Run Ruff:

```bash
ruff check .
ruff format --check .
```

Run mypy:

```bash
mypy .
```

Run Django checks:

```bash
cd backend
python manage.py check
python manage.py makemigrations --check
```

Run deploy checks with production settings:

```bash
cd backend
python manage.py check --deploy --settings=config.settings.production
```

Run all pre-commit hooks:

```bash
pre-commit run --all-files
```
