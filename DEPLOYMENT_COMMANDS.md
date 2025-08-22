# 🚀 Quick Deployment Commands

## One-Line Commands

### Build & Deploy (Complete Process)

```bash
# Build
gcloud builds submit --config=cloudbuild.yaml --substitutions=_IMAGE=gcr.io/animathic-backend/animathic-backend:latest .

# Deploy
gcloud run deploy animathic-backend --image gcr.io/animathic-backend/animathic-backend:latest --platform managed --region us-central1 --allow-unauthenticated --memory 512Mi --cpu 1 --concurrency 100 --max-instances 3 --min-instances 0 --execution-environment gen2 --cpu-throttling
```

## Quick Deploy Script

```bash
./scripts/deploy.sh
```

## Individual Commands

### Build Only

```bash
gcloud builds submit --config=cloudbuild.yaml --substitutions=_IMAGE=gcr.io/animathic-backend/animathic-backend:latest .
```

### Deploy Only (if image already built)

```bash
gcloud run deploy animathic-backend \
  --image gcr.io/animathic-backend/animathic-backend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --concurrency 100 \
  --max-instances 3 \
  --min-instances 0 \
  --execution-environment gen2 \
  --cpu-throttling
```

## Cost Optimization Flags

- `--memory 512Mi` - Reduced memory for cost savings
- `--cpu 1` - Single CPU core for cost efficiency
- `--concurrency 100` - High concurrency for better resource utilization
- `--max-instances 3` - Prevents cost spikes
- `--min-instances 0` - Scales to zero when not in use
- `--execution-environment gen2` - Latest generation with better performance
- `--cpu-throttling` - Additional cost control

## Service Information

- **Service Name**: animathic-backend
- **Region**: us-central1
- **Image**: gcr.io/animathic-backend/animathic-backend:latest
- **URL**: https://animathic-backend-4734151242.us-central1.run.app

## Useful Commands

```bash
# Check service status
gcloud run services describe animathic-backend --region=us-central1

# View logs
gcloud logs tail --service=animathic-backend --region=us-central1

# List revisions
gcloud run revisions list --service=animathic-backend --region=us-central1
```
