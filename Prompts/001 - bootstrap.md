Você é um Staff Software Engineer.

Vamos iniciar um novo projeto chamado Health OS.

Objetivo:
Construir uma plataforma de acompanhamento de saúde baseada em Domain-Driven Design, Modular Monolith e Clean Architecture.

Tecnologias:

- Python 3.13
- Django 5.x
- Django REST Framework
- SQLite (apenas para desenvolvimento)
- Git
- VS Code

NÃO utilizar Docker por enquanto.

Quero que você apenas prepare a estrutura inicial do projeto.

Crie:

health-os/
│
├── backend/
├── docs/
├── mobile/
├── design/
├── infra/
├── product/
├── scripts/
│
├── README.md
├── .gitignore
├── LICENSE
└── CHANGELOG.md

Dentro de backend:

- criar projeto Django
- criar pasta config
- organizar settings
- criar estrutura modular

backend/
│
├── config/
├── modules/
├── shared/
├── tests/
└── manage.py

Ainda NÃO criar nenhuma regra de negócio.

Não criar Models.

Não criar APIs.

Não criar autenticação.

Apenas preparar uma estrutura profissional.

Ao final:

- projeto deve executar com `python manage.py runserver`
- migrations padrão do Django devem funcionar
- criar endpoint `/health/` retornando:

{
    "status": "ok",
    "application": "Health OS",
    "version": "0.1.0"
}

Gerar também um README inicial explicando como executar o projeto.