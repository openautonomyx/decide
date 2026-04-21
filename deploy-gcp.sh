#!/usr/bin/env bash
set -euo pipefail

# Deploy Decide API to Google Cloud Run with Cloud SQL (Postgres) and optional VPC access.
#
# Required env vars:
# PROJECT_ID, REGION, SERVICE_NAME, SQL_INSTANCE, DB_NAME, DB_USER, DB_PASSWORD, SECRET_KEY
#
# Optional env vars:
# IMAGE_NAME (default: decide-api)
# VPC_CONNECTOR
# SERVICE_ACCOUNT
# ALLOW_UNAUTHENTICATED (default: false)
# MIN_INSTANCES (default: 0)
# MAX_INSTANCES (default: 4)
# MEMORY (default: 1Gi)
# CPU (default: 1)
# ENVIRONMENT (default: prod)

required_vars=(
  PROJECT_ID
  REGION
  SERVICE_NAME
  SQL_INSTANCE
  DB_NAME
  DB_USER
  DB_PASSWORD
  SECRET_KEY
)

for var in "${required_vars[@]}"; do
  if [[ -z "${!var:-}" ]]; then
    echo "Missing required env var: ${var}" >&2
    exit 1
  fi
done

IMAGE_NAME="${IMAGE_NAME:-decide-api}"
ALLOW_UNAUTHENTICATED="${ALLOW_UNAUTHENTICATED:-false}"
MIN_INSTANCES="${MIN_INSTANCES:-0}"
MAX_INSTANCES="${MAX_INSTANCES:-4}"
MEMORY="${MEMORY:-1Gi}"
CPU="${CPU:-1}"
ENVIRONMENT="${ENVIRONMENT:-prod}"

if ! command -v gcloud >/dev/null 2>&1; then
  echo "gcloud CLI is required." >&2
  exit 1
fi

if ! gcloud auth list --filter=status:ACTIVE --format='value(account)' | grep -q .; then
  echo "No active gcloud auth session. Run: gcloud auth login" >&2
  exit 1
fi

gcloud config set project "${PROJECT_ID}" >/dev/null

SQL_CONNECTION_NAME="${PROJECT_ID}:${REGION}:${SQL_INSTANCE}"
IMAGE_URI="${REGION}-docker.pkg.dev/${PROJECT_ID}/${IMAGE_NAME}/${SERVICE_NAME}:$(date +%Y%m%d-%H%M%S)"

REDIS_HOST="$(gcloud redis instances list --region="${REGION}" --format='value(host)' --filter='state:READY' | head -n 1)"
if [[ -z "${REDIS_HOST}" ]]; then
  echo "No READY Redis instance found in ${REGION}. Create one or set REDIS_URL manually after deploy." >&2
  exit 1
fi

REDIS_URL="redis://${REDIS_HOST}:6379"
DATABASE_URL="postgresql://${DB_USER}:${DB_PASSWORD}@/${DB_NAME}?host=/cloudsql/${SQL_CONNECTION_NAME}"

if [[ ${#SECRET_KEY} -lt 32 ]]; then
  echo "SECRET_KEY should be at least 32 characters for production deployments." >&2
  exit 1
fi

echo "Enabling required APIs..."
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  sqladmin.googleapis.com \
  redis.googleapis.com \
  secretmanager.googleapis.com \
  vpcaccess.googleapis.com >/dev/null

echo "Ensuring Artifact Registry repository ${IMAGE_NAME} exists..."
if ! gcloud artifacts repositories describe "${IMAGE_NAME}" --location "${REGION}" >/dev/null 2>&1; then
  gcloud artifacts repositories create "${IMAGE_NAME}" \
    --repository-format=docker \
    --location="${REGION}" \
    --description="Decide API container images"
fi

echo "Building image ${IMAGE_URI}..."
gcloud builds submit --tag "${IMAGE_URI}" .

echo "Deploying ${SERVICE_NAME} to Cloud Run..."
DEPLOY_ARGS=(
  run deploy "${SERVICE_NAME}"
  --image "${IMAGE_URI}"
  --region "${REGION}"
  --platform managed
  --set-env-vars "DATABASE_URL=${DATABASE_URL},REDIS_URL=${REDIS_URL},SECRET_KEY=${SECRET_KEY},DEBUG=false,ENVIRONMENT=${ENVIRONMENT},SEED_ON_STARTUP=false"
  --add-cloudsql-instances "${SQL_CONNECTION_NAME}"
  --port 8000
  --min-instances "${MIN_INSTANCES}"
  --max-instances "${MAX_INSTANCES}"
  --memory "${MEMORY}"
  --cpu "${CPU}"
)

if [[ -n "${VPC_CONNECTOR:-}" ]]; then
  DEPLOY_ARGS+=(--vpc-connector "${VPC_CONNECTOR}" --egress-settings all)
fi

if [[ -n "${SERVICE_ACCOUNT:-}" ]]; then
  DEPLOY_ARGS+=(--service-account "${SERVICE_ACCOUNT}")
fi

if [[ "${ALLOW_UNAUTHENTICATED}" == "true" ]]; then
  DEPLOY_ARGS+=(--allow-unauthenticated)
else
  DEPLOY_ARGS+=(--no-allow-unauthenticated)
fi

gcloud "${DEPLOY_ARGS[@]}"

URL="$(gcloud run services describe "${SERVICE_NAME}" --region "${REGION}" --format='value(status.url)')"

echo ""
echo "Deployment complete: ${URL}"
echo "Remember to run database migrations against Cloud SQL before production traffic."
