# Setup Guide

## Requirements

- Docker Desktop
- Docker Compose
- Git

## Repository setup

Clone the repository and prepare the environment file:

```bash
cp infra/.env.example infra/.env
```

## Start the current stack

From the `infra` directory run:

```bash
docker compose up --build
```

## Available endpoints

- Auth API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## Database migrations

Migrations are stored in each service using Alembic.

Required Alembic files:
- `alembic.ini`
- `alembic/env.py`
- `alembic/script.py.mako`
- `alembic/versions/*.py`

If the service is configured to run migrations automatically, the container should
execute:

```bash
alembic upgrade head
```

before starting the application server.

## Manual migration commands

### Upgrade to the latest revision
```bash
docker compose run --rm api alembic upgrade head
```

## Troubleshooting

### Alembic files are missing
Make sure the service repository contains:
- `alembic.ini`
- `alembic/env.py`
- `alembic/script.py.mako`

Without these files, Alembic cannot run.

### Docker cannot connect to the database
Check:
- `docker compose` is running
- database environment variables are correct
- the service uses the correct `DATABASE_URL`

### Port already in use
Stop the process using the port or change the mapping in `docker-compose.yml`.

## Notes for contributors

- Do not commit secret `.env` files.
- Commit `.env.example` instead.
- Keep service boundaries strict.
- Do not share database tables across services.