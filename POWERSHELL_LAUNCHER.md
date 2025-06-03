# PowerShell Launcher for Workflow Use Suite

A comprehensive PowerShell script that automates the setup and launch of the complete Workflow Use ecosystem, including optional integration with browser-use and web-ui components.

## Overview

The `launch-workflow-suite.ps1` script provides a one-click solution for Windows users to:
- Set up the complete workflow automation environment
- Integrate with browser-use for AI-powered browser control
- Launch visual workflow editors and managers
- Support both local and Docker deployments

## Quick Start

### Download and Run
```powershell
# Download the launcher script
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/browser-use/workflow-use/main/launch-workflow-suite.ps1" -OutFile "launch-workflow-suite.ps1"

# Basic workflow-use setup
.\launch-workflow-suite.ps1

# Full suite with all components
.\launch-workflow-suite.ps1 -LaunchWebUI -LaunchWorkflowGUI
```

### Prerequisites
- **Windows 10/11** with PowerShell 5.1+
- **Python 3.11+** (if not using Docker for all components)
- **Git** for repository cloning
- **Node.js and npm** for building extensions and UI
- **Docker Desktop** (optional, for Docker deployment)

## Usage Examples

### Basic Workflow Setup
```powershell
# Minimal setup - just workflow-use
.\launch-workflow-suite.ps1
```

### Full Development Environment
```powershell
# Complete setup with visual interfaces
.\launch-workflow-suite.ps1 -LaunchWebUI -LaunchWorkflowGUI
```

### Docker Deployment
```powershell
# Use Docker for browser-use components
.\launch-workflow-suite.ps1 -UseDocker -LaunchWebUI -PersistentBrowser
```

### Custom Configuration
```powershell
# Custom directory and ports
.\launch-workflow-suite.ps1 `
  -WorkingDirectory "D:\my-workflows" `
  -WorkflowUIPort 3000 `
  -WebUIPort 8080 `
  -LaunchWorkflowGUI
```

## Parameters Reference

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `WorkingDirectory` | String | `C:\workflow-use-suite` | Installation directory |
| `PythonVersion` | String | `3.11` | Python version for virtual environments |
| `WorkflowUIPort` | Int | `5173` | Port for workflow visual interface |
| `WorkflowAPIPort` | Int | `8000` | Port for workflow API backend |
| `WebUIPort` | Int | `7788` | Port for browser-use web interface |
| `WebUIIP` | String | `127.0.0.1` | IP address for web interfaces |
| `SkipInstall` | Switch | `false` | Skip installation, just launch services |
| `UseDocker` | Switch | `false` | Use Docker for browser-use components |
| `PersistentBrowser` | Switch | `false` | Keep browser open between tasks |
| `LaunchWebUI` | Switch | `false` | Launch browser-use web interface |
| `LaunchWorkflowGUI` | Switch | `false` | Launch workflow visual editor |
| `Help` | Switch | `false` | Show help message |

## What the Script Does

### 1. Prerequisites Check
- Verifies Python, Git, Node.js, npm installation
- Checks for Docker if using Docker mode
- Warns about missing UV package manager (optional)

### 2. Repository Management
- Clones workflow-use repository
- Optionally clones browser-use and web-ui (if `-LaunchWebUI`)
- Updates existing repositories with latest changes

### 3. Environment Setup
- Creates Python virtual environments using UV or pip
- Installs all Python dependencies
- Builds workflow browser extension with npm
- Sets up workflow UI dependencies
- Installs Playwright browsers

### 4. Configuration
- Creates `.env` files from examples
- Configures API endpoints and ports
- Sets up Docker environment if requested

### 5. Service Launch
- Starts workflow API backend (FastAPI)
- Launches workflow visual interface (if requested)
- Starts browser-use web UI (if requested)
- Opens browsers automatically

## Services and Interfaces

### Workflow Components
- **Workflow CLI**: Command-line interface for workflow operations
- **Workflow API**: FastAPI backend for workflow management
- **Workflow GUI**: Visual interface for workflow creation and execution

### Browser-Use Integration (Optional)
- **Web UI**: Gradio-based interface for AI browser automation
- **VNC Viewer**: Remote browser viewing (Docker mode only)

