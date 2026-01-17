# Stock Insights Assistant

A stock insights assistant application.

## Prerequisites

- Python 3.10+
- Poetry (install from [poetry.pypa.io](https://python-poetry.org/docs/#installation))

## Setup

1. Install Poetry if you haven't already:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Install dependencies:
```bash
poetry install
```

3. Copy `.env.example` to `.env` and fill in your API keys:
```bash
cp .env.example .env
```

4. Run the application:
```bash
poetry run python -m app.main
```

## Development

Run tests:
```bash
poetry run pytest
```

Format and lint code:
```bash
poetry run ruff format .
poetry run ruff check .
```

## Docker

Build and run with Docker:
```bash
docker-compose up --build
```
