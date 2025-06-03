# UV-Based Deployment Guide

This guide covers the modern, streamlined deployment of workflow-use using `uv` (the fast Python package manager) with a stable virtual environment in the project root.

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+** - [Download from python.org](https://python.org)
- **uv** - Will be auto-installed if missing
- **Git** - For cloning browser-use web-ui (optional)
- **Node.js** - For workflow UI development (optional)

### One-Command Deployment

```batch
# Windows
deploy.bat

# Then select your preferred mode:
# 1. Backend only (API server)
# 2. Web-UI only (Browser automation)  
# 3. Complete suite (All components)
```

### Manual Commands

```batch
# Setup environment
uv sync

# Run specific components
uv run python main.py backend    # Backend API only
uv run python main.py webui      # Browser-use web-ui only
uv run python main.py suite      # Complete integrated suite
```

## 📁 Project Structure

```
workflow-use/
├── .venv/                    # Stable virtual environment (project root)
├── workflows/               # Workflow backend
│   ├── backend/            # FastAPI backend
│   ├── workflow_use/       # Core workflow logic
│   ├── .env               # Backend configuration
│   └── pyproject.toml     # Original workflow dependencies
├── ui/                     # Workflow UI (React/Vite)
├── browser-use-web-ui/     # Official browser-use web-ui (auto-cloned)
├── pyproject.toml          # Unified project dependencies
├── main.py                 # Central entry point
├── deploy.bat              # Single deployment script
└── README.md
```

## 🔧 Configuration

### Environment Setup

The deployment script automatically creates environment files:

**workflows/.env** (Backend configuration):
```env
# Required: At least one LLM provider API key
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# Optional: Workflow settings
WORKFLOW_DEBUG=false
WORKFLOW_LOG_LEVEL=info
```

**browser-use-web-ui/.env** (Web-UI configuration):
```env
# LLM Provider API Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# Browser settings
BROWSER_HEADLESS=false
BROWSER_DISABLE_SECURITY=true

# Optional: Custom browser path
BROWSER_PATH="C:\Program Files\Google\Chrome\Application\chrome.exe"
BROWSER_USER_DATA="C:\Users\YourUsername\AppData\Local\Google\Chrome\User Data"
```

## 🎯 Deployment Modes

### 1. Backend Only
**Purpose**: API server for workflow management
**Port**: 8000
**Use case**: Headless automation, API integration

```batch
uv run python main.py backend
```

**Endpoints**:
- API: `http://127.0.0.1:8000`
- Documentation: `http://127.0.0.1:8000/docs`
- OpenAPI spec: `http://127.0.0.1:8000/openapi.json`

### 2. Web-UI Only  
**Purpose**: Browser automation interface
**Port**: 7788
**Use case**: Interactive browser automation

```batch
uv run python main.py webui
```

**Interface**:
- Web-UI: `http://127.0.0.1:7788`
- Features: Multi-LLM support, browser automation, session recording

### 3. Complete Suite
**Purpose**: Full integrated system
**Ports**: 8000 (backend), 7788 (web-ui), 5173 (workflow UI)
**Use case**: Development, full feature access

```batch
uv run python main.py suite
```

**Services**:
- Backend API: `http://127.0.0.1:8000`
- Browser Web-UI: `http://127.0.0.1:7788`
- Workflow UI: `http://127.0.0.1:5173`

## 🛠️ Development Workflow

### Initial Setup
```batch
# Clone repository
git clone https://github.com/browser-use/workflow-use.git
cd workflow-use

# Run deployment script
deploy.bat
```

### Daily Development
```batch
# Activate environment and sync dependencies
uv sync

# Start development suite
uv run python main.py suite

# Or start individual components
uv run python main.py backend
uv run python main.py webui
```

### Adding Dependencies
```batch
# Add runtime dependency
uv add package-name

# Add development dependency  
uv add --dev package-name

# Update all dependencies
uv sync --upgrade
```

### Environment Management
```batch
# Create fresh environment
uv venv --force

# Install dependencies
uv sync

# Run with specific Python version
uv venv --python 3.11
```

## 🔍 Troubleshooting

### Common Issues

**1. "uv not found" error**
```batch
# Install uv manually
python -m pip install uv

# Or use official installer
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**2. "Python 3.11+ required" error**
- Download and install Python 3.11+ from [python.org](https://python.org)
- Ensure Python is in your PATH
- Restart command prompt after installation

**3. "API key not found" error**
- Edit `workflows/.env` to add at least one API key
- Restart the application after adding keys
- Verify the key format matches the provider's requirements

**4. "Port already in use" error**
```batch
# Check what's using the port
netstat -ano | findstr :8000

# Kill the process (replace PID)
taskkill /PID <process_id> /F
```

**5. "Browser automation fails" error**
```batch
# Reinstall Playwright browsers
uv run playwright install --with-deps

# Try with visible browser
# Edit .env: BROWSER_HEADLESS=false
```

**6. "Virtual environment issues"**
```batch
# Remove and recreate environment
rmdir /s .venv
uv venv
uv sync
```

### Performance Optimization

**1. Faster dependency installation**
```batch
# Use uv's parallel installation
uv sync --no-dev  # Skip dev dependencies in production

# Use cached wheels
uv sync --offline  # Use only cached packages
```

**2. Reduce startup time**
```batch
# Start only needed components
uv run python main.py backend  # API only
uv run python main.py webui    # UI only
```

**3. Memory optimization**
```batch
# Set environment variables for lower memory usage
set PYTHONOPTIMIZE=1
set PYTHONDONTWRITEBYTECODE=1
uv run python main.py suite
```

## 📊 Monitoring and Logs

### Application Logs
- Backend logs: Console output with structured logging
- Web-UI logs: Browser console and terminal output
- Workflow UI logs: Browser developer tools

### Health Checks
```batch
# Check backend health
curl http://127.0.0.1:8000/health

# Check web-ui availability
curl http://127.0.0.1:7788

# Process monitoring
tasklist | findstr python
```

### Performance Metrics
- Backend API response times via `/docs` interface
- Browser automation performance in web-ui
- Memory usage via Task Manager

## 🔄 Updates and Maintenance

### Updating Dependencies
```batch
# Update all dependencies
uv sync --upgrade

# Update specific package
uv add package-name@latest

# Check for outdated packages
uv pip list --outdated
```

### Updating Browser-Use Web-UI
```batch
# Navigate to web-ui directory
cd browser-use-web-ui

# Pull latest changes
git pull origin main

# Update dependencies
uv sync
```

### Backup and Restore
```batch
# Backup configuration
copy workflows\.env workflows\.env.backup
copy browser-use-web-ui\.env browser-use-web-ui\.env.backup

# Export dependency list
uv pip freeze > requirements-backup.txt

# Restore from backup
copy workflows\.env.backup workflows\.env
uv pip install -r requirements-backup.txt
```

## 🚀 Production Deployment

### Environment Preparation
```batch
# Set production environment
set ENVIRONMENT=production
set DEBUG=false

# Use production-optimized settings
uv sync --no-dev
```

### Service Configuration
```batch
# Run as Windows service (requires additional setup)
# Or use process managers like PM2 for Node.js-style management

# Background execution
start /B uv run python main.py backend
```

### Security Considerations
- Use environment variables for sensitive data
- Enable HTTPS in production
- Configure firewall rules for required ports
- Regular security updates for dependencies

## 📚 Additional Resources

- **UV Documentation**: https://docs.astral.sh/uv/
- **Browser-Use Web-UI**: https://github.com/browser-use/web-ui
- **Workflow-Use Core**: https://github.com/browser-use/workflow-use
- **Python Virtual Environments**: https://docs.python.org/3/tutorial/venv.html
- **FastAPI Documentation**: https://fastapi.tiangolo.com/

## 🤝 Contributing

### Development Setup
```batch
# Install development dependencies
uv sync --dev

# Run tests
uv run pytest

# Code formatting
uv run ruff format
uv run ruff check --fix
```

### Creating Pull Requests
1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make changes and test with `uv run python main.py suite`
4. Commit changes: `git commit -m "Description"`
5. Push branch: `git push origin feature-name`
6. Create pull request

This modern deployment approach provides a streamlined, reliable way to run the complete workflow-use suite with minimal setup complexity.

