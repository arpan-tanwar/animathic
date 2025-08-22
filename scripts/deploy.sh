#!/bin/bash

# 🚀 Animathic Backend Deployment Script
# This script builds and deploys the backend to Google Cloud Run with cost optimization

set -e  # Exit on any error

echo "🚀 Starting Animathic Backend Deployment..."
echo "=========================================="

# Configuration
PROJECT_ID="animathic-backend"
REGION="us-central1"
SERVICE_NAME="animathic-backend"
IMAGE_NAME="gcr.io/animathic-backend/animathic-backend:latest"

echo "📋 Configuration:"
echo "  Project: $PROJECT_ID"
echo "  Region: $REGION"
echo "  Service: $SERVICE_NAME"
echo "  Image: $IMAGE_NAME"
echo ""

# Step 1: Build Docker Image
echo "🔨 Step 1: Building Docker Image..."
echo "   Using Cloud Build with substitutions..."
gcloud builds submit \
  --config=cloudbuild.yaml \
  --substitutions=_IMAGE=$IMAGE_NAME \
  .

echo "✅ Docker image built successfully!"
echo ""

# Step 2: Deploy to Cloud Run
echo "🚀 Step 2: Deploying to Cloud Run..."
echo "   Applying cost optimization settings..."

gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --concurrency 100 \
  --max-instances 3 \
  --min-instances 0 \
  --execution-environment gen2 \
  --cpu-throttling \
  --set-env-vars ENVIRONMENT=production,LOG_LEVEL=INFO,HOST=0.0.0.0,WORKERS=4 \
  --set-env-vars DATABASE_URL="postgresql://postgres.cclnoqiorysuciutdera:Bazinga543%21@aws-0-us-east-2.pooler.supabase.com:5432/postgres" \
  --set-env-vars SUPABASE_URL="https://cclnoqiorysuciutdera.supabase.co" \
  --set-env-vars SUPABASE_SERVICE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNjbG5vcWlvcnlzdWNpdXRkZXJhIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NzE3MzczMiwiZXhwIjoyMDYyNzQ5NzMyfQ.h6paue8vin9v9Kjk4JrqZHtIGyE5mAmPsSxQEdewACo" \
  --set-env-vars SUPABASE_NEW_BUCKET="animathic-media" \
  --set-env-vars SUPABASE_OLD_BUCKET="manim-videos" \
  --set-env-vars GOOGLE_AI_API_KEY="AIzaSyAKovoSNRWJTnM465bX9Gnc3xs8VrHlLX8" \
  --set-env-vars CLERK_SECRET_KEY="sk_live_aHeNkUGSKE1nYHpGStiVA39o9UVNul8Jgmp3NqKInJ"

echo "✅ Deployment completed successfully!"
echo ""

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

echo "🎉 Deployment Summary:"
echo "======================"
echo "✅ Build: SUCCESS"
echo "✅ Deploy: SUCCESS"
echo "🌐 Service URL: $SERVICE_URL"
echo "💰 Cost Optimized: 512Mi memory, 1 CPU, scale 0-3"
echo ""

# Test the deployment
echo "🧪 Testing deployment..."
echo "   Health check..."

# Wait a moment for service to be ready
sleep 10

# Test health endpoint
if curl -s -f "$SERVICE_URL/api/health" > /dev/null; then
    echo "✅ Health check: PASSED"
else
    echo "⚠️  Health check: Service may still be starting up"
fi

echo ""
echo "🚀 Deployment complete! Your service is now running at:"
echo "   $SERVICE_URL"
echo ""
echo "📝 To monitor logs:"
echo "   gcloud logs tail --service=$SERVICE_NAME --region=$REGION"
echo ""
echo "📝 To check service status:"
echo "   gcloud run services describe $SERVICE_NAME --region=$REGION"
