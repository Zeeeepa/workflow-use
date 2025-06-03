# Browser-Use Web-UI Launcher for Workflow-Use
# This script sets up and launches the official browser-use web-ui integrated with workflow-use

param(
    [string]$WorkingDirectory = ".",
    [string]$WebUIPort = "7788",
    [string]$WorkflowPort = "8000", 
    [string]$WebUIIP = "127.0.0.1",
    [switch]$UseDocker,
    [switch]$PersistentBrowser,
    [switch]$LaunchWorkflowBackend,
    [switch]$SkipDependencies,
    [switch]$Verbose
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

# Header
Write-Host ""
Write-Success "🚀 Browser-Use Web-UI Launcher for Workflow-Use"
Write-Host "=================================================="
Write-Info "Integrating official browser-use web-ui with workflow-use"
Write-Host ""

# Set working directory
$originalLocation = Get-Location
Set-Location $WorkingDirectory

try {
    # Check prerequisites
    Write-Info "🔍 Checking prerequisites..."
    
    if (-not $SkipDependencies) {
        # Check Python
        try {
            $pythonVersion = python --version 2>&1
            if ($pythonVersion -match "Python 3\.1[1-9]|Python 3\.[2-9][0-9]") {
                Write-Success "✅ Python found: $pythonVersion"
            } else {
                Write-Error "❌ Python 3.11+ required. Found: $pythonVersion"
                exit 1
            }
        } catch {
            Write-Error "❌ Python not found. Please install Python 3.11+"
            exit 1
        }

        # Check Git
        try {
            git --version | Out-Null
            Write-Success "✅ Git found"
        } catch {
            Write-Error "❌ Git not found. Please install Git"
            exit 1
        }

        # Check Node.js for workflow-use UI
        try {
            $nodeVersion = node --version 2>&1
            Write-Success "✅ Node.js found: $nodeVersion"
        } catch {
            Write-Warning "⚠️ Node.js not found. Workflow-use UI may not work"
        }
    }

    if ($UseDocker) {
        # Docker setup
        Write-Info "🐳 Setting up Docker environment..."
        
        try {
            docker --version | Out-Null
            Write-Success "✅ Docker found"
        } catch {
            Write-Error "❌ Docker not found. Please install Docker Desktop"
            exit 1
        }

        # Clone browser-use web-ui if not exists
        if (-not (Test-Path "browser-use-web-ui")) {
            Write-Info "📥 Cloning browser-use web-ui..."
            git clone https://github.com/browser-use/web-ui.git browser-use-web-ui
            if ($LASTEXITCODE -ne 0) {
                Write-Error "❌ Failed to clone browser-use web-ui"
                exit 1
            }
        } else {
            Write-Success "✅ Browser-use web-ui already exists"
        }

        Set-Location browser-use-web-ui

        # Setup environment file
        if (-not (Test-Path ".env")) {
            Write-Info "⚙️ Setting up environment configuration..."
            Copy-Item ".env.example" ".env"
            Write-Warning "📝 Please edit .env file to add your API keys before running"
            Write-Info "   Required: At least one of OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY"
        }

        # Build and run with Docker
        Write-Info "🏗️ Building and starting Docker containers..."
        
        $env:WEBUI_PORT = $WebUIPort
        if ($PersistentBrowser) {
            $env:CHROME_PERSISTENT_SESSION = "true"
        }
        
        docker compose up --build
        
    } else {
        # Local setup
        Write-Info "💻 Setting up local environment..."

        # Clone browser-use web-ui if not exists
        if (-not (Test-Path "browser-use-web-ui")) {
            Write-Info "📥 Cloning browser-use web-ui..."
            git clone https://github.com/browser-use/web-ui.git browser-use-web-ui
            if ($LASTEXITCODE -ne 0) {
                Write-Error "❌ Failed to clone browser-use web-ui"
                exit 1
            }
        } else {
            Write-Success "✅ Browser-use web-ui already exists"
            Set-Location browser-use-web-ui
            Write-Info "🔄 Updating browser-use web-ui..."
            git pull origin main
        }

        Set-Location browser-use-web-ui

        # Setup Python virtual environment
        Write-Info "🐍 Setting up Python environment..."
        
        if (-not (Test-Path ".venv")) {
            Write-Info "Creating virtual environment..."
            python -m venv .venv
            if ($LASTEXITCODE -ne 0) {
                Write-Error "❌ Failed to create virtual environment"
                exit 1
            }
        }

        # Activate virtual environment
        Write-Info "Activating virtual environment..."
        if ($IsWindows -or $env:OS -eq "Windows_NT") {
            & ".venv\Scripts\Activate.ps1"
        } else {
            & source .venv/bin/activate
        }

        # Install dependencies
        Write-Info "📦 Installing Python dependencies..."
        python -m pip install --upgrade pip
        python -m pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) {
            Write-Error "❌ Failed to install Python dependencies"
            exit 1
        }

        # Install Playwright browsers
        Write-Info "🎭 Installing Playwright browsers..."
        playwright install --with-deps
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "⚠️ Playwright installation had issues, but continuing..."
        }

        # Setup environment file
        if (-not (Test-Path ".env")) {
            Write-Info "⚙️ Setting up environment configuration..."
            Copy-Item ".env.example" ".env"
            Write-Warning "📝 Please edit .env file to add your API keys"
            Write-Info "   Required: At least one of OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY"
            
            # Open .env file for editing
            if (Get-Command "code" -ErrorAction SilentlyContinue) {
                Write-Info "🔧 Opening .env in VS Code for editing..."
                code .env
            } elseif (Get-Command "notepad" -ErrorAction SilentlyContinue) {
                Write-Info "🔧 Opening .env in Notepad for editing..."
                notepad .env
            }
        }

        # Start workflow-use backend if requested
        if ($LaunchWorkflowBackend) {
            Write-Info "🔧 Starting workflow-use backend..."
            Set-Location ..
            
            if (Test-Path "workflows") {
                Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd workflows; python -m backend.api --host 127.0.0.1 --port $WorkflowPort"
                Write-Success "✅ Workflow-use backend starting on port $WorkflowPort"
            } else {
                Write-Warning "⚠️ Workflow-use backend not found. Skipping..."
            }
            
            Set-Location browser-use-web-ui
        }

        # Launch browser-use web-ui
        Write-Success "🚀 Launching browser-use web-ui..."
        Write-Info "   Web-UI will be available at: http://$WebUIIP`:$WebUIPort"
        Write-Info "   Press Ctrl+C to stop the server"
        Write-Host ""

        python webui.py --ip $WebUIIP --port $WebUIPort
    }

} catch {
    Write-Error "❌ An error occurred: $_"
    exit 1
} finally {
    Set-Location $originalLocation
}

Write-Host ""
Write-Success "🎉 Browser-Use Web-UI setup complete!"
Write-Info "📖 For more information, visit: https://docs.browser-use.com"
Write-Host ""

