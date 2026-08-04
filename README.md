# Health OS

Health OS is a health tracking platform built with Domain-Driven Design, a Modular Monolith architecture, and Clean Architecture principles.

This repository currently contains only the initial project structure and a minimal Django backend.

## Stack

- Python 3.13
- Django 5.x
- Django REST Framework
- SQLite for local development

## Project Structure

```text
health-os/
|-- backend/
|   |-- config/
|   |-- modules/
|   |-- shared/
|   |-- tests/
|   `-- manage.py
|-- design/
|-- docs/
|-- infra/
|-- mobile/
|-- product/
|-- scripts/
|-- CHANGELOG.md
|-- LICENSE
|-- README.md
`-- requirements.txt
```

## Running Locally

From the repository root:

```bash
cd backend
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
pip install -r ../requirements.txt
```

Run migrations:

```bash
python manage.py migrate
```

Start the development server:

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/health/
```

Expected response:

```json
{
  "status": "ok",
  "application": "Health OS",
  "version": "0.1.0"
}
```
