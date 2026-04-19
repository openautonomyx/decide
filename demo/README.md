# Decide Platform Demo Interface

This directory contains a thin demo interface for the Decide platform, allowing visual demonstration of the end-to-end platform flow without requiring raw API calls.

## Quick Start

### Prerequisites

The demo requires the backend API to be running:

```bash
# Option 1: Using Docker Compose
docker compose up -d postgres redis app

# Option 2: Local development
# Set DATABASE_URL and REDIS_URL, then:
cd app && uvicorn main:app --reload --port 8000
```

The API should be available at `http://localhost:8000`.

### Running the Demo

1. Open `demo/index.html` in a web browser:
   - Using a local server: `python3 -m http.server 8080` then visit `http://localhost:8080/demo`
   - Or directly open the file in a browser

2. Alternative - the demo is also available at the API root:
   - With the backend running, visit `http://localhost:8000/demo/`
   - Or copy `demo/index.html` to serve statically

## Demo Workflow

The interface guides you through these steps:

1. **Select/Create Tenant** - Choose an existing tenant or create a new one
2. **Memory Setup** - Create memory spaces and add memory entries (facts, policies, instructions)
3. **Skill Setup** - Create skills and add versions
4. **Workflow Demo** - Import a workflow (JSON), validate, and run
5. **Run Detail** - View run status, resolved memory, and outputs

## Using the "Run Full Demo" Button

The simplest way to see the full flow:

1. Click **🎯 Run Full Demo** button
2. Watch the activity log as it:
   - Creates a demo tenant
   - Creates a memory space with sample entries
   - Creates a skill with version
   - Imports a sample workflow
   - Validates the workflow
   - Runs the workflow
   - Resolves memory and skills for the run

3. Click **View** on any run to see details

## API Endpoints Used

The demo interface calls these backend endpoints:

| Section | Endpoints |
|---------|---------|
| Tenants | `GET/POST /api/v1/tenants` |
| Memory | `GET/POST /api/v1/memory/spaces`, `GET/POST /api/v1/memory/entries`, `POST /api/v1/memory/resolve` |
| Skills | `GET/POST /api/v1/skills`, `GET/POST /api/v1/skills/versions`, `POST /api/v1/skills/resolve` |
| Workflows | `POST /api/v1/workflows/import/langflow`, `POST /api/v1/workflows/{id}/validate`, `POST /api/v1/workflows/{id}/run`, `GET /api/v1/workflows/{id}/runs/{run_id}` |

## Troubleshooting

- **Empty lists**: Ensure you have a tenant selected
- **API errors**: Check backend logs at `docker compose logs app -f`
- **CORS issues**: Run from same origin or configure CORS in FastAPI

## Notes

- This is a **demo interface**, not a production admin console
- Keep it thin and focused on the happy path
- Uses real API calls where available
- Some flows may require additional backend configuration