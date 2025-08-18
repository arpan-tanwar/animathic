# Animathic Backend - Google Cloud Deployment Guide

## 🚀 Overview

This guide covers deploying the Animathic Backend to Google Cloud Platform (GCP) using Cloud Run. The backend is optimized for production use with auto-scaling, monitoring, and security features.

## 🏗️ Architecture

- **Platform**: Google Cloud Run (serverless)
- **Container**: Python 3.12 + FastAPI
- **Database**: Supabase (PostgreSQL)
- **Storage**: Supabase Storage + Google Cloud Storage
- **AI**: Google Gemini API
- **Monitoring**: Google Cloud Monitoring + Logging

## 📋 Prerequisites

1. **Google Cloud Account** with billing enabled
2. **Google Cloud CLI** installed and configured
3. **Docker** installed and running
4. **Python 3.12+** for local development

## 🔧 Setup

### 1. Install Google Cloud CLI

```bash
# macOS
brew install google-cloud-sdk

# Or download from: https://cloud.google.com/sdk/docs/install
```

### 2. Authenticate and Configure

```bash
# Login to Google Cloud
gcloud auth login

# Set your project
gcloud config set project animathic-backend

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable storage.googleapis.com
```

### 3. Configure Environment

```bash
# Copy environment template
cp env.template .env

# Edit .env with your values
nano .env
```

## 🚀 Deployment

### Option 1: Automated Deployment Script

```bash
# Make script executable
chmod +x deploy_gcp_production.sh

# Run deployment
./deploy_gcp_production.sh
```

### Option 2: Manual Deployment

```bash
# Build for AMD64 (required for Cloud Run)
docker buildx build --platform linux/amd64 -f Dockerfile.production -t gcr.io/animathic-backend/animathic-backend .

# Push to Google Container Registry
docker push gcr.io/animathic-backend/animathic-backend

# Deploy to Cloud Run
gcloud run deploy animathic-backend \
    --image gcr.io/animathic-backend/animathic-backend \
    --platform managed \
    --region us-central1 \
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
```

### Option 3: Cloud Build (CI/CD)

```bash
# Trigger build from source
gcloud builds submit --config cloudbuild.yaml
```

## 🔐 Secrets Management

### Create Secrets in Secret Manager

```bash
# Google AI API Key
echo -n "your_google_ai_api_key" | gcloud secrets create GOOGLE_AI_API_KEY --data-file=-

# Supabase URL
echo -n "https://your-project.supabase.co" | gcloud secrets create SUPABASE_URL --data-file=-

# Supabase Anon Key
echo -n "your_supabase_anon_key" | gcloud secrets create SUPABASE_ANON_KEY --data-file=-
```

### Update Secrets

```bash
# Update existing secret
echo -n "new_value" | gcloud secrets versions add SECRET_NAME --data-file=-
```

## 📊 Monitoring & Logging

### View Logs

```bash
# View service logs
gcloud run services logs read animathic-backend --region=us-central1

# Stream logs
gcloud run services logs tail animathic-backend --region=us-central1
```

### Monitoring Dashboard

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to Monitoring > Dashboards
3. Import the `monitoring.yaml` configuration

### Set Up Alerts

```bash
# Apply monitoring configuration
gcloud monitoring policies create --policy-from-file=monitoring.yaml
```

## 🔄 Continuous Deployment

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Google Cloud

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Google Cloud CLI
        uses: google-github-actions/setup-gcloud@v1
        with:
          project_id: ${{ secrets.GCP_PROJECT_ID }}
          service_account_key: ${{ secrets.GCP_SA_KEY }}
          
      - name: Deploy to Cloud Run
        run: |
          gcloud builds submit --config cloudbuild.yaml
```

## 🧪 Testing

### Local Testing

```bash
# Test with production Dockerfile
docker build -f Dockerfile.production -t animathic-test .
docker run -p 8080:8080 -e PORT=8080 animathic-test

# Test endpoints
curl http://localhost:8080/
curl http://localhost:8080/api/health
```

### Production Testing

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe animathic-backend --region=us-central1 --format='value(status.url)')

# Test endpoints
curl $SERVICE_URL/
curl $SERVICE_URL/api/health
```

## 📈 Scaling & Performance

### Auto-scaling Configuration

- **Min Instances**: 0 (scale to zero)
- **Max Instances**: 10
- **CPU**: 1 vCPU
- **Memory**: 2GB
- **Concurrency**: 80 requests per instance

### Performance Tuning

```bash
# Increase memory for heavy workloads
gcloud run services update animathic-backend \
    --memory 4Gi \
    --region us-central1

# Enable CPU boost for faster startup
gcloud run services update animathic-backend \
    --cpu-boost \
    --region us-central1
```

## 🔒 Security

### IAM Roles

```bash
# Grant Cloud Run service account access to secrets
gcloud projects add-iam-policy-binding animathic-backend \
    --member="serviceAccount:4734151242-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

### Network Security

- **HTTPS Only**: Enabled by default
- **Authentication**: Optional (can be enabled)
- **VPC**: Can be configured for private access

## 💰 Cost Optimization

### Resource Optimization

- **Scale to Zero**: Automatically scales down when not in use
- **Memory**: Start with 2GB, adjust based on usage
- **CPU**: 1 vCPU is sufficient for most workloads
- **Instances**: Limit max instances to control costs

### Monitoring Costs

```bash
# View Cloud Run costs
gcloud billing accounts list
gcloud billing projects describe animathic-backend
```

## 🚨 Troubleshooting

### Common Issues

1. **Container Won't Start**
   - Check logs: `gcloud run services logs read animathic-backend`
   - Verify Dockerfile builds locally
   - Check environment variables

2. **Secrets Not Found**
   - Verify secrets exist in Secret Manager
   - Check IAM permissions
   - Ensure secret names match deployment

3. **High Latency**
   - Enable CPU boost
   - Increase memory allocation
   - Check application performance

### Debug Commands

```bash
# Service status
gcloud run services describe animathic-backend --region=us-central1

# Revision details
gcloud run revisions list --service=animathic-backend --region=us-central1

# Service logs
gcloud run services logs read animathic-backend --region=us-central1 --limit=50
```

## 📚 Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Container Registry](https://cloud.google.com/container-registry)
- [Secret Manager](https://cloud.google.com/secret-manager)
- [Cloud Monitoring](https://cloud.google.com/monitoring)
- [Cloud Build](https://cloud.google.com/cloud-build)

## 🆘 Support

For issues specific to this deployment:

1. Check the troubleshooting section above
2. Review Cloud Run logs
3. Check Google Cloud Console for errors
4. Verify environment configuration

---

**Happy Deploying! 🚀**
