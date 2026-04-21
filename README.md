# Autonomyx Decide

Autonomyx Decide is a decision intelligence and agent orchestration platform built around a FastAPI backend, PostgreSQL, Redis, and LangFlow.

It provides a foundation for:
- decision execution APIs
- workflow orchestration
- memory and skill resolution
- framework interoperability
- agent-oriented runtime services
- demo and integration surfaces for broader Autonomyx workflows

## Current state

This repository already contains a working backend and local deployment stack, not just a concept repo.

Included today:
- FastAPI application under `app/`
- PostgreSQL and Redis local stack via Docker Compose
- Alembic migrations
- LangFlow integration
- memory APIs
- framework APIs
- demo assets
- optional side services under `services/`

The main app exposes a health endpoint and seeds default data on startup when enabled. The repository also includes a Google Cloud deployment script for Cloud Run.

## Repository structure

```text
.
├── alembic/
├── app/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── framework/
│   ├── models/
│   ├── schemas/
│   └── services/
├── configs/
├── db/migrations/
├── demo/
├── docs/
├── langflow_components/
├── services/
├── tests/
├── .env.example
├── app.Dockerfile
├── docker-compose.yml
├── deploy.sh
├── deploy-gcp.sh
└── requirements.txt
```

## Architecture

### Core services
- **FastAPI** for the Decide API
- **PostgreSQL** for persistent storage
- **Redis** for runtime and cache support
- **LangFlow** for visual orchestration
- **Optional coding services** under Docker profiles
- **Optional MCP or integration services** under Docker profiles

### Local ports
- Decide API: `http://localhost:18000`
- LangFlow: `http://localhost:17860`
- PostgreSQL: `localhost:15432`
- Redis: `localhost:16379`

## Quick start

### Local development

```bash
git clone https://github.com/openautonomyx/decide.git
cd decide
cp .env.example .env
./deploy.sh
```

After startup:
- API: `http://localhost:18000`
- API docs: `http://localhost:18000/docs`
- LangFlow: `http://localhost:17860`

### LangFlow login
Current local defaults:
- Username: `admin`
- Password: `admin123`

These values are for local development only and must be changed before any shared or production deployment.

## API basics

The app includes:
- `GET /health`
- `GET /`
- `GET /config`
- routed API modules under the configured API prefix

## Key platform areas

### Memory
The codebase includes a dedicated memory API and related platform wiring for storing and resolving memory in the Decide runtime.

### Framework interoperability
The codebase includes a framework API intended for interop between orchestration styles and imported workflow definitions.

### Demo and workflow support
The repository includes:
- `demo/`
- `langflow_components/`
- optional services for broader orchestration and coding workflows

## Docker profiles

The compose stack includes optional profile-based services.

### Coding profile
Additional coding services are defined under the `coding` profile.

```bash
docker compose --profile coding up
```

### MCP and integrations
Additional integration services are defined separately in the compose setup and can be enabled as needed.

```bash
docker compose --profile mcp up
```

## Production deployment

A Google Cloud deployment script is included for deploying the API to Cloud Run with Cloud SQL and Redis-related configuration.

Example usage pattern:

```bash
PROJECT_ID=my-project \
REGION=us-central1 \
SERVICE_NAME=decide-api \
SQL_INSTANCE=decide-sql \
DB_NAME=autonomyx \
DB_USER=autonomyx \
DB_PASSWORD=... \
SECRET_KEY=... \
./deploy-gcp.sh
```

## Important production note

This repository is **not yet production-hardened by default**.

Before production use, you should at minimum:
- replace all dev credentials and secrets
- disable debug settings
- remove development-only runtime flags
- lock down public access
- add proper authentication and authorization in front of the API
- add observability, CI or CD validation, and backup or restore procedures

## Known gaps

Current repo signals suggest the platform is still in an active buildout phase:
- README was previously outdated relative to the codebase
- local defaults include development secrets
- the container previously started `uvicorn` with `--reload`
- Cloud Run deployment could allow unauthenticated access by default unless changed
- production architecture and security expectations were not documented clearly

## Recommended next steps

1. Harden deployment defaults
2. Add authentication and authorization documentation
3. Add architecture diagram and domain model
4. Document major API groups
5. Add a production deployment guide
6. Add CI or CD checks and operational runbooks
7. Add observability and backup strategy
8. Add tenant isolation and security review notes

## License

Add your intended license here.
