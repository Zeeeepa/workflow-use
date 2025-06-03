# Workflow Use Suite Launcher
# Enhanced PowerShell script for launching workflow-use with browser-use and web-ui integration
# Author: Codegen
# Version: 2.0

param(
    [string]$WorkingDirectory = "C:\workflow-use-suite",
    [string]$PythonVersion = "3.11",
    [int]$WorkflowUIPort = 5173,
    [int]$WorkflowAPIPort = 8000,
    [int]$WebUIPort = 7788,
    [string]$WebUIIP = "127.0.0.1",
    [switch]$SkipInstall,
    [switch]$UseDocker,
    [switch]$PersistentBrowser,
    [switch]$LaunchWebUI,
    [switch]$LaunchWorkflowGUI,
    [switch]$Help
)

# Color functions for better output
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    } else {
        $input | Write-Output
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Write-Success { Write-ColorOutput Green $args }
function Write-Warning { Write-ColorOutput Yellow $args }
function Write-Error { Write-ColorOutput Red $args }
function Write-Info { Write-ColorOutput Cyan $args }

# Help function
function Show-Help {
    Write-Host @"
Workflow Use Suite Launcher

DESCRIPTION:
    Enhanced launcher for workflow-use with browser-use and web-ui integration.
    Sets up the complete workflow automation ecosystem with AI browser control.

PARAMETERS:
    -WorkingDirectory   Directory to install components (default: C:\workflow-use-suite)
    -PythonVersion      Python version to use (default: 3.11)
    -WorkflowUIPort     Port for workflow GUI (default: 5173)
    -WorkflowAPIPort    Port for workflow API (default: 8000)
    -WebUIPort          Port for browser-use web UI (default: 7788)
    -WebUIIP            IP address for web interfaces (default: 127.0.0.1)
    -SkipInstall        Skip installation and just launch
    -UseDocker          Use Docker for browser-use web-ui
    -PersistentBrowser  Keep browser open between tasks
    -LaunchWebUI        Also launch browser-use web UI
    -LaunchWorkflowGUI  Launch workflow visual interface
    -Help               Show this help message

EXAMPLES:
    # Basic workflow-use setup
    .\launch-workflow-suite.ps1
    
    # Full suite with web UI and workflow GUI
    .\launch-workflow-suite.ps1 -LaunchWebUI -LaunchWorkflowGUI
    
    # Docker mode with persistent browser
    .\launch-workflow-suite.ps1 -UseDocker -PersistentBrowser -LaunchWebUI
    
    # Custom ports and directory
    .\launch-workflow-suite.ps1 -WorkingDirectory "D:\workflows" -WorkflowUIPort 3000 -WebUIPort 8080

FEATURES:
    - Workflow recording and execution
    - Browser automation with AI fallback
    - Visual workflow editor and manager
    - Integration with browser-use ecosystem
    - Support for multiple LLM providers
    - Docker deployment option

REQUIREMENTS:
    - Python 3.11+ (if not using Docker for all components)
    - Git
    - Node.js and npm
    - Docker and Docker Compose (if using -UseDocker)
"@
}

# Check if help was requested
if ($Help) {
    Show-Help
    exit 0
}

# Function to check if a command exists
function Test-Command($command) {
    try {
        Get-Command $command -ErrorAction Stop | Out-Null
        return $true
    } catch {
        return $false
    }
}

# Function to check prerequisites
function Test-Prerequisites {
    Write-Info "Checking prerequisites..."
    
    $missing = @()
    
    if (-not (Test-Command "git")) {
        $missing += "Git"
    }
    
    if (-not (Test-Command "python")) {
        $missing += "Python"
    }
    
    if (-not (Test-Command "node")) {
        $missing += "Node.js"
    }
    
    if (-not (Test-Command "npm")) {
        $missing += "npm"
    }
    
    if ($UseDocker) {
        if (-not (Test-Command "docker")) {
            $missing += "Docker"
        }
        if (-not (Test-Command "docker-compose")) {
            $missing += "Docker Compose"
        }
    }
    
    if (-not (Test-Command "uv")) {
        Write-Warning "UV package manager not found. Will use pip instead."
    }
    
    if ($missing.Count -gt 0) {
        Write-Error "Missing prerequisites: $($missing -join ', ')"
        Write-Error "Please install the missing components and try again."
        exit 1
    }
    
    Write-Success "All prerequisites found!"
}

# Function to create working directory
function New-WorkingDirectory {
    if (-not (Test-Path $WorkingDirectory)) {
        Write-Info "Creating working directory: $WorkingDirectory"
        New-Item -ItemType Directory -Path $WorkingDirectory -Force | Out-Null
    }
    Set-Location $WorkingDirectory
    Write-Success "Working directory: $WorkingDirectory"
}

# Function to clone repositories
function Get-Repositories {
    Write-Info "Cloning repositories..."
    
    $repos = @(
        @{Name="workflow-use"; URL="https://github.com/browser-use/workflow-use.git"}
    )
    
    # Add browser-use and web-ui if launching web UI
    if ($LaunchWebUI) {
        $repos += @{Name="browser-use"; URL="https://github.com/browser-use/browser-use.git"}
        $repos += @{Name="web-ui"; URL="https://github.com/browser-use/web-ui.git"}
    }
    
    foreach ($repo in $repos) {
        if (-not (Test-Path $repo.Name)) {
            Write-Info "Cloning $($repo.Name)..."
            git clone $repo.URL $repo.Name
            if ($LASTEXITCODE -ne 0) {
                Write-Error "Failed to clone $($repo.Name)"
                exit 1
            }
        } else {
            Write-Info "$($repo.Name) already exists, pulling latest changes..."
            Set-Location $repo.Name
            git pull
            Set-Location ..
        }
    }
    
    Write-Success "All repositories cloned/updated!"
}

# Function to build workflow extension
function Build-WorkflowExtension {
    Write-Info "Building workflow extension..."
    Set-Location "$WorkingDirectory\workflow-use\extension"
    
    Write-Info "Installing npm dependencies..."
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to install npm dependencies"
        exit 1
    }
    
    Write-Info "Building extension..."
    npm run build
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to build workflow extension"
        exit 1
    }
    
    Set-Location $WorkingDirectory
    Write-Success "Workflow extension built successfully!"
}

