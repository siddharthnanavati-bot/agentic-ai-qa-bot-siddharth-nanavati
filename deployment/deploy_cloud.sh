#!/usr/bin/env bash
# Optional Cloud Deployment Script (Section 7)
# Deploys container to Google Cloud Run or AWS App Runner
set -euo pipefail

IMAGE_TAG="gcr.io/${GCP_PROJECT_ID:-my-project}/agentic-qa-agent:latest"

echo "Building container image: ${IMAGE_TAG}..."
docker build -t "${IMAGE_TAG}" -f deployment/Dockerfile .

echo "Pushing image to registry..."
# docker push "${IMAGE_TAG}"

echo "Deploying to Cloud Run (Serverless, min instances 0)..."
# gcloud run deploy agentic-qa-agent \
#   --image "${IMAGE_TAG}" \
#   --platform managed \
#   --region us-central1 \
#   --allow-unauthenticated \
#   --memory 2Gi

echo "Deployment configuration ready. Local fallback remains primary."