### Access URLs
- **Workflow GUI**: `http://127.0.0.1:5173` (default)
- **Workflow API**: `http://127.0.0.1:8000` (default)
- **Browser-Use Web UI**: `http://127.0.0.1:7788` (default)
- **VNC Viewer**: `http://127.0.0.1:6080/vnc.html` (Docker mode)

## Workflow Commands

After setup, navigate to the workflows directory and use these commands:

```powershell
cd C:\workflow-use-suite\workflow-use\workflows

# Create a new workflow
python cli.py create-workflow

# Run workflow as AI tool
python cli.py run-as-tool examples/example.workflow.json --prompt "fill the form with example data"

# Run workflow with predefined variables
python cli.py run-workflow examples/example.workflow.json

# Launch GUI (alternative to script parameter)
python cli.py launch-gui

# See all available commands
python cli.py --help
```

## Python Integration

Use workflows programmatically:

```python
from workflow_use import Workflow
import asyncio

# Load and run a workflow
workflow = Workflow.load_from_file("example.workflow.json")
result = asyncio.run(workflow.run_as_tool("I want to search for 'workflow use'"))
print(result)
```

## Environment Configuration

### API Keys Required
Edit the generated `.env` files to add your API keys:

**workflows/.env**:
```env
OPENAI_API_KEY=your_openai_key_here
```

**web-ui/.env** (if using browser-use):
```env
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GOOGLE_API_KEY=your_google_key_here
# ... other LLM provider keys
```

### Docker Configuration
When using Docker mode, additional environment variables:
```env
CHROME_PERSISTENT_SESSION=true  # Keep browser open
VNC_PASSWORD=youvncpassword     # VNC access password
```

## Troubleshooting

### Common Issues

**1. PowerShell Execution Policy**
```powershell
# If script execution is blocked
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**2. Missing Prerequisites**
- Install Python 3.11+ from python.org
- Install Git from git-scm.com
- Install Node.js from nodejs.org
- Install Docker Desktop from docker.com

**3. Port Conflicts**
```powershell
# Use different ports if defaults are occupied
.\launch-workflow-suite.ps1 -WorkflowUIPort 3000 -WebUIPort 8080
```

**4. Permission Errors**
- Run PowerShell as Administrator
- Check antivirus software blocking file creation

**5. Virtual Environment Issues**
```powershell
# Install UV package manager for better environment management
pip install uv
```

### Stopping Services

**Background Jobs (Local Mode)**:
```powershell
# List running jobs
Get-Job

# Stop specific job
Stop-Job -Id <JobId>
Remove-Job -Id <JobId>

# Stop all jobs
Get-Job | Stop-Job
Get-Job | Remove-Job
```

**Docker Services**:
```powershell
cd C:\workflow-use-suite\web-ui
docker-compose down
```

## Advanced Usage

### Custom Workflow Directory
```powershell
# Use existing workflow directory
.\launch-workflow-suite.ps1 -WorkingDirectory "C:\existing-workflows" -SkipInstall
```

### Development Mode
```powershell
# Launch with hot-reload for development
.\launch-workflow-suite.ps1 -LaunchWorkflowGUI -LaunchWebUI
```

### Production Deployment
```powershell
# Docker mode for production-like environment
.\launch-workflow-suite.ps1 -UseDocker -PersistentBrowser -LaunchWebUI
```

## Integration with Browser-Use Ecosystem

The launcher seamlessly integrates with the broader browser-use ecosystem:

- **browser-use**: Core AI browser automation library
- **web-ui**: User-friendly interface for browser control
- **workflow-use**: Deterministic workflow automation

This integration provides:
- **AI Fallback**: Workflows can fall back to AI browser control when steps fail
- **Unified Interface**: Single web interface for both workflows and AI automation
- **Shared Configuration**: Common environment and API key management
- **Cross-Component Communication**: Workflows can trigger browser-use actions

## Support

For issues and questions:
- **GitHub Issues**: [workflow-use issues](https://github.com/browser-use/workflow-use/issues)
- **Discord**: [Browser Use Discord](https://link.browser-use.com/discord)
- **Documentation**: [Browser Use Docs](https://docs.browser-use.com)

## License

This launcher script is provided under the same license as the workflow-use project (MIT).

