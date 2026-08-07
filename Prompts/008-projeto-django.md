# Feature 001

## Etapa 2

Implemente somente a fundação do backend.

Objetivos:

- criar projeto Django
- configurar pyproject.toml
- configurar ambientes
- configurar SQLite
- configurar settings separados

Requisitos

Utilizar:

- Python 3.13
- Django 5.2
- DRF
- django-environ
- drf-spectacular
- pytest
- pytest-django
- Ruff
- mypy
- pre-commit

Criar:

config/settings/

- base.py
- local.py
- production.py
- test.py

Criar:

- .env.example
- pyproject.toml
- manage.py

Não implementar:

- Health Check
- Event Bus
- Domínio
- Módulos de negócio

Executar:

python manage.py check

Executar migrations.

No final apresentar:

- arquivos alterados
- decisões arquiteturais
- resultados dos testes

Não fazer commit.