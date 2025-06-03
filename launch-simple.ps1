#Requires -Version 5.1
<#
.SYNOPSIS
    Simple Browser-Use Suite Launcher
    
.DESCRIPTION
    A simplified PowerShell script to launch browser-use with web-ui and workflows
    
.PARAMETER WebUIPort
    Port for the web-ui interface (default: 7788)
    
.PARAMETER WorkflowPort
    Port for the workflow backend (default: 8000)
    
.EXAMPLE
    .\launch-simple.ps1
    Basic launch with all components
#>

[CmdletBinding()]
param(
    [int]$WebUIPort = 7788,
    [int]$WorkflowPort = 8000
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Simple output functions
function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️ $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Warn {
    param([string]$Message)
    Write-Host "⚠️ $Message" -ForegroundColor Yellow
}

function Write-Err {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Banner {
    Write-Host ""
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host "   🚀 Browser-Use Suite Launcher" -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host ""
}

function Test-Prerequisites {
    Write-Info "Checking prerequisites..."
    
    $allGood = $true
    
    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Python found: $pythonVersion"
        } else {
            Write-Err "Python not found"
            $allGood = $false
        }
    } catch {
        Write-Err "Python not found"
        $allGood = $false
    }
    
    # Check Git
    try {
        $gitVersion = git --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Git found: $gitVersion"
        } else {
            Write-Err "Git not found"
            $allGood = $false
        }
    } catch {
        Write-Err "Git not found"
        $allGood = $false
    }
    
    return $allGood
}

function Clone-Repos {
    Write-Info "Setting up repositories..."
    
    $repos = @(
        @{ Name = "browser-use"; Url = "https://github.com/browser-use/browser-use.git" },
        @{ Name = "web-ui"; Url = "https://github.com/browser-use/web-ui.git" },
        @{ Name = "workflow-use"; Url = "https://github.com/browser-use/workflow-use.git" }
    )
    
    foreach ($repo in $repos) {
        if (Test-Path $repo.Name) {
            Write-Success "$($repo.Name) already exists"
        } else {
            Write-Info "Cloning $($repo.Name)..."
            git clone $repo.Url $repo.Name
            if ($LASTEXITCODE -eq 0) {
                Write-Success "$($repo.Name) cloned successfully"
            } else {
                Write-Err "Failed to clone $($repo.Name)"
                return $false
            }
        }
    }
    
    return $true
}

function Setup-Dependencies {
    Write-Info "Installing dependencies..."
    
    # Setup browser-use
    if (Test-Path "browser-use") {
        Write-Info "Setting up browser-use..."
        Push-Location "browser-use"
        try {
            python -m venv .venv
            if ($IsWindows) {
                & ".\.venv\Scripts\Activate.ps1"
                & ".\.venv\Scripts\pip.exe" install -e .
                & ".\.venv\Scripts\pip.exe" install playwright
                & ".\.venv\Scripts\playwright.exe" install chromium
            } else {
                & source .venv/bin/activate
                pip install -e .
                pip install playwright
                playwright install chromium
            }
            Write-Success "browser-use setup complete"
        } catch {
            Write-Err "Failed to setup browser-use"
        } finally {
            Pop-Location
        }
    }
    
    # Setup web-ui
    if (Test-Path "web-ui") {
        Write-Info "Setting up web-ui..."
        Push-Location "web-ui"
        try {
            python -m venv .venv
            if ($IsWindows) {
                & ".\.venv\Scripts\Activate.ps1"
                & ".\.venv\Scripts\pip.exe" install -r requirements.txt
            } else {
                & source .venv/bin/activate
                pip install -r requirements.txt
            }
            Write-Success "web-ui setup complete"
        } catch {
            Write-Err "Failed to setup web-ui"
        } finally {
            Pop-Location
        }
    }
    
    # Setup workflow-use
    if (Test-Path "workflow-use") {
        Write-Info "Setting up workflow-use..."
        Push-Location "workflow-use"
        try {
            python -m venv .venv
            if ($IsWindows) {
                & ".\.venv\Scripts\Activate.ps1"
                & ".\.venv\Scripts\pip.exe" install -e .
            } else {
                & source .venv/bin/activate
                pip install -e .
            }
            Write-Success "workflow-use setup complete"
        } catch {
            Write-Err "Failed to setup workflow-use"
        } finally {
            Pop-Location
        }
    }
}

function Create-EnvFile {
    Write-Info "Creating environment file..."
    
    $envContent = @(
        "# Browser-Use Suite Configuration",
        "WEBUI_PORT=$WebUIPort",
        "WORKFLOW_PORT=$WorkflowPort",
        "",
        "# API Keys (add your actual keys here)",
        "OPENAI_API_KEY=your_openai_key_here",
        "ANTHROPIC_API_KEY=your_anthropic_key_here",
        "GOOGLE_API_KEY=your_google_key_here",
        "",
        "# Browser Configuration",
        "BROWSER_TYPE=chromium",
        "HEADLESS=false"
    )
    
    $envContent | Out-File -FilePath ".env" -Encoding UTF8
    Write-Success "Environment file created"
}

function Start-Services {
    Write-Info "Starting services..."
    
    # Start web-ui
    if (Test-Path "web-ui") {
        Write-Info "Starting web-ui on port $WebUIPort..."
        Push-Location "web-ui"
        try {
            $env:PORT = $WebUIPort
            if ($IsWindows) {
                Start-Process -FilePath ".\.venv\Scripts\python.exe" -ArgumentList "app.py" -WindowStyle Minimized
            } else {
                Start-Process -FilePath "./.venv/bin/python" -ArgumentList "app.py"
            }
            Write-Success "Web-UI started at http://localhost:$WebUIPort"
        } finally {
            Pop-Location
        }
    }
    
    # Start workflow backend
    if (Test-Path "workflow-use") {
        Write-Info "Starting workflow backend on port $WorkflowPort..."
        Push-Location "workflow-use"
        try {
            $env:PORT = $WorkflowPort
            if ($IsWindows) {
                Start-Process -FilePath ".\.venv\Scripts\python.exe" -ArgumentList "-m", "workflow_use.main" -WindowStyle Minimized
            } else {
                Start-Process -FilePath "./.venv/bin/python" -ArgumentList "-m", "workflow_use.main"
            }
            Write-Success "Workflow backend started at http://localhost:$WorkflowPort"
        } finally {
            Pop-Location
        }
    }
}

function Main {
    Write-Banner
    
    Write-Info "Launch Configuration:"
    Write-Info "- Web-UI Port: $WebUIPort"
    Write-Info "- Workflow Port: $WorkflowPort"
    Write-Host ""
    
    # Check prerequisites
    if (!(Test-Prerequisites)) {
        Write-Err "Prerequisites check failed. Please install missing components."
        exit 1
    }
    
    # Clone repositories
    if (!(Clone-Repos)) {
        Write-Err "Repository setup failed."
        exit 1
    }
    
    # Setup dependencies
    Setup-Dependencies
    
    # Create environment file
    Create-EnvFile
    
    # Start services
    Start-Services
    
    Write-Host ""
    Write-Success "Browser-Use Suite is starting up!"
    Write-Info "Services will be available at:"
    Write-Info "- Web-UI: http://localhost:$WebUIPort"
    Write-Info "- Workflow API: http://localhost:$WorkflowPort"
    Write-Host ""
    Write-Warn "Press Ctrl+C to stop services when done."
    
    # Keep script running
    try {
        while ($true) {
            Start-Sleep -Seconds 10
        }
    } catch {
        Write-Info "Stopping services..."
    }
}

# Run main function
Main

