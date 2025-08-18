#!/bin/bash

# Production Deployment Script for Animathic Backend on Google Cloud
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="animathic-backend"
REGION="us-central1"
SERVICE_NAME="animathic-backend"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"
DOCKERFILE="Dockerfile.production"

echo -e "${BLUE}🚀 Starting Production Deployment to Google Cloud${NC}"
echo "=================================================="

# Check prerequisites
echo -e "${YELLOW}🔍 Checking prerequisites...${NC}"
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ Google Cloud CLI not found. Please install it first.${NC}"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found. Please install it first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"

# Authenticate with Google Cloud
echo -e "${YELLOW}🔐 Authenticating with Google Cloud...${NC}"
gcloud auth login --no-launch-browser
echo -e "${GREEN}✅ Authentication successful${NC}"

# Set project
echo -e "${YELLOW}📁 Setting Google Cloud project...${NC}"
gcloud config set project $PROJECT_ID
echo -e "${GREEN}✅ Project set to ${PROJECT_ID}${NC}"

# Enable required APIs
echo -e "${YELLOW}🔌 Enabling required APIs...${NC}"
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable storage.googleapis.com
echo -e "${GREEN}✅ All required APIs enabled${NC}"

# Configure Docker for Google Container Registry
echo -e "${YELLOW}🐳 Configuring Docker for Google Container Registry...${NC}"
gcloud auth configure-docker
echo -e "${GREEN}✅ Docker configured for GCR${NC}"

# Build production Docker image
echo -e "${YELLOW}🏗️ Building production Docker image...${NC}"
docker buildx build --platform linux/amd64 -f $DOCKERFILE -t $IMAGE_NAME .
echo -e "${GREEN}✅ Docker image built successfully${NC}"

# Push Docker image
echo -e "${YELLOW}📤 Pushing Docker image to Google Container Registry...${NC}"
docker push $IMAGE_NAME
echo -e "${GREEN}✅ Docker image pushed successfully${NC}"

# Deploy to Cloud Run
echo -e "${YELLOW}🚀 Deploying to Cloud Run...${NC}"
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 1 \
    --timeout 300 \
    --port 8080 \
    --execution-environment=gen2 \
    --cpu-boost \
    --min-instances 0 \
    --max-instances 10 \
    --set-env-vars "ENVIRONMENT=production,LOG_LEVEL=INFO" \
    --set-secrets "GOOGLE_AI_API_KEY=GOOGLE_AI_API_KEY:latest,SUPABASE_URL=SUPABASE_URL:latest,SUPABASE_ANON_KEY=SUPABASE_ANON_KEY:latest"

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)')
echo -e "${GREEN}🌐 Service URL: ${SERVICE_URL}${NC}"

# Test the service
echo -e "${YELLOW}🧪 Testing the service...${NC}"
sleep 10  # Wait for service to be ready

if curl -f "${SERVICE_URL}/api/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Service is responding correctly${NC}"
else
    echo -e "${YELLOW}⚠️ Service health check failed, but deployment succeeded${NC}"
fi

echo -e "${BLUE}🎉 Production deployment completed!${NC}"
echo -e "${BLUE}📊 Monitor your service at: https://console.cloud.google.com/run/detail/${REGION}/${SERVICE_NAME}${NC}"
echo -e "${BLUE}🔗 Service URL: ${SERVICE_URL}${NC}"
