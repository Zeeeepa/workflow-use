# Workflow-Use Suite - Deployment Guide

This guide provides multiple deployment options for the Workflow-Use Suite, from simple to advanced configurations.

## 🚀 Quick Start Options

### Option 1: Ultra-Simple Deployment (Recommended for Testing)

**Best for**: First-time users, testing, development

```batch
# Run the ultra-simple deployment
deploy-simple.bat
```

**What it does:**
- ✅ Installs dependencies directly without package building
- ✅ Avoids complex build system issues
- ✅ Creates simple launchers
- ✅ Works immediately without configuration

**Pros:**
- No build system complexity
- Fast installation
- Guaranteed to work
- Perfect for testing

**Cons:**
- Doesn't install the full workflow_use package
- Limited to basic functionality

### Option 2: Standard Deployment (Recommended for Production)

**Best for**: Production use, full feature access

```batch
# Run the standard deployment
deploy.bat
```

**What it does:**
- ✅ Creates proper package configuration
- ✅ Installs full workflow_use package
- ✅ Backs up and restores original configuration
- ✅ Provides complete functionality

**Pros:**
- Full feature access
- Proper package installation
- Production-ready
- Complete workflow_use functionality

**Cons:**
- Slightly more complex
- Requires proper package structure

### Option 3: Advanced Deployment (For Enterprise)

**Best for**: Enterprise deployments, Docker, advanced configurations

```batch
# Run the advanced deployment
deploy-advanced.bat
```

**What it does:**
- ✅ Multiple deployment modes
- ✅ Docker support
- ✅ Production configurations
- ✅ Advanced monitoring

## 🔧 Troubleshooting Common Issues

### Issue 1: Package Build Errors

**Error Message:**
```
ValueError: Unable to determine which files to ship inside the wheel
```

**Solution:**
Use the ultra-simple deployment instead:
```batch
deploy-simple.bat
```

**Why this works:**
- Bypasses package building entirely
- Installs dependencies directly
- Avoids hatchling configuration issues

### Issue 2: Dependency Conflicts

**Error Message:**
```
Failed to build workflow-use-suite
```

**Solution 1 - Use Simple Deployment:**
```batch
deploy-simple.bat
```

**Solution 2 - Manual Dependency Installation:**
```batch
# Create virtual environment
uv venv

# Install dependencies one by one
uv pip install fastapi uvicorn pydantic
uv pip install playwright gradio requests
uv pip install python-dotenv rich psutil click

# Install browsers
uv run playwright install chromium
```

### Issue 3: Python Version Issues

**Error Message:**
```
Python not found or version < 3.11
```

**Solution:**
1. Install Python 3.11+ from [python.org](https://python.org)
2. Verify installation: `python --version`
3. Run deployment script again

### Issue 4: UV Installation Issues

**Error Message:**
```
uv not found
```

**Solution:**
```batch
# Install uv manually
python -m pip install uv

# Or use PowerShell installer
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## 📋 Deployment Comparison

| Feature | deploy-simple.bat | deploy.bat | deploy-advanced.bat |
|---------|-------------------|------------|---------------------|
| **Complexity** | Low | Medium | High |
| **Setup Time** | < 2 minutes | < 5 minutes | < 10 minutes |
| **Package Building** | ❌ No | ✅ Yes | ✅ Yes |
| **Full Features** | ⚠️ Basic | ✅ Complete | ✅ Complete |
| **Docker Support** | ❌ No | ❌ No | ✅ Yes |
| **Production Ready** | ⚠️ Testing | ✅ Yes | ✅ Enterprise |
| **Error Prone** | ❌ Low | ⚠️ Medium | ⚠️ High |

## 🎯 Recommended Deployment Flow

### For First-Time Users:
1. **Start with**: `deploy-simple.bat`
2. **Test functionality**: Run `START.bat`
3. **If satisfied**: Upgrade to `deploy.bat` for full features

### For Production Users:
1. **Use**: `deploy.bat`
2. **Validate**: Run `test-all.bat` for comprehensive testing
3. **Deploy**: Use generated launchers

### For Enterprise Users:
1. **Use**: `deploy-advanced.bat`
2. **Configure**: Docker and production settings
3. **Monitor**: Use advanced monitoring features

## 🔄 Migration Between Deployment Types

### From Simple to Standard:
```batch
# Clean up simple deployment
rmdir /s .venv
del START.bat start-*.bat main_simple.py

# Run standard deployment
deploy.bat
```

### From Standard to Advanced:
```batch
# Standard deployment is compatible
# Just run advanced deployment
deploy-advanced.bat
```

## 🛠️ Manual Installation (If All Else Fails)

If automated deployment fails, you can install manually:

```batch
# 1. Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# 2. Install core dependencies
pip install fastapi uvicorn pydantic
pip install playwright gradio requests
pip install python-dotenv rich psutil click

# 3. Install browsers
playwright install chromium

# 4. Create simple launcher
echo python -m uvicorn backend.api:app --host 127.0.0.1 --port 8000 > start-backend.bat

# 5. Clone web-ui
git clone https://github.com/browser-use/web-ui.git browser-use-web-ui
```

## 📊 Validation and Testing

After any deployment, validate your installation:

```batch
# Run comprehensive validation
test-all.bat

# Or manual validation
uv run python validate.py

# Test individual components
START.bat
start-backend.bat
start-webui.bat
```

## 🔍 Debugging Deployment Issues

### Enable Verbose Output:
```batch
# Add to any deployment script
set VERBOSE=1
deploy.bat
```

### Check Installation:
```batch
# Verify Python packages
uv pip list

# Check virtual environment
dir .venv

# Verify browsers
uv run playwright --version
```

### Common File Locations:
- **Virtual Environment**: `.venv/`
- **Configuration**: `.env`
- **Launchers**: `START.bat`, `start-*.bat`
- **Logs**: `logs/` (created after first run)
- **Data**: `data/` (created after first run)

## 🎉 Success Indicators

Your deployment is successful when:

- ✅ Virtual environment created (`.venv/` exists)
- ✅ Dependencies installed (no error messages)
- ✅ Launchers created (`START.bat` exists)
- ✅ Configuration ready (`.env` exists)
- ✅ Validation passes (`test-all.bat` succeeds)

## 📞 Getting Help

If you encounter issues:

1. **Check this guide** for common solutions
2. **Run validation**: `test-all.bat` for detailed diagnostics
3. **Try simple deployment**: `deploy-simple.bat` as fallback
4. **Check logs**: Look in `logs/` directory after running
5. **Manual installation**: Follow manual steps above

## 🔄 Updates and Maintenance

### Updating Dependencies:
```batch
# Update all packages
uv pip install --upgrade fastapi uvicorn pydantic
uv pip install --upgrade playwright gradio requests

# Update browsers
uv run playwright install chromium
```

### Cleaning Installation:
```batch
# Remove virtual environment
rmdir /s .venv

# Remove generated files
del START.bat start-*.bat main_simple.py

# Re-run deployment
deploy.bat
```

This comprehensive guide ensures you can successfully deploy the Workflow-Use Suite regardless of your environment or experience level!

