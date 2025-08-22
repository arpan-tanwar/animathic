# 🚀 Hybrid AI System Deployment Guide

## Overview

This guide walks you through deploying the new Hybrid AI System for Animathic, which provides intelligent model routing between Gemini 2.5 Flash and your local trained model, with comprehensive feedback collection and continuous improvement.

## 🎯 What You Get

### **Option 1: Gemini 2.5 Flash (Primary)**

- High-quality animation generation
- Structured JSON output for reliable compilation
- Automatic fine-tuning using user feedback
- Fast response times

### **Option 2: Local Model (Fallback)**

- Cost-effective ($0 per generation)
- Privacy-focused (no data leaves your infrastructure)
- Continuous learning from user feedback
- Offline capability

### **Option 3: Hybrid Intelligence**

- Best of both worlds
- Automatic model selection based on prompt complexity
- Seamless fallback if primary model fails
- Performance optimization over time

## 📋 Prerequisites

### **Required Environment Variables**

```bash
# Google AI API (for Gemini)
GOOGLE_AI_API_KEY=your_gemini_api_key_here

# Google Cloud Project (for Gemini fine-tuning)
GCP_PROJECT_ID=your_project_id
GCP_REGION=us-central1

# Optional Configuration
GEMINI_CONFIDENCE_THRESHOLD=0.7
LOCAL_FALLBACK_ENABLED=true
QUALITY_ASSESSMENT_ENABLED=true
```

### **Required Dependencies**

```bash
# Core dependencies (already in requirements.txt)
fastapi>=0.110.0
uvicorn[standard]>=0.27.0
google-generativeai>=0.8.0
httpx>=0.26.0
pydantic>=2.5.0

# New dependencies for hybrid system
uuid>=1.30
sqlite3  # Usually included with Python
```

## 🚀 Deployment Steps

### **Step 1: Environment Setup**

1. **Set API Keys**

   ```bash
   export GOOGLE_AI_API_KEY="your_actual_api_key"
   export GCP_PROJECT_ID="your_project_id"
   export GCP_REGION="us-central1"
   ```

2. **Verify Configuration**
   ```bash
   cd backend
   python test_hybrid_system.py
   ```
   All tests should pass (some may be skipped if services unavailable).

### **Step 2: Update Your .env File**

Add these variables to your `backend/.env` file:

```bash
# Hybrid AI System Configuration
GOOGLE_AI_API_KEY=your_gemini_api_key
GCP_PROJECT_ID=your_project_id
GCP_REGION=us-central1

# Optional Settings
GEMINI_CONFIDENCE_THRESHOLD=0.7
LOCAL_FALLBACK_ENABLED=true
QUALITY_ASSESSMENT_ENABLED=true
```

### **Step 3: Restart Your Backend**

The system automatically detects available services and configures itself:

```bash
# If running locally
cd backend
python dev_server.py

# If running in production
# Restart your Cloud Run service
```

### **Step 4: Verify Deployment**

Check the logs for these success messages:

```
✅ Hybrid orchestrator initialized - Gemini: True, Local: True
✅ Enhanced Gemini service initialized with gemini-2.5-flash
✅ Local LLM service initialized
✅ Feedback collector initialized with database: feedback_data.db
```

## 🔧 Configuration Options

### **Model Selection Logic**

The system automatically selects models based on:

1. **Prompt Complexity**:

   - Simple prompts (circle, square, basic shapes) → Local model
   - Complex prompts (3D, transformations, sequences) → Gemini

2. **Performance Metrics**:

   - Success rates
   - Response times
   - User satisfaction scores

3. **Availability**:
   - Falls back to available models if primary fails

### **Customizing Model Selection**

You can adjust the behavior by modifying these parameters:

```python
# In backend/services/hybrid_orchestrator.py
self.gemini_confidence_threshold = 0.7  # When to prefer Gemini
self.local_fallback_enabled = True      # Enable/disable fallback
```

### **Feedback Collection Settings**

The feedback system automatically tracks:

- Generation attempts and results
- User ratings and comments
- Performance metrics
- Error patterns

## 📊 Monitoring and Analytics

### **Real-time Performance**

Check model performance in real-time:

```python
from services.hybrid_orchestrator import HybridOrchestrator

orchestrator = HybridOrchestrator()
summary = await orchestrator.get_performance_summary()

print(f"Gemini Success Rate: {summary['models']['gemini-2.5-flash']['success_rate']:.1f}%")
print(f"Local Success Rate: {summary['models']['local-trained']['success_rate']:.1f}%")
```

### **Feedback Analytics**

