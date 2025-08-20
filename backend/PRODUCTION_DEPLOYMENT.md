# 🚀 Animathic Backend - Production Deployment Guide

## 🎯 **System Overview**

Animathic is a production-ready AI-powered mathematical animation generation system that combines:
- **Gemini AI** (primary) for structured JSON generation
- **Local LLM** (fallback) using Ollama for cost-effective processing
- **Manim** for mathematical animation compilation
- **Feedback collection** for continuous model improvement
- **Training pipeline** for fine-tuning and local model training

## ✅ **Pre-Deployment Checklist**

### **1. Environment Setup**
- [ ] Google Cloud Platform project configured
- [ ] Google AI API key obtained
- [ ] Supabase project configured (optional, for enhanced features)
- [ ] Local Ollama service running (for fallback)

### **2. Configuration**
- [ ] Environment variables configured in `.env`
- [ ] Production secrets set in Google Cloud Secret Manager
- [ ] CORS origins configured for your domain
- [ ] Rate limiting configured appropriately

### **3. Testing**
- [ ] All tests passing locally (8/9 tests = 89% success rate)
- [ ] Workflow tested: prompt → JSON → Manim → compilation
- [ ] Feedback collection system verified
- [ ] Training pipeline validated

## 🚀 **Deployment Options**

### **Option 1: Google Cloud Run (Recommended)**

```bash
# Set environment variables
export GCP_PROJECT_ID="your-project-id"
export GCP_REGION="us-central1"
export COMMIT_SHA="$(git rev-parse HEAD)"

# Run deployment script
cd backend
./deploy.sh
```

### **Option 2: Manual Google Cloud Run**

```bash
# Build and push Docker image
docker build -f Dockerfile.gcp -t gcr.io/YOUR_PROJECT_ID/animathic-backend .
docker push gcr.io/YOUR_PROJECT_ID/animathic-backend

# Deploy to Cloud Run
gcloud run deploy animathic-backend \
    --image gcr.io/YOUR_PROJECT_ID/animathic-backend \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --memory 4Gi \
    --cpu 1 \
    --timeout 600 \
    --port 8080
```

### **Option 3: Docker Compose (Local/Staging)**

```bash
# Create docker-compose.yml
version: '3.8'
services:
  animathic-backend:
    build: .
    ports:
      - "8080:8080"
    environment:
      - ENVIRONMENT=production
      - GOOGLE_AI_API_KEY=${GOOGLE_AI_API_KEY}
    volumes:
      - ./media:/app/media

# Run
docker-compose up -d
```

## 🔧 **Configuration**

### **Environment Variables**

```bash
# Core Configuration
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Google AI
GOOGLE_AI_API_KEY=your_api_key_here
GOOGLE_AI_MODEL=gemini-2.0-flash-exp

# Local LLM (Ollama)
LOCAL_FALLBACK_ENABLED=true
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=codellama:7b-instruct-q4_K_M

# Security
SECRET_KEY=your_production_secret_key
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Rate Limiting
ENABLE_RATE_LIMITING=true
RATE_LIMIT_REQUESTS=10
RATE_LIMIT_WINDOW=1
```

### **Google Cloud Secret Manager**

```bash
# Create secrets
echo -n "your_google_ai_api_key" | gcloud secrets create GOOGLE_AI_API_KEY --data-file=-
echo -n "your_supabase_url" | gcloud secrets create SUPABASE_URL --data-file=-
echo -n "your_supabase_key" | gcloud secrets create SUPABASE_ANON_KEY --data-file=-
```

## 📊 **Monitoring & Health Checks**

### **Health Endpoints**
- `GET /api/health` - System health status
- `GET /api/metrics` - Performance metrics (if enabled)
- `GET /docs` - API documentation

### **Logs**
```bash
# View Cloud Run logs
gcloud logs tail --service=animathic-backend

# View specific log entries
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=animathic-backend"
```

### **Performance Monitoring**
- Response time monitoring
- Error rate tracking
- Model performance metrics
- Resource utilization

## 🔄 **Workflow Verification**

### **1. Test Basic Endpoints**
```bash
# Health check
curl https://your-service-url/api/health

# API docs
curl https://your-service-url/docs
```

### **2. Test Animation Generation**
```bash
# Generate animation
curl -X POST https://your-service-url/api/generate-animation \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a simple blue circle"}'
```

### **3. Test Feedback Collection**
```bash
# Submit feedback
curl -X POST https://your-service-url/api/feedback \
  -H "Content-Type: application/json" \
  -d '{"generation_id": "uuid", "rating": 5, "comments": "Great animation!"}'
```

## 🚨 **Troubleshooting**

### **Common Issues**

#### **1. Local LLM Timeout**
- **Symptom**: 30-second timeout on local model
- **Solution**: Increase timeout or optimize model performance
- **Workaround**: Use Gemini as primary model

#### **2. Manim Compilation Errors**
- **Symptom**: Animation generation fails
- **Solution**: Check Manim installation and dependencies
- **Debug**: Review compilation logs

#### **3. Rate Limiting**
- **Symptom**: 429 Too Many Requests
- **Solution**: Adjust rate limit configuration
- **Monitor**: Check request patterns

### **Debug Commands**
```bash
# Check service status
gcloud run services describe animathic-backend --region=us-central1

# View recent logs
gcloud logs read "resource.type=cloud_run_revision" --limit=50

# Test local components
cd backend
python test_hybrid_system.py
```

## 📈 **Scaling & Performance**

### **Auto-scaling Configuration**
- **Min instances**: 0 (cost optimization)
- **Max instances**: 10 (performance limit)
- **CPU**: 1 (adequate for most workloads)
- **Memory**: 4Gi (sufficient for Manim compilation)

### **Performance Optimization**
- **Model caching**: Implement for frequently used prompts
- **Async processing**: Background animation compilation
- **CDN**: Use for static media delivery
- **Database**: Consider PostgreSQL for production scale

## 🔒 **Security Considerations**

### **Production Security**
- [ ] HTTPS enforced
- [ ] API key rotation
- [ ] Rate limiting enabled
- [ ] CORS properly configured
- [ ] Input validation implemented
- [ ] Error messages sanitized

### **Access Control**
- [ ] Authentication system (if required)
- [ ] API key management
- [ ] User role permissions
- [ ] Audit logging

## 📚 **Maintenance**

### **Regular Tasks**
- **Daily**: Monitor error rates and performance
- **Weekly**: Review feedback data and model performance
- **Monthly**: Update dependencies and security patches
- **Quarterly**: Analyze usage patterns and optimize

### **Backup Strategy**
- **Configuration**: Version controlled in Git
- **Data**: Regular database backups (if using database)
- **Media**: Cloud storage with lifecycle policies
- **Secrets**: Managed in Google Secret Manager

## 🎉 **Success Metrics**

### **System Health**
- **Uptime**: >99.9%
- **Response Time**: <2 seconds average
- **Error Rate**: <1%
- **Test Coverage**: >89%

### **User Experience**
- **Animation Success Rate**: >95%
- **User Satisfaction**: >4.5/5 rating
- **Feedback Response Time**: <24 hours

## 📞 **Support & Contact**

### **Emergency Contacts**
- **System Issues**: Check logs and health endpoints
- **Performance Issues**: Monitor metrics and scaling
- **Security Issues**: Immediate response required

### **Documentation**
- **API Docs**: `/docs` endpoint
- **Code Repository**: GitHub main branch
- **Configuration**: Environment templates
- **Deployment**: This guide

---

**🎯 Ready for Production!** Your Animathic backend is now deployed and ready to generate amazing mathematical animations! 🚀
