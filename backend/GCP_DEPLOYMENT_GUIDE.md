# 🚀 Complete Guide: Deploy Animathic Backend to Google Cloud Platform

This guide will walk you through deploying your Animathic backend from Render to Google Cloud Platform using Cloud Run.

## 📋 **Prerequisites**

### Required Software
- [Google Cloud CLI (gcloud)](https://cloud.google.com/sdk/docs/install)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) or Docker Engine
- [Git](https://git-scm.com/downloads)

### Required Accounts
- Google Cloud account with billing enabled
- Access to Google Cloud Console

---

## **Step 1: Google Cloud Project Setup**

### 1.1 Install Google Cloud CLI

**macOS:**
```bash
brew install google-cloud-sdk
```

**Windows:**
Download from [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)

**Linux:**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

### 1.2 Initialize Google Cloud

```bash
# Login to Google Cloud
gcloud auth login

# Create new project (or use existing)
gcloud projects create animathic-backend --name="Animathic Backend"

# Set as default project
gcloud config set project animathic-backend

# Enable billing (required for deployment)
# Go to: https://console.cloud.google.com/billing
# Link your billing account to the project
```

### 1.3 Enable Required APIs

```bash
# Enable Cloud Run API
gcloud services enable run.googleapis.com

# Enable Cloud Build API
gcloud services enable cloudbuild.googleapis.com

# Enable Container Registry API
gcloud services enable containerregistry.googleapis.com

# Enable Cloud Storage API
gcloud services enable storage.googleapis.com

# Enable Secret Manager API
gcloud services enable secretmanager.googleapis.com

# Enable Cloud SQL API (if using database)
gcloud services enable sqladmin.googleapis.com
```

---

## **Step 2: Prepare Your Backend Code**

### 2.1 Update Configuration

Your backend is already prepared with GCP-specific files:
- `config_gcp.py` - GCP configuration
- `Dockerfile.gcp` - GCP-optimized Dockerfile
- `deploy_gcp.sh` - Automated deployment script
- `cloudbuild.yaml` - Cloud Build configuration

### 2.2 Test GCP Configuration

```bash
cd backend
python config_gcp.py
```

This should display your GCP configuration settings.

---

## **Step 3: Set Up Secrets and Environment Variables**

### 3.1 Create Secrets in Secret Manager

```bash
# Set your project ID
PROJECT_ID="animathic-backend"

# Create Google AI API Key secret
echo "your_google_ai_api_key_here" | gcloud secrets create GOOGLE_AI_API_KEY --data-file=-

# Create Supabase URL secret
echo "your_supabase_url_here" | gcloud secrets create SUPABASE_URL --data-file=-

# Create Supabase Anon Key secret
echo "your_supabase_anon_key_here" | gcloud secrets create SUPABASE_ANON_KEY --data-file=-
```

### 3.2 Verify Secrets

```bash
# List all secrets
gcloud secrets list

# View a specific secret (metadata only)
gcloud secrets describe GOOGLE_AI_API_KEY
```

---

## **Step 4: Deploy to Google Cloud**

### 4.1 Automated Deployment (Recommended)

```bash
# Make the deployment script executable
chmod +x deploy_gcp.sh

# Run the deployment script
./deploy_gcp.sh
```

The script will:
- ✅ Check prerequisites
- ✅ Authenticate with Google Cloud
- ✅ Enable required APIs
- ✅ Build and push Docker image
- ✅ Create Cloud Storage bucket
- ✅ Deploy to Cloud Run
- ✅ Test the deployment

### 4.2 Manual Deployment

If you prefer manual deployment:

```bash
# Configure Docker for Google Container Registry
gcloud auth configure-docker

# Build Docker image
docker build -f Dockerfile.gcp -t gcr.io/animathic-backend/animathic-backend .

# Push to Container Registry
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
    --concurrency 80 \
    --min-instances 0 \
    --max-instances 10 \
    --set-env-vars "ENVIRONMENT=production,LOG_LEVEL=INFO" \
    --set-secrets "GOOGLE_AI_API_KEY=GOOGLE_AI_API_KEY:latest,SUPABASE_URL=SUPABASE_URL:latest,SUPABASE_ANON_KEY=SUPABASE_ANON_KEY:latest"
```

---

## **Step 5: Post-Deployment Setup**

### 5.1 Get Your Service URL

```bash
# Get the service URL
gcloud run services describe animathic-backend --region=us-central1 --format='value(status.url)'
```

### 5.2 Test Your Deployment

```bash
# Test health endpoint
curl https://your-service-url/api/health

# Test API documentation
curl https://your-service-url/docs
```

### 5.3 Set Up Cloud Storage for Media Files

```bash
# Create storage bucket (if not already created)
gsutil mb -l us-central1 gs://animathic-media

# Set bucket permissions for public read access to media files
gsutil iam ch allUsers:objectViewer gs://animathic-media

# Create folders for different media types
gsutil mkdir gs://animathic-media/images
gsutil mkdir gs://animathic-media/videos
gsutil mkdir gs://animathic-media/temp
```

---

## **Step 6: Configure Continuous Deployment (Optional)**

### 6.1 Set Up Cloud Build Triggers

```bash
# Create a trigger for automatic deployment on Git push
gcloud builds triggers create github \
    --repo-name=animathic \
    --repo-owner=your-github-username \
    --branch-pattern="^main$" \
    --build-config=cloudbuild.yaml
```

### 6.2 Test Automated Deployment

```bash
# Push a change to trigger build
git push origin main

# Monitor the build
gcloud builds log --stream
```

---

## **Step 7: Monitoring and Maintenance**

### 7.1 View Logs

```bash
# View Cloud Run logs
gcloud logs tail --project=animathic-backend

# View specific service logs
gcloud logs tail --project=animathic-backend --filter="resource.type=cloud_run_revision"
```

### 7.2 Monitor Performance

```bash
# View service metrics
gcloud run services describe animathic-backend --region=us-central1

# Check resource usage
gcloud run services describe animathic-backend --region=us-central1 --format='value(spec.template.spec.containers[0].resources)'
```

### 7.3 Update Your Service

```bash
# Update environment variables
gcloud run services update animathic-backend \
    --region=us-central1 \
    --set-env-vars "LOG_LEVEL=DEBUG"

# Update secrets
gcloud run services update animathic-backend \
    --region=us-central1 \
    --set-secrets "NEW_SECRET=NEW_SECRET:latest"
```

---

## **Step 8: Update Frontend Configuration**

### 8.1 Update API Endpoint

In your frontend code, update the API base URL:

```typescript
// Before (Render)
const API_BASE_URL = 'https://your-render-app.onrender.com';

// After (Google Cloud)
const API_BASE_URL = 'https://your-cloud-run-service-url';
```

### 8.2 Update CORS Settings

If you need to update CORS settings in your backend:

```python
# In your main.py, update CORS origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend-domain.com",
        "http://localhost:3000",  # For local development
    ],
    # ... other settings
)
```

---

## **Step 9: Cost Optimization**

### 9.1 Monitor Costs

```bash
# View current month's cost
gcloud billing accounts list

# Set up billing alerts in Google Cloud Console
# Go to: https://console.cloud.google.com/billing
```

### 9.2 Optimize Resources

```bash
# Reduce memory if not needed
gcloud run services update animathic-backend \
    --region=us-central1 \
    --memory=1Gi

# Reduce CPU if not needed
gcloud run services update animathic-backend \
    --region=us-central1 \
    --cpu=0.5
```

---

## **Step 10: Troubleshooting**

### Common Issues and Solutions

#### Issue: Service won't start
```bash
# Check logs
gcloud logs tail --project=animathic-backend

# Check service status
gcloud run services describe animathic-backend --region=us-central1
```

#### Issue: Secrets not accessible
```bash
# Verify secrets exist
gcloud secrets list

# Check service has access to secrets
gcloud run services describe animathic-backend --region=us-central1 --format='value(spec.template.spec.containers[0].env)'
```

#### Issue: High costs
```bash
# Reduce instance count
gcloud run services update animathic-backend \
    --region=us-central1 \
    --max-instances=5

# Set min instances to 0 for cost savings
gcloud run services update animathic-backend \
    --region=us-central1 \
    --min-instances=0
```

---

## **🚀 Deployment Checklist**

- [ ] Google Cloud CLI installed
- [ ] Google Cloud project created
- [ ] Billing enabled
- [ ] Required APIs enabled
- [ ] Secrets created in Secret Manager
- [ ] Docker image built and pushed
- [ ] Service deployed to Cloud Run
- [ ] Health check passed
- [ ] Frontend updated with new URL
- [ ] CORS configured
- [ ] Monitoring set up
- [ ] Cost alerts configured

---

## **📚 Useful Commands Reference**

```bash
# Service management
gcloud run services list --region=us-central1
gcloud run services describe animathic-backend --region=us-central1
gcloud run services update animathic-backend --region=us-central1
gcloud run services delete animathic-backend --region=us-central1

# Logs and monitoring
gcloud logs tail --project=animathic-backend
gcloud logging read "resource.type=cloud_run_revision" --limit=50

# Secrets management
gcloud secrets list
gcloud secrets create SECRET_NAME --data-file=-
gcloud secrets delete SECRET_NAME

# Storage management
gsutil ls gs://animathic-media
gsutil cp local-file gs://animathic-media/
gsutil rm gs://animathic-media/file-name
```

---

## **🎯 Next Steps After Deployment**

1. **Set up monitoring** with Google Cloud Monitoring
2. **Configure alerts** for errors and high costs
3. **Set up custom domain** if needed
4. **Implement CI/CD** with Cloud Build
5. **Set up backup strategies** for your data
6. **Monitor performance** and optimize resources
7. **Set up logging** and error tracking

---

## **💡 Tips for Success**

- **Start small**: Use minimal resources initially and scale up as needed
- **Monitor costs**: Set up billing alerts to avoid surprises
- **Test thoroughly**: Always test in staging before production
- **Document changes**: Keep track of configuration changes
- **Backup regularly**: Regular backups of your configuration and data
- **Security first**: Use Secret Manager for all sensitive data

---

**🎉 Congratulations! Your Animathic backend is now running on Google Cloud Platform!**

For additional support, check the [Google Cloud documentation](https://cloud.google.com/docs) or [Cloud Run documentation](https://cloud.google.com/run/docs).