Generate comprehensive reports:

```python
from scripts.enhanced_training_pipeline import EnhancedTrainingPipeline

pipeline = EnhancedTrainingPipeline()
report = await pipeline.generate_improvement_report(days=30)

print(f"Overall Success Rate: {report['overall_metrics']['success_rate']:.1f}%")
print(f"User Satisfaction: {report['overall_metrics']['user_satisfaction']:.1f}/5")
```

### **Database Monitoring**

The feedback system uses SQLite by default:

```bash
# Check database size
ls -lh feedback_data.db

# View recent generations
sqlite3 feedback_data.db "SELECT * FROM generation_records ORDER BY timestamp DESC LIMIT 10;"
```

## 🔄 Continuous Improvement

### **Automatic Training Data Collection**

Every generation automatically feeds the improvement pipeline:

1. **User generates animation** → System tracks success/failure
2. **User provides feedback** → Rating and quality assessment
3. **System analyzes patterns** → Identifies improvement areas
4. **Training datasets created** → Ready for model improvement

### **Local Model Training**

Run the training pipeline monthly:

```bash
cd backend
python scripts/enhanced_training_pipeline.py --days 30 --colab --report
```

This will:

- Generate training dataset from user feedback
- Create specialized datasets by animation type
- Prepare Colab training data
- Generate improvement recommendations

### **Gemini Fine-tuning**

Automatically trigger fine-tuning when enough data is collected:

```python
from services.gemini_fine_tuning import GeminiFineTuningService

fine_tuning = GeminiFineTuningService()

# Create fine-tuning job
job_id = await fine_tuning.create_fine_tuning_job(
    training_data_path="training_data/feedback_dataset.jsonl"
)

# Monitor progress
status = await fine_tuning.get_tuning_job_status(job_id)
```

## 🚨 Troubleshooting

### **Common Issues**

1. **"Gemini service unavailable"**

   - Check `GOOGLE_AI_API_KEY` is set correctly
   - Verify API key has proper permissions
   - Check Google AI API quotas

2. **"Local LLM service unavailable"**

   - Ensure your local model is running
   - Check `LOCAL_INFER_URL` environment variable
   - Verify Ollama is running (if using)

3. **"Feedback collector failed"**
   - Check database permissions
   - Ensure `feedback_data.db` is writable
   - Verify SQLite is available

### **Performance Issues**

1. **Slow Generation**

   - Monitor model selection logic
   - Check API response times
   - Review fallback behavior

2. **High Failure Rates**
   - Review error logs
   - Check model availability
   - Analyze prompt complexity distribution

### **Debug Mode**

Enable detailed logging:

```bash
export LOG_LEVEL=DEBUG
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"
```

## 📈 Scaling Considerations

### **Production Deployment**

1. **Database**: Consider migrating from SQLite to PostgreSQL
2. **Storage**: Use cloud storage for training datasets
3. **Monitoring**: Add comprehensive logging and alerting
4. **Backup**: Regular backups of feedback database

### **Performance Optimization**

1. **Caching**: Cache frequently used model responses
2. **Load Balancing**: Distribute requests across multiple instances
3. **Async Processing**: Use background tasks for non-critical operations
4. **Resource Limits**: Set appropriate timeouts and retry limits

## 🔮 Future Enhancements

### **Short Term (1-3 months)**

- Real-time performance dashboards
- Automated quality assessment
- A/B testing for model selection
- Enhanced error recovery

### **Medium Term (3-6 months)**

- Multi-modal input support
- Advanced prompt engineering
- Distributed training pipeline
- Model versioning and rollback

## 📚 Additional Resources

- [Hybrid AI System Documentation](HYBRID_AI_SYSTEM.md)
- [Manim Documentation](https://docs.manim.community/)
- [Google AI Studio](https://aistudio.google.com/)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/)

## 🎉 Success Metrics

Your deployment is successful when you see:

✅ **All tests pass**: `python test_hybrid_system.py` shows 6/6 tests passed
✅ **Services initialize**: Logs show successful service initialization
✅ **Model routing works**: Complex prompts use Gemini, simple prompts use local
✅ **Feedback collection**: Database grows with user interactions
✅ **Performance improves**: Success rates increase over time

## 🆘 Getting Help

If you encounter issues:

1. **Check logs**: Look for error messages and warnings
2. **Run tests**: Verify system components are working
3. **Review configuration**: Ensure environment variables are set
4. **Check dependencies**: Verify all packages are installed
5. **Monitor resources**: Check API quotas and system resources

The system is designed to be self-improving - the more you use it, the better it gets! 🚀✨
