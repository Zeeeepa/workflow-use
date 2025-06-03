# Browser-Use Complete Suite PowerShell Launcher

This comprehensive PowerShell script sets up and launches the complete Browser-Use ecosystem with web-UI and workflows in a single command.

## 🚀 Quick Start

### Basic Usage
```powershell
# Launch complete suite (browser-use + web-ui + workflows)
.\launch-browser-use-complete.ps1
```

### Advanced Usage
```powershell
# Docker mode with persistent browser
.\launch-browser-use-complete.ps1 -UseDocker -PersistentBrowser

# Custom ports and specific components
.\launch-browser-use-complete.ps1 -LaunchMode webui -WebUIPort 8080

# Verbose output for debugging
.\launch-browser-use-complete.ps1 -Verbose
```

## 🎯 What You Get

### Complete Browser-Use Ecosystem
- **🤖 Browser-Use Core**: AI-powered browser automation engine
- **🌐 Web-UI**: Beautiful Gradio-based web interface for easy interaction
- **⚙️ Workflow-Use**: Record, replay, and automate complex workflows
- **🔧 Unified Configuration**: Single environment setup for all components

### Multiple Deployment Options
- **🐍 Local Python**: Direct installation with virtual environments
- **🐳 Docker**: Containerized deployment with isolation
- **💾 Persistent Sessions**: Keep browser state across runs
- **🎛️ Flexible Configuration**: Customizable ports and settings

## 📋 Prerequisites

### Required
- **PowerShell 5.1+** (Windows) or **PowerShell Core 6+** (Cross-platform)
- **Python 3.8+** with pip
- **Git** for repository cloning

### Optional
- **Node.js 16+** (for web-ui extensions)
- **Docker** (if using Docker mode)
- **UV Package Manager** (for faster dependency resolution)

## 🛠️ Installation & Setup

### 1. Download the Script
```powershell
# Download directly
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/browser-use/workflow-use/main/launch-browser-use-complete.ps1" -OutFile "launch-browser-use-complete.ps1"

# Or clone the repository
git clone https://github.com/browser-use/workflow-use.git
cd workflow-use
```

### 2. Set Execution Policy (Windows)
```powershell
# Allow script execution (run as Administrator)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3. Run the Launcher
```powershell
# Basic launch
.\launch-browser-use-complete.ps1

# Or with parameters
.\launch-browser-use-complete.ps1 -LaunchMode all -WebUIPort 7788 -WorkflowPort 8000
```

## 🎛️ Configuration Options

### Launch Modes
| Mode | Description | Components |
|------|-------------|------------|
| `all` | Complete suite (default) | Browser-Use + Web-UI + Workflows |
| `webui` | Web interface only | Browser-Use + Web-UI |
| `workflows` | Workflow automation only | Browser-Use + Workflows |
| `browser-only` | Core browser automation | Browser-Use only |

### Parameters

#### Basic Parameters
- **`-WorkingDirectory`**: Directory for repositories (default: current directory)
- **`-LaunchMode`**: Components to launch (`all`, `webui`, `workflows`, `browser-only`)
- **`-WebUIPort`**: Web-UI port (default: 7788)
- **`-WorkflowPort`**: Workflow backend port (default: 8000)

#### Advanced Parameters
- **`-UseDocker`**: Use Docker containers instead of local Python
- **`-PersistentBrowser`**: Keep browser sessions across runs
- **`-SkipDependencies`**: Skip dependency installation (use existing)
- **`-Verbose`**: Enable detailed output for debugging

## 🌐 Service Endpoints

After successful launch, you'll have access to:

### Web-UI Interface
- **URL**: `http://localhost:7788` (or custom port)
- **Features**: 
  - Chat interface for browser automation
  - Visual workflow builder
  - Real-time browser control
  - Session management

### Workflow Backend API
- **URL**: `http://localhost:8000` (or custom port)
- **API Docs**: `http://localhost:8000/docs`
- **Features**:
  - RESTful API for workflow management
  - Workflow execution endpoints
  - Status monitoring
  - Configuration management

## 🔧 Environment Configuration

The script automatically creates a `.env` file with:

```env
# API Keys (add your actual keys)
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GOOGLE_API_KEY=your_google_key_here
AZURE_OPENAI_API_KEY=your_azure_key_here
DEEPSEEK_API_KEY=your_deepseek_key_here

# Service Configuration
WEBUI_PORT=7788
WORKFLOW_PORT=8000
BROWSER_PERSISTENT=false

# Browser Configuration
BROWSER_TYPE=chromium
HEADLESS=false
BROWSER_ARGS=--no-sandbox,--disable-dev-shm-usage
```

## 🐳 Docker Mode

### Enable Docker Mode
```powershell
.\launch-browser-use-complete.ps1 -UseDocker
```

### Docker Features
- **🔒 Isolation**: Complete environment isolation
- **📦 Consistency**: Same environment across different machines
- **🔄 Easy Cleanup**: Remove containers when done
- **💾 Volume Mounting**: Persistent data storage
- **🌐 Network Configuration**: Proper port mapping

