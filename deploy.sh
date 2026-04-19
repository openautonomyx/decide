#!/bin/bash
# Deploy Decide Platform with LangFlow
# Usage: ./deploy.sh [--skip-build]

set -e

SKIP_BUILD=false
if [ "$1" == "--skip-build" ]; then
  SKIP_BUILD=true
fi

echo "=== Deploying Decide Platform ==="

# Start infrastructure
echo "Starting PostgreSQL and Redis..."
docker compose up -d postgres redis

# Wait for postgres
echo "Waiting for PostgreSQL..."
sleep 5
until docker compose exec -T postgres pg_isready -U autonomyx; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

# Build Decide app if not skipped
if [ "$SKIP_BUILD" == "false" ]; then
  echo "Building Decide app..."
  docker compose build app
fi

# Start Decide app
echo "Starting Decide API..."
docker compose up -d app

# Start LangFlow
echo "Starting LangFlow..."
docker compose up -d langflow

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Services:"
echo "  Decide API:     http://localhost:18000"
echo "  LangFlow:      http://localhost:17860"
echo "  PostgreSQL:     localhost:15432"
echo "  Redis:         localhost:16379"
echo ""
echo "LangFlow Credentials:"
echo "  User:     admin"
echo "  Password: admin123"
echo ""
echo "To import the flow:"
echo "  1. Open http://localhost:17860"
echo "  2. Login with admin/admin123"
echo "  3. Go to Flows → Import"
echo "  4. Select langflow_components/decide/agent_orchestrator_flow.json"