# Function to setup workflow environment
function Set-WorkflowEnvironment {
    Write-Info "Setting up workflow environment..."
    Set-Location "$WorkingDirectory\workflow-use\workflows"
    
    # Create virtual environment
    if (Test-Command "uv") {
        Write-Info "Using UV to sync workflow environment..."
        uv sync
    } else {
        Write-Info "Creating workflow virtual environment with pip..."
        python -m venv .venv
        if (Test-Path ".venv\Scripts\Activate.ps1") {
            & ".venv\Scripts\Activate.ps1"
            pip install -r requirements.txt
        } else {
            Write-Error "Failed to create virtual environment"
            exit 1
        }
    }
    
    # Install Playwright
    Write-Info "Installing Playwright for workflows..."
    if (Test-Path ".venv\Scripts\Activate.ps1") {
        & ".venv\Scripts\Activate.ps1"
    }
    playwright install chromium
    
    # Setup environment file
    if (-not (Test-Path ".env")) {
        Write-Info "Creating workflow .env file..."
        Copy-Item ".env.example" ".env"
        Write-Warning "Please edit workflows/.env file and add your OPENAI_API_KEY!"
    }
    
    Set-Location $WorkingDirectory
    Write-Success "Workflow environment setup complete!"
}

# Function to setup workflow UI
function Set-WorkflowUI {
    Write-Info "Setting up workflow UI..."
    Set-Location "$WorkingDirectory\workflow-use\ui"
    
    Write-Info "Installing UI dependencies..."
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to install UI dependencies"
        exit 1
    }
    
    Set-Location $WorkingDirectory
    Write-Success "Workflow UI setup complete!"
}

# Function to setup web UI environment (if requested)
function Set-WebUIEnvironment {
    if (-not $LaunchWebUI) {
        return
    }
    
    Write-Info "Setting up Browser Use Web UI environment..."
    Set-Location "$WorkingDirectory\web-ui"
    
    if ($UseDocker) {
        # Setup environment file for Docker
        if (-not (Test-Path ".env")) {
            Write-Info "Creating .env file for Docker..."
            Copy-Item ".env.example" ".env"
            Write-Warning "Please edit web-ui/.env file and add your API keys!"
        }
    } else {
        # Create virtual environment
        if (Test-Command "uv") {
            Write-Info "Using UV to create web UI virtual environment..."
            uv venv --python $PythonVersion
        } else {
            Write-Info "Using Python to create web UI virtual environment..."
            python -m venv .venv
        }
        
        # Activate virtual environment
        if (Test-Path ".venv\Scripts\Activate.ps1") {
            Write-Info "Activating web UI virtual environment..."
            & ".venv\Scripts\Activate.ps1"
        } else {
            Write-Error "Failed to create web UI virtual environment"
            exit 1
        }
        
        # Install dependencies
        Write-Info "Installing web UI Python dependencies..."
        if (Test-Command "uv") {
            uv pip install -r requirements.txt
        } else {
            pip install -r requirements.txt
        }
        
        # Install Playwright
        Write-Info "Installing Playwright for web UI..."
        playwright install
        
        # Setup environment file
        if (-not (Test-Path ".env")) {
            Write-Info "Creating web UI .env file..."
            Copy-Item ".env.example" ".env"
            Write-Warning "Please edit web-ui/.env file and add your API keys!"
        }
    }
    
    Set-Location $WorkingDirectory
    Write-Success "Web UI environment setup complete!"
}

