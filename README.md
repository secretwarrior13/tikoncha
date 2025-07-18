# Tikoncha Executive Shield FastAPI Project

## Overview

This repository contains the Tikoncha Executive Shield API, a FastAPI backend organized in a clean 3‑tier architecture (Models → Services → Routers).
It targets PostgreSQL, uses JWT Bearer authentication via a phone‑number/password flow, and is container‑ready with Docker
## Architecture
- **Models**: Representations of database entities.
- **Schemas**: DTOs for handling requests and responses.
- **Routers**: Act as controllers to route and handle API requests.
- **DevOps files**: Dockerfile, docker‑compose.yml, and Alembic migrations for schema control
- **Services**: Contains the business and technical logic of the application. Offers convenience helpers for performing CRUD (Create, Read, Update, Delete) operations on the database objects, keeping them distinct from the main service logic.
## Databases
PostgreSQL DSNs (sync and async) are configured in .env and parsed by app/core/config.py.
## Migrations
```python
alembic revision --autogenerate -m "Comment thatt Migration"
alembic upgrade head
```
- **Note**: The database need to be created manually before running alembic migrations.

## Authentication
OAuth2 Password grant where username=phone number.

Passwords hashed with Argon2; tokens signed with HS256 and valid for 60 minutes by default.
Roles (student, parent, teacher, etc) defined in enums. UserRole and embedded in the JWT.


### Applying Migrations
To apply migrations to the database:

```bash
alembic upgrade head
```
## Running the Application


### Command to Run the Server

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirement .
uvicorn app.main:app --reload --port 8080
```
