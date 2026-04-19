# Deploy Decide API to Google Cloud

This guide deploys the FastAPI service (`app.Dockerfile`) to **Cloud Run** with:

- **Cloud SQL (PostgreSQL)** for `DATABASE_URL`
- **Memorystore (Redis)** for `REDIS_URL`
- **Artifact Registry** for container images

## 1) One-time setup

```bash
gcloud auth login
gcloud config set project <PROJECT_ID>
```

Enable APIs:

```bash
gcloud services enable \
  run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com \
  sqladmin.googleapis.com redis.googleapis.com vpcaccess.googleapis.com
```

Create Cloud SQL instance + DB + user (example):

```bash
gcloud sql instances create decide-sql \
  --database-version=POSTGRES_16 --cpu=1 --memory=3840MiB --region=us-central1

gcloud sql databases create autonomyx --instance=decide-sql
gcloud sql users create autonomyx --instance=decide-sql --password='<DB_PASSWORD>'
```

Create a Redis instance (example):

```bash
gcloud redis instances create decide-redis \
  --size=1 --region=us-central1 --redis-version=redis_7_0 --tier=basic
```

> If Redis is private-only in your network, deploy Cloud Run with a Serverless VPC connector.

## 2) Deploy using the script

From repo root:

```bash
PROJECT_ID=<PROJECT_ID> \
REGION=us-central1 \
SERVICE_NAME=decide-api \
SQL_INSTANCE=decide-sql \
DB_NAME=autonomyx \
DB_USER=autonomyx \
DB_PASSWORD='<DB_PASSWORD>' \
SECRET_KEY='<RANDOM_SECRET>' \
./deploy-gcp.sh
```

Optional flags via env vars:

- `IMAGE_NAME` (default `decide-api`) – Artifact Registry repository name.
- `ALLOW_UNAUTHENTICATED` (`true`/`false`) – Cloud Run public access.
- `VPC_CONNECTOR` – required if your Redis/SQL networking setup needs connector egress.

## 3) Run migrations

Before production traffic, run Alembic migrations against Cloud SQL. Example pattern:

```bash
DATABASE_URL='postgresql://autonomyx:<DB_PASSWORD>@127.0.0.1:5432/autonomyx' alembic upgrade head
```

Use Cloud SQL Auth Proxy or a CI job running inside the same VPC.

## 4) Verify health

```bash
curl https://<your-cloud-run-url>/health
```

If `/health` is unavailable in your current build, verify with:

```bash
curl -I https://<your-cloud-run-url>/docs
```

## Notes

- The script auto-selects the first `READY` Redis instance in the region.
- The script configures Cloud Run for port `8000`, matching `app.Dockerfile`.
- For production, store secrets in Secret Manager and mount as env vars at deploy time.