# Function to start workflow API
function Start-WorkflowAPI {
    Write-Info "Starting Workflow API server..."
    Set-Location "$WorkingDirectory\workflow-use\workflows"
    
    # Activate virtual environment
    if (Test-Path ".venv\Scripts\Activate.ps1") {
        & ".venv\Scripts\Activate.ps1"
    }
    
    $apiJob = Start-Job -ScriptBlock {
        param($WorkingDir, $Port)
        Set-Location "$WorkingDir\workflow-use\workflows"
        if (Test-Path ".venv\Scripts\Activate.ps1") {
            & ".venv\Scripts\Activate.ps1"
        }
        uvicorn backend.api:app --reload --host 0.0.0.0 --port $Port
    } -ArgumentList $WorkingDirectory, $WorkflowAPIPort
    
    Set-Location $WorkingDirectory
    Write-Success "Workflow API started on port $WorkflowAPIPort (Job ID: $($apiJob.Id))"
    return $apiJob
}

# Function to start workflow UI
function Start-WorkflowUI {
    if (-not $LaunchWorkflowGUI) {
        return $null
    }
    
    Write-Info "Starting Workflow UI..."
    Set-Location "$WorkingDirectory\workflow-use\ui"
    
    $uiJob = Start-Job -ScriptBlock {
        param($WorkingDir, $Port)
        Set-Location "$WorkingDir\workflow-use\ui"
        $env:VITE_API_URL = "http://localhost:8000"
        npm run dev -- --port $Port --host 0.0.0.0
    } -ArgumentList $WorkingDirectory, $WorkflowUIPort
    
    Set-Location $WorkingDirectory
    Write-Success "Workflow UI started on port $WorkflowUIPort (Job ID: $($uiJob.Id))"
    return $uiJob
}

# Function to start web UI
function Start-WebUI {
    if (-not $LaunchWebUI) {
        return $null
    }
    
    Write-Info "Starting Browser Use Web UI..."
    Set-Location "$WorkingDirectory\web-ui"
    
    if ($UseDocker) {
        Write-Info "Starting Web UI with Docker..."
        if ($PersistentBrowser) {
            $env:CHROME_PERSISTENT_SESSION = "true"
        }
        docker-compose up --build -d
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Web UI started with Docker on port 7788!"
        } else {
            Write-Error "Failed to start Web UI with Docker"
        }
        Set-Location $WorkingDirectory
        return $null
    } else {
        $webUIJob = Start-Job -ScriptBlock {
            param($WorkingDir, $WebUIIP, $WebUIPort)
            Set-Location "$WorkingDir\web-ui"
            if (Test-Path ".venv\Scripts\Activate.ps1") {
                & ".venv\Scripts\Activate.ps1"
            }
            python webui.py --ip $WebUIIP --port $WebUIPort
        } -ArgumentList $WorkingDirectory, $WebUIIP, $WebUIPort
        
        Set-Location $WorkingDirectory
        Write-Success "Web UI started on port $WebUIPort (Job ID: $($webUIJob.Id))"
        return $webUIJob
    }
}

# Function to show workflow commands
function Show-WorkflowCommands {
    Write-Info @"

WORKFLOW COMMANDS:
Navigate to: $WorkingDirectory\workflow-use\workflows

Available commands:
1. Create a new workflow:
   python cli.py create-workflow

2. Run workflow as tool with AI prompt:
   python cli.py run-as-tool examples/example.workflow.json --prompt "your prompt here"

3. Run workflow with predefined variables:
   python cli.py run-workflow examples/example.workflow.json

4. Launch workflow GUI:
   python cli.py launch-gui

5. See all commands:
   python cli.py --help

PYTHON USAGE:
from workflow_use import Workflow
workflow = Workflow.load_from_file("example.workflow.json")
result = asyncio.run(workflow.run_as_tool("I want to search for 'workflow use'"))

"@
}