### Docker Requirements
```powershell
# Verify Docker is running
docker --version
docker ps

# Pull required images (done automatically)
docker pull python:3.11-slim
```

## 🎯 Usage Examples

### Example 1: Complete Development Setup
```powershell
# Set up complete development environment
.\launch-browser-use-complete.ps1 -WorkingDirectory "C:\dev\browser-use" -Verbose

# Result: Full suite running with detailed output
# - Web-UI at http://localhost:7788
# - Workflow API at http://localhost:8000
# - All repositories cloned to C:\dev\browser-use
```

### Example 2: Production Docker Deployment
```powershell
# Production deployment with Docker
.\launch-browser-use-complete.ps1 -UseDocker -PersistentBrowser -WebUIPort 80 -WorkflowPort 8080

# Result: Dockerized deployment with:
# - Web-UI at http://localhost:80
# - Workflow API at http://localhost:8080
# - Persistent browser sessions
```

### Example 3: Web-UI Only for Demos
```powershell
# Launch only web interface for demonstrations
.\launch-browser-use-complete.ps1 -LaunchMode webui -WebUIPort 3000

# Result: Lightweight setup with just web interface
# - Web-UI at http://localhost:3000
# - No workflow backend (faster startup)
```

### Example 4: Workflow Development
```powershell
# Focus on workflow development
.\launch-browser-use-complete.ps1 -LaunchMode workflows -WorkflowPort 5000

# Result: Backend-focused setup
# - Workflow API at http://localhost:5000
# - API docs at http://localhost:5000/docs
# - No web-ui (use API directly)
```

## 🔍 Troubleshooting

### Common Issues

#### 1. PowerShell Execution Policy
**Error**: `execution of scripts is disabled on this system`
**Solution**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 2. Python Not Found
**Error**: `Python not found or not in PATH`
**Solution**:
- Install Python from [python.org](https://python.org)
- Ensure Python is in your PATH
- Restart PowerShell after installation

#### 3. Git Not Found
**Error**: `Git not found or not in PATH`
**Solution**:
- Install Git from [git-scm.com](https://git-scm.com)
- Ensure Git is in your PATH
- Restart PowerShell after installation

#### 4. Port Already in Use
**Error**: `Port 7788 is already in use`
**Solution**:
```powershell
# Use different ports
.\launch-browser-use-complete.ps1 -WebUIPort 8080 -WorkflowPort 9000

# Or find and stop conflicting process
netstat -ano | findstr :7788
taskkill /PID <process_id> /F
```

#### 5. Docker Issues
**Error**: `Docker not found but UseDocker specified`
**Solution**:
- Install Docker Desktop
- Start Docker service
- Verify with `docker --version`

### Debug Mode
```powershell
# Enable verbose output for debugging
.\launch-browser-use-complete.ps1 -Verbose

# This provides detailed information about:
# - Prerequisite checks
# - Repository cloning
# - Dependency installation
# - Service startup
# - Error details
```

### Health Checks
The script automatically performs health checks:
- **Service Availability**: Tests if services respond to HTTP requests
- **Port Accessibility**: Verifies ports are accessible
- **Process Status**: Monitors process health
- **Dependency Verification**: Checks all required dependencies

## 🔄 Updates and Maintenance

### Updating Components
```powershell
# Update all repositories
cd browser-use && git pull origin main
cd ../browser-use-web-ui && git pull origin main
cd ../workflow-use && git pull origin main

# Update dependencies
.\launch-browser-use-complete.ps1 -SkipDependencies:$false
```

### Cleaning Up
```powershell
# The script automatically cleans up on exit, but you can also:

# Stop all processes
Get-Process | Where-Object {$_.ProcessName -like "*python*" -or $_.ProcessName -like "*node*"} | Stop-Process

# Remove Docker containers (if using Docker mode)
docker stop browser-use-webui workflow-use-backend
docker rm browser-use-webui workflow-use-backend

# Clean up temporary files
Remove-Item .env -Force -ErrorAction SilentlyContinue
```

## 🎉 Success Indicators

Your setup is successful when you see:

```
✅ Python found: Python 3.11.5
✅ Git found: git version 2.41.0
✅ Browser-Use Core cloned successfully
✅ Browser-Use Web-UI cloned successfully
✅ Workflow-Use cloned successfully
✅ Web-UI started successfully
   🌐 Web Interface: http://localhost:7788
✅ Workflow backend started successfully
   📡 API Endpoint: http://localhost:8000
   📚 API Docs: http://localhost:8000/docs

🎉 Browser-Use Suite is running!
Press Ctrl+C to stop all services...
```

## 📚 Additional Resources

- **Browser-Use Documentation**: [browser-use.com](https://browser-use.com)
- **Web-UI Repository**: [github.com/browser-use/web-ui](https://github.com/browser-use/web-ui)
- **Workflow-Use Repository**: [github.com/browser-use/workflow-use](https://github.com/browser-use/workflow-use)
- **PowerShell Documentation**: [docs.microsoft.com/powershell](https://docs.microsoft.com/powershell)

## 🤝 Contributing

To contribute to this launcher:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This launcher script is provided under the same license as the Browser-Use project.

---

**Happy Automating! 🚀**

