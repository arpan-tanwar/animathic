# 🚀 Animathic Development Branch

This is the development branch for testing and experimenting with different configurations, LLMs, and server settings.

## 🌿 Branch Information

- **Branch Name**: `development/llm-testing`
- **Purpose**: Testing different LLM models, server configurations, and experimental features
- **Base**: Created from `main` branch after fixing all backend errors

## 🛠️ Development Tools

### 1. Configuration Management (`config_dev.py`)

Easily switch between different configurations:

```python
from config_dev import get_llm_config, get_server_config

# Get LLM configuration
llm_config = get_llm_config("gemini-1.5-pro")

# Get server configuration
server_config = get_server_config("testing")
```

### 2. Development Server (`dev_server.py`)

Start the server with different configurations:

```bash
# List all available configurations
python dev_server.py --list-configs

# Start with specific configuration
python dev_server.py --config testing --llm gemini-1.5-pro

# Override specific settings
python dev_server.py --config development --port 8001 --reload

# Set feature flags
python dev_server.py --feature experimental_prompts true
```

## 🤖 Available LLM Models

| Model | Description | Use Case |
|-------|-------------|----------|
| `gemini-2.5-flash` | Fast, efficient model | Simple animations, quick responses |
| `gemini-2.0-flash` | Reliable fallback model | Backup when primary fails |
| `gemini-1.5-pro` | High-capacity model | Complex animations, detailed prompts |
| `gemini-1.5-flash` | Balanced model | General use, good performance |

## 🌐 Server Configurations

| Config | Host | Port | Reload | Workers | Description |
|--------|------|------|--------|---------|-------------|
| `development` | 127.0.0.1 | 8000 | ✅ | 1 | Local development |
| `testing` | 0.0.0.0 | 8001 | ❌ | 2 | Testing environment |
| `production` | 0.0.0.0 | 8000 | ❌ | 4 | Production-like |
| `docker` | 0.0.0.0 | 8000 | ❌ | 1 | Container environment |

## ⚙️ Feature Flags

Control experimental features:

```python
from config_dev import update_feature_flag

# Enable experimental prompts
update_feature_flag("experimental_prompts", True)

# Disable syntax error fixing
update_feature_flag("syntax_error_fixing", False)
```

Available flags:
- `enhanced_logging` - Detailed logging
- `syntax_error_fixing` - Automatic syntax error correction
- `content_validation` - Validate AI responses
- `response_extraction_debug` - Debug response extraction
- `manim_error_details` - Detailed Manim error reporting
- `experimental_prompts` - Use experimental prompt strategies
- `custom_llm_integration` - Enable custom LLM integration

## 🧪 Testing Different Configurations

### Test Different LLMs

```bash
# Test Gemini 2.5 Flash
python dev_server.py --llm gemini-2.5-flash

# Test Gemini 1.5 Pro
python dev_server.py --llm gemini-1.5-pro

# Test with specific prompt
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -H "user-id: test_user" \
  -d '{"prompt": "Create a simple blue circle"}'
```

### Test Server Configurations

```bash
# Test development config
python dev_server.py --config development

# Test production-like config
python dev_server.py --config production

# Test with custom port
python dev_server.py --config testing --port 8002
```

### Test Feature Combinations

```bash
# Enable all experimental features
python dev_server.py --feature experimental_prompts true --feature custom_llm_integration true

# Disable syntax fixing for testing
python dev_server.py --feature syntax_error_fixing false
```

## 🔍 Monitoring and Debugging

### Enhanced Logging

When `enhanced_logging` is enabled:
- Detailed response extraction logs
- Manim render error details
- Code validation results
- Performance metrics

### Response Extraction Debug

When `response_extraction_debug` is enabled:
- Logs all extraction attempts
- Shows response structure
- Tracks extraction success/failure

### Manim Error Details

When `manim_error_details` is enabled:
- Full error tracebacks
- Code that caused errors
- Render command details

## 🚨 Troubleshooting

### Common Issues

1. **LLM Model Not Available**
   ```bash
   # Check available models
   python dev_server.py --list-configs
   
   # Use fallback model
   python dev_server.py --llm gemini-2.0-flash
   ```

2. **Port Already in Use**
   ```bash
   # Use different port
   python dev_server.py --port 8001
   
   # Or kill existing process
   lsof -ti:8000 | xargs kill -9
   ```

3. **Feature Flag Issues**
   ```bash
   # Reset to defaults
   python dev_server.py --feature experimental_prompts false
   ```

### Debug Mode

Enable debug logging:

```bash
# Set log level to debug
export LOG_LEVEL=DEBUG

# Start server with debug
python dev_server.py --config development
```

## 📝 Development Workflow

1. **Make Changes**: Edit code in the development branch
2. **Test Configurations**: Use `dev_server.py` to test different setups
3. **Validate Changes**: Ensure all features work with different configs
4. **Commit Changes**: Use descriptive commit messages
5. **Push Updates**: Keep the development branch updated

## 🔄 Branch Management

### Update from Main

```bash
# Switch to main and pull updates
git checkout main
git pull origin main

# Switch back to development and merge
git checkout development/llm-testing
git merge main
```

### Push Development Changes

```bash
# Commit your changes
git add .
git commit -m "Add new LLM configuration for testing"

# Push to remote
git push origin development/llm-testing
```

## 📚 Additional Resources

- **Main README**: See `../README.md` for general project information
- **API Documentation**: Available at `http://localhost:8000/docs` when server is running
- **Configuration Examples**: Check `config_dev.py` for more configuration options

## 🤝 Contributing

When testing configurations:
1. Document any issues found
2. Test with multiple LLM models
3. Verify server configurations work
4. Update this README with findings

---

**Happy Testing! 🎉**