# Function to open browsers
function Open-Browsers {
    Start-Sleep -Seconds 5
    Write-Info "Opening browsers..."
    
    if ($LaunchWorkflowGUI) {
        Write-Info "Opening Workflow GUI..."
        Start-Process "http://$WebUIIP`:$WorkflowUIPort"
    }
    
    if ($LaunchWebUI) {
        Write-Info "Opening Browser Use Web UI..."
        if ($UseDocker) {
            Start-Process "http://$WebUIIP`:7788"
        } else {
            Start-Process "http://$WebUIIP`:$WebUIPort"
        }
    }
}

# Function to monitor jobs
function Watch-Jobs {
    param($Jobs)
    
    $activeJobs = $Jobs | Where-Object { $_ -ne $null }
    
    if ($activeJobs.Count -eq 0) {
        Write-Info "No background jobs to monitor."
        return
    }
    
    Write-Info "Monitoring background jobs. Press Ctrl+C to stop all services."
    
    try {
        while ($true) {
            Start-Sleep -Seconds 5
            
            foreach ($job in $activeJobs) {
                if ((Get-Job -Id $job.Id -ErrorAction SilentlyContinue).State -eq "Failed") {
                    Write-Error "Job $($job.Id) failed!"
                    Receive-Job -Id $job.Id
                }
            }
        }
    } catch {
        Write-Info "Stopping all services..."
    } finally {
        foreach ($job in $activeJobs) {
            Stop-Job $job.Id -ErrorAction SilentlyContinue
            Remove-Job $job.Id -ErrorAction SilentlyContinue
        }
        
        if ($UseDocker -and $LaunchWebUI) {
            Write-Info "Stopping Docker services..."
            Set-Location "$WorkingDirectory\web-ui"
            docker-compose down
        }
    }
}

# Main execution
function Main {
    Write-Success "Workflow Use Suite Launcher"
    Write-Success "============================"
    
    # Check prerequisites
    Test-Prerequisites
    
    # Create working directory
    New-WorkingDirectory
    
    if (-not $SkipInstall) {
        # Clone repositories
        Get-Repositories
        
        # Build workflow extension
        Build-WorkflowExtension
        
        # Setup environments
        Set-WorkflowEnvironment
        
        if ($LaunchWorkflowGUI) {
            Set-WorkflowUI
        }
        
        if ($LaunchWebUI) {
            Set-WebUIEnvironment
        }
        
        Write-Success "Installation complete!"
    }
    
    # Show workflow commands
    Show-WorkflowCommands
    
    # Start services
    Write-Info "Starting Workflow Use Suite..."
    
    $jobs = @()
    
    # Start workflow API (always needed for GUI)
    if ($LaunchWorkflowGUI) {
        $jobs += Start-WorkflowAPI
    }
    
    # Start workflow UI
    $workflowUIJob = Start-WorkflowUI
    if ($workflowUIJob) {
        $jobs += $workflowUIJob
    }
    
    # Start web UI
    $webUIJob = Start-WebUI
    if ($webUIJob) {
        $jobs += $webUIJob
    }
    
    # Open browsers
    Open-Browsers
    
    # Show status
    Write-Success @"

WORKFLOW USE SUITE IS RUNNING!

Services:
"@
    
    if ($LaunchWorkflowGUI) {
        Write-Info "- Workflow GUI: http://$WebUIIP`:$WorkflowUIPort"
        Write-Info "- Workflow API: http://$WebUIIP`:$WorkflowAPIPort"
    }
    
    if ($LaunchWebUI) {
        if ($UseDocker) {
            Write-Info "- Browser Use Web UI: http://$WebUIIP`:7788"
            Write-Info "- VNC Viewer: http://$WebUIIP`:6080/vnc.html"
        } else {
            Write-Info "- Browser Use Web UI: http://$WebUIIP`:$WebUIPort"
        }
    }
    
    Write-Info "- Workflow CLI: $WorkingDirectory\workflow-use\workflows"
    
    # Monitor jobs
    Watch-Jobs -Jobs $jobs
}

# Error handling
try {
    Main
} catch {
    Write-Error "An error occurred: $_"
    Write-Error $_.ScriptStackTrace
    exit 1
}

