#!/bin/bash

# Google Cloud Platform Deployment Script for Animathic Backend
# This script automates the complete deployment process

set -e  # Exit on any error

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

echo -e "${BLUE}🚀 Starting Animathic Backend Deployment to Google Cloud${NC}"
echo "=================================================="

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "🔍 Checking prerequisites..."

if ! command_exists gcloud; then
    print_error "Google Cloud CLI (gcloud) is not installed"
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

if ! command_exists docker; then
    print_error "Docker is not installed"
    echo "Please install Docker Desktop or Docker Engine"
    exit 1
fi

print_status "Prerequisites check passed"

# Authenticate with Google Cloud
echo "🔐 Authenticating with Google Cloud..."
gcloud auth login --no-launch-browser

# Set project
echo "📁 Setting Google Cloud project..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔌 Enabling required APIs..."
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable sqladmin.googleapis.com

print_status "All required APIs enabled"

# Configure Docker for GCR
echo "🐳 Configuring Docker for Google Container Registry..."
gcloud auth configure-docker

# Build and push Docker image
echo "🏗️  Building Docker image..."
docker build -f Dockerfile.gcp -t $IMAGE_NAME .

print_status "Docker image built successfully"

echo "📤 Pushing Docker image to Google Container Registry..."
docker push $IMAGE_NAME

print_status "Docker image pushed successfully"

# Create Cloud Storage bucket for media files
echo "🪣 Creating Cloud Storage bucket..."
gsutil mb -l $REGION gs://animathic-media || print_warning "Bucket already exists"

# Set bucket permissions
gsutil iam ch allUsers:objectViewer gs://animathic-media

print_status "Cloud Storage bucket configured"

# Create secrets in Secret Manager
echo "🔐 Setting up secrets in Secret Manager..."

# Check if secrets exist, if not create them
if ! gcloud secrets describe GOOGLE_AI_API_KEY --project=$PROJECT_ID >/dev/null 2>&1; then
    echo "Please enter your Google AI API Key:"
    read -s GOOGLE_AI_API_KEY
    echo $GOOGLE_AI_API_KEY | gcloud secrets create GOOGLE_AI_API_KEY --data-file=-
fi

if ! gcloud secrets describe SUPABASE_URL --project=$PROJECT_ID >/dev/null 2>&1; then
    echo "Please enter your Supabase URL:"
    read SUPABASE_URL
    echo $SUPABASE_URL | gcloud secrets create SUPABASE_URL --data-file=-
fi

if ! gcloud secrets describe SUPABASE_ANON_KEY --project=$PROJECT_ID >/dev/null 2>&1; then
    echo "Please enter your Supabase Anon Key:"
    read -s SUPABASE_ANON_KEY
    echo $SUPABASE_ANON_KEY | gcloud secrets create SUPABASE_ANON_KEY --data-file=-
fi

print_status "Secrets configured in Secret Manager"

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."

gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 1 \
    --timeout 300 \
    --concurrency 80 \
    --min-instances 0 \
    --max-instances 10 \
    --set-env-vars "ENVIRONMENT=production,LOG_LEVEL=INFO" \
    --set-secrets "GOOGLE_AI_API_KEY=GOOGLE_AI_API_KEY:latest,SUPABASE_URL=SUPABASE_URL:latest,SUPABASE_ANON_KEY=SUPABASE_ANON_KEY:latest"

print_status "Deployment to Cloud Run completed"

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)')

echo "=================================================="
print_status "🎉 Deployment completed successfully!"
echo "🌐 Service URL: $SERVICE_URL"
echo "📊 Health Check: $SERVICE_URL/api/health"
echo "📖 API Documentation: $SERVICE_URL/docs"
echo "=================================================="

# Test the deployment
echo "🧪 Testing deployment..."
sleep 10  # Wait for service to be ready

if curl -f "$SERVICE_URL/api/health" >/dev/null 2>&1; then
    print_status "Health check passed - service is running!"
else
    print_warning "Health check failed - service may still be starting"
fi

echo ""
echo "🔧 Next steps:"
echo "1. Update your frontend to use the new service URL"
echo "2. Configure custom domain if needed"
echo "3. Set up monitoring and logging"
echo "4. Configure auto-scaling policies"
echo ""
echo "📚 Useful commands:"
echo "  View logs: gcloud logs tail --project=$PROJECT_ID"
echo "  Update service: gcloud run services update $SERVICE_NAME --region=$REGION"
echo "  Delete service: gcloud run services delete $SERVICE_NAME --region=$REGION"
echo ""
print_status "Deployment script completed!"
