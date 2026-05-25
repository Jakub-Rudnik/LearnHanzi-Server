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

### New auth/user endpoints

- `POST /auth/register` - register new user
- `POST /auth/login` - login user
- `POST /auth/refresh` - refresh access token
- `POST /auth/logout` - logout user
- `GET /auth/me` - get current user
- `GET /auth/session` - get current session with token claims
- `POST /auth/password-reset/request` - request password reset (forgotten password)
- `POST /auth/password-reset/confirm` - confirm password reset using token
- `POST /auth/password` - change password for logged-in user
- `PATCH /users/me` - edit profile (`username`, `email`)
- `GET /users/{user_id}/basic` - basic user data for logged-in users (`id`, `username`, `account_status`)
- `GET /users/{user_id}/identity` - full user identity for logged-in users

### Password reset vs password change

- **Password reset** (`POST /auth/password-reset/request` + `/confirm`):
  - User forgot their password
  - Can be done without authentication
  - Email with reset link is sent (or token returned in debug mode)
  - Token is valid for 30 minutes (configurable)

- **Password change** (`POST /auth/password`):
  - Logged-in user wants to change their password
  - Requires current password verification
  - Invalidates all refresh tokens (user must login again on all devices)
  - No email sent

- By default (`PASSWORD_RESET_DEBUG_RETURN_TOKEN=true`) reset token is returned in API response from `POST /auth/password-reset/request` for local development.
- To use real e-mail delivery, configure SMTP variables in `services/auth-service/.env`.
- For Gmail, use an **app password** (not your normal login password) and set:

```dotenv
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-address@gmail.com
SMTP_PASSWORD=your-google-app-password
SMTP_FROM_EMAIL=your-address@gmail.com
SMTP_STARTTLS=true
PASSWORD_RESET_DEBUG_RETURN_TOKEN=false
```

- `SMTP_FROM_EMAIL` can be omitted in code; if left empty, the service uses `SMTP_USER` as the sender.
- For local Docker testing without a real mailbox, you can run MailHog/Mailpit and point `SMTP_HOST` + `SMTP_PORT` to that container.

### Profile editing

- `PATCH /users/me` - update logged-in user's profile:
  - `username` - must be unique and 3-50 characters
  - `email` - must be unique and valid email format
  - Both fields are optional; if omitted, they won't be updated
  - Returns updated user data

- `GET /users/{user_id}/basic` - get basic user data (for ranking service):
  - Returns: `id`, `username`, `account_status`
  - Requires authentication
  - Can access any user's basic data

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