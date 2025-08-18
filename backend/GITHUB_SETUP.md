# 🔗 GitHub + Google Cloud Integration Setup

## 🎯 **What This Achieves**

- **Automatic deployment** when you push to `main` branch
- **No manual deployment** needed
- **Version tracking** for all deployments
- **Easy rollbacks** to previous versions
- **Team collaboration** with safe deployments

## 🔧 **Setup Steps**

### **Step 1: Add GitHub Secrets**

In your GitHub repository:
1. Go to **Settings > Secrets and variables > Actions**
2. Click **New repository secret**
3. Add these secrets:

#### **Required Secrets:**

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `GCP_PROJECT_ID` | `animathic-backend` | Your Google Cloud project ID |
| `GCP_SA_KEY` | `[Content of github-actions-key.json]` | Service account key file content |

### **Step 2: Get Service Account Key**

The service account key was created at: `~/github-actions-key.json`

**To copy the content:**
```bash
cat ~/github-actions-key.json
```

**Copy the entire JSON content** and paste it as the `GCP_SA_KEY` secret value.

### **Step 3: Verify Setup**

1. **Push to main branch** to trigger deployment
2. **Check Actions tab** in GitHub to see deployment progress
3. **Monitor deployment** in Google Cloud Console

## 🚀 **How It Works**

### **Trigger: Push to Main Branch**
```
git push origin main → GitHub Actions → Google Cloud → Deploy to Cloud Run
```

### **Deployment Process**
1. **Build** Docker image for AMD64 platform
2. **Push** to Google Container Registry
3. **Deploy** to Cloud Run with production settings
4. **Test** service health
5. **Report** deployment status

### **Branch Strategy**
- **`main` branch**: Automatic deployment to production
- **`development/*` branches**: No automatic deployment (safe for development)
- **Pull requests**: Trigger deployment tests but don't deploy

## 🔒 **Security Features**

### **Service Account Permissions**
- ✅ **Cloud Run Admin**: Deploy and manage services
- ✅ **Storage Admin**: Push Docker images
- ✅ **Secret Manager Access**: Read configuration secrets

### **No Hardcoded Credentials**
- ❌ No API keys in code
- ❌ No service account keys in repository
- ✅ All secrets stored securely in GitHub

## 📊 **Monitoring & Debugging**

### **GitHub Actions Logs**
- View deployment progress in **Actions** tab
- Check for build/deployment errors
- Monitor deployment time and success rate

### **Google Cloud Logs**
```bash
# View deployment logs
gcloud run services logs read animathic-backend --region=us-central1

# Stream real-time logs
gcloud run services logs tail animathic-backend --region=us-central1
```

### **Deployment Status**
```bash
# Check service status
gcloud run services describe animathic-backend --region=us-central1

# List revisions
gcloud run revisions list --service=animathic-backend --region=us-central1
```

## 🚨 **Troubleshooting**

### **Common Issues**

#### **1. Service Account Key Invalid**
- Verify the JSON content is copied completely
- Check if the service account still exists
- Regenerate the key if needed

#### **2. Permission Denied**
- Verify service account has required roles
- Check project ID matches
- Ensure secrets are set correctly

#### **3. Build Failures**
- Check Dockerfile syntax
- Verify all dependencies are available
- Check for platform-specific issues

### **Debug Commands**
```bash
# Verify service account exists
gcloud iam service-accounts list --filter="email:github-actions"

# Check permissions
gcloud projects get-iam-policy animathic-backend \
  --flatten="bindings[].members" \
  --filter="bindings.members:github-actions@animathic-backend.iam.gserviceaccount.com" \
  --format="table(bindings.role)"
```

## 🔄 **Workflow Customization**

### **Environment-Specific Deployments**
You can modify the workflow to deploy to different environments:

```yaml
# Deploy to staging on development branch
if: github.ref == 'refs/heads/development'
  # Use staging configuration

# Deploy to production on main branch  
if: github.ref == 'refs/heads/main'
  # Use production configuration
```

### **Approval Workflows**
Add manual approval for production deployments:

```yaml
# Add environment protection
environment: production
```

### **Testing Before Deployment**
Add testing steps before deployment:

```yaml
- name: Run Tests
  run: |
    python -m pytest tests/
    python -m flake8 .
```

## 📈 **Benefits After Setup**

### **Immediate Benefits**
- ✅ **Faster deployments** (no manual steps)
- ✅ **Consistent deployments** (same process every time)
- ✅ **Version tracking** (every deployment linked to commit)
- ✅ **Easy rollbacks** (deploy previous version instantly)

### **Long-term Benefits**
- 🚀 **Faster iteration** (push and deploy)
- 🔒 **Safer deployments** (automated testing)
- 👥 **Team collaboration** (anyone can deploy safely)
- 📊 **Deployment analytics** (track success rates, timing)

## 🎉 **Next Steps**

1. **Add GitHub secrets** (GCP_PROJECT_ID, GCP_SA_KEY)
2. **Push to main branch** to test automatic deployment
3. **Monitor deployment** in GitHub Actions and Google Cloud
4. **Customize workflow** as needed for your team

---

**🎊 Once set up, every push to main will automatically deploy to Google Cloud! 🎊**
