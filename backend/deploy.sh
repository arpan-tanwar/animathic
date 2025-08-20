#!/bin/bash

# Animathic Backend Production Deployment Script
# This script deploys the backend to Google Cloud Platform

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID=${GCP_PROJECT_ID:-"animathic-backend"}
REGION=${GCP_REGION:-"us-central1"}
SERVICE_NAME=${GCP_SERVICE_NAME:-"animathic-backend"}
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo -e "${BLUE}🚀 Animathic Backend Production Deployment${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}🔍 Checking prerequisites...${NC}"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ Google Cloud SDK (gcloud) is not installed${NC}"
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo "Please install Docker Desktop or Docker Engine"
    exit 1
fi

# Check if we're authenticated with gcloud
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${YELLOW}⚠️ Not authenticated with Google Cloud${NC}"
    echo "Please run: gcloud auth login"
    exit 1
fi

# Check if we have the right project
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null)
if [ "$CURRENT_PROJECT" != "$PROJECT_ID" ]; then
    echo -e "${YELLOW}⚠️ Setting project to ${PROJECT_ID}${NC}"
    gcloud config set project $PROJECT_ID
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"
echo ""

# Build and deploy
echo -e "${YELLOW}🔨 Building Docker image...${NC}"

# Build the image
docker build -f Dockerfile.gcp -t $IMAGE_NAME:$COMMIT_SHA .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Docker image built successfully${NC}"
else
    echo -e "${RED}❌ Docker build failed${NC}"
    exit 1
fi

echo ""

# Push to Container Registry
echo -e "${YELLOW}📤 Pushing image to Container Registry...${NC}"

# Configure docker to use gcloud as a credential helper
gcloud auth configure-docker

# Push the image
docker push $IMAGE_NAME:$COMMIT_SHA

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Image pushed successfully${NC}"
else
    echo -e "${RED}❌ Image push failed${NC}"
    exit 1
fi

echo ""

# Deploy to Cloud Run
echo -e "${YELLOW}🚀 Deploying to Cloud Run...${NC}"

# Deploy the service
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME:$COMMIT_SHA \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --memory 4Gi \
    --cpu 1 \
    --timeout 600 \
    --port 8080 \
    --execution-environment gen2 \
    --cpu-boost \
    --min-instances 0 \
    --max-instances 10 \
    --set-env-vars ENVIRONMENT=production,LOG_LEVEL=INFO \
    --set-secrets GOOGLE_AI_API_KEY=GOOGLE_AI_API_KEY:latest,SUPABASE_URL=SUPABASE_URL:latest,SUPABASE_ANON_KEY=SUPABASE_ANON_KEY:latest

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Deployment successful!${NC}"
else
    echo -e "${RED}❌ Deployment failed${NC}"
    exit 1
fi

echo ""

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo ""
echo -e "${BLUE}Service Information:${NC}"
echo -e "  Service Name: ${SERVICE_NAME}"
echo -e "  Region: ${REGION}"
echo -e "  URL: ${SERVICE_URL}"
echo -e "  Image: ${IMAGE_NAME}:${COMMIT_SHA}"
echo ""

# Health check
echo -e "${YELLOW}🔍 Performing health check...${NC}"

# Wait a moment for the service to be ready
sleep 10

# Test the health endpoint
HEALTH_RESPONSE=$(curl -s "${SERVICE_URL}/api/health" || echo "FAILED")

if [[ "$HEALTH_RESPONSE" == *"healthy"* ]] || [[ "$HEALTH_RESPONSE" == *"degraded"* ]]; then
    echo -e "${GREEN}✅ Health check passed${NC}"
    echo -e "Response: ${HEALTH_RESPONSE:0:200}..."
else
    echo -e "${RED}❌ Health check failed${NC}"
    echo -e "Response: ${HEALTH_RESPONSE}"
fi

echo ""
echo -e "${GREEN}🎯 Your Animathic backend is now live at: ${SERVICE_URL}${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "  1. Test the API endpoints"
echo "  2. Monitor the service logs: gcloud logs tail --service=${SERVICE_NAME}"
echo "  3. Check service status: gcloud run services describe ${SERVICE_NAME} --region=${REGION}"
echo ""
echo -e "${GREEN}Deployment script completed! 🚀${NC}"
