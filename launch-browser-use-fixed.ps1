#Requires -Version 5.1
<#
.SYNOPSIS
    Complete Browser-Use Suite Launcher with Web-UI and Workflows
    
.DESCRIPTION
    This PowerShell script sets up and launches the complete Browser-Use ecosystem:
    - browser-use: Core AI browser automation
    - web-ui: Gradio-based web interface
    - workflow-use: Workflow automation and recording
    
.PARAMETER WorkingDirectory
    Directory where repositories will be cloned (default: current directory)
    
.PARAMETER UseDocker
    Use Docker containers instead of local Python installation
    
.PARAMETER PersistentBrowser
    Keep browser sessions persistent across runs
    
.PARAMETER WebUIPort
    Port for the web-ui interface (default: 7788)
    
.PARAMETER WorkflowPort
    Port for the workflow backend (default: 8000)
    
.PARAMETER LaunchMode
    Launch mode: 'all', 'webui', 'workflows', 'browser-only'
    
.PARAMETER SkipDependencies
    Skip dependency installation (use existing environment)
    
.PARAMETER Verbose
    Enable verbose output for debugging
    
.EXAMPLE
    .\launch-browser-use-fixed.ps1
    Basic launch with all components
    
.EXAMPLE
    .\launch-browser-use-fixed.ps1 -UseDocker -PersistentBrowser
    Launch using Docker with persistent browser sessions
    
.EXAMPLE
    .\launch-browser-use-fixed.ps1 -LaunchMode webui -WebUIPort 8080
    Launch only web-ui on custom port
#>

[CmdletBinding()]
param(
    [string]$WorkingDirectory = (Get-Location).Path,
    [switch]$UseDocker,
    [switch]$PersistentBrowser,
    [int]$WebUIPort = 7788,
    [int]$WorkflowPort = 8000,
    [ValidateSet('all', 'webui', 'workflows', 'browser-only')]
    [string]$LaunchMode = 'all',
    [switch]$SkipDependencies,
    [switch]$Verbose
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Enable verbose output if requested
if ($Verbose) {
    $VerbosePreference = "Continue"
}

# Global variables
$script:Processes = @()
$script:TempFiles = @()

# Color functions for better output
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    
    $colorMap = @{
        "Red" = [ConsoleColor]::Red
        "Green" = [ConsoleColor]::Green
        "Yellow" = [ConsoleColor]::Yellow
        "Blue" = [ConsoleColor]::Blue
        "Magenta" = [ConsoleColor]::Magenta
        "Cyan" = [ConsoleColor]::Cyan
        "White" = [ConsoleColor]::White
    }
    
    Write-Host $Message -ForegroundColor $colorMap[$Color]
}

function Write-Banner {
    param([string]$Title)
    
    Write-ColorOutput "`n$('='*60)" "Cyan"
    Write-ColorOutput "   🚀 $Title" "Cyan"
    Write-ColorOutput "$('='*60)" "Cyan"
    Write-Host ""
}

function Write-Step {
    param([string]$Message)
    Write-ColorOutput "🔧 $Message" "Blue"
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput "✅ $Message" "Green"
}

function Write-Warning {
    param([string]$Message)
    Write-ColorOutput "⚠️ $Message" "Yellow"
}

function Write-ErrorMessage {
    param([string]$Message)
    Write-ColorOutput "❌ $Message" "Red"
}

# Cleanup function
function Cleanup {
    Write-Step "Cleaning up processes and temporary files..."
    
    foreach ($process in $script:Processes) {
        if ($process -and !$process.HasExited) {
            try {
                $process.Kill()
                $process.WaitForExit(5000)
            }
            catch {
                Write-Warning "Failed to stop process: $($_.Exception.Message)"
            }
        }
    }
    
    foreach ($file in $script:TempFiles) {
        if (Test-Path $file) {
            Remove-Item $file -Force -ErrorAction SilentlyContinue
        }
    }
    
    Write-Success "Cleanup completed"
}

# Register cleanup on exit
Register-EngineEvent PowerShell.Exiting -Action { Cleanup }

function Test-Prerequisites {
    Write-Banner "Checking Prerequisites"
    
    $prerequisites = @()
    
    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Python found: $pythonVersion"
            $prerequisites += "python"
        }
        else {
            Write-ErrorMessage "Python not found or not in PATH"
        }
    }
    catch {
        Write-ErrorMessage "Python not found: $($_.Exception.Message)"
    }
    
    # Check Node.js (for web-ui extensions)
    try {
        $nodeVersion = node --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Node.js found: $nodeVersion"
            $prerequisites += "node"
        }
        else {
            Write-Warning "Node.js not found - some web-ui features may be limited"
        }
    }
    catch {
        Write-Warning "Node.js not found - some web-ui features may be limited"
    }
    
    # Check Git
    try {
        $gitVersion = git --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Git found: $gitVersion"
            $prerequisites += "git"
        }
        else {
            Write-ErrorMessage "Git not found or not in PATH"
        }
    }
    catch {
        Write-ErrorMessage "Git not found: $($_.Exception.Message)"
    }
    
    # Check Docker (if requested)
    if ($UseDocker) {
        try {
            $dockerVersion = docker --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Docker found: $dockerVersion"
                $prerequisites += "docker"
            }
            else {
                Write-ErrorMessage "Docker not found but UseDocker specified"
                return $false
            }
        }
        catch {
            Write-ErrorMessage "Docker not found: $($_.Exception.Message)"
            return $false
        }
    }
    
    # Check UV package manager
    try {
        $uvVersion = uv --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "UV found: $uvVersion"
            $prerequisites += "uv"
        }
        else {
            Write-Step "Installing UV package manager..."
            python -m pip install uv
            if ($LASTEXITCODE -eq 0) {
                Write-Success "UV installed successfully"
                $prerequisites += "uv"
            }
            else {
                Write-Warning "Failed to install UV - will use pip instead"
            }
        }
    }
    catch {
        Write-Warning "UV not available - will use pip instead"
    }
    
    return ($prerequisites -contains "python") -and ($prerequisites -contains "git")
}

function Clone-Repository {
    param(
        [string]$RepoUrl,
        [string]$LocalPath,
        [string]$DisplayName
    )
    
    if (Test-Path $LocalPath) {
        Write-Success "$DisplayName already exists at $LocalPath"
        return $true
    }
    
    Write-Step "Cloning $DisplayName..."
    try {
        git clone $RepoUrl $LocalPath
        if ($LASTEXITCODE -eq 0) {
            Write-Success "$DisplayName cloned successfully"
            return $true
        }
        else {
            Write-ErrorMessage "Failed to clone $DisplayName"
            return $false
        }
    }
    catch {
        $errorMsg = "Error cloning $DisplayName" + ": " + $_.Exception.Message
        Write-ErrorMessage $errorMsg
        return $false
    }
}

function Setup-BrowserUse {
    Write-Banner "Setting Up Browser-Use Core"
    
    $browserUsePath = Join-Path $WorkingDirectory "browser-use"
    
    if (!(Clone-Repository "https://github.com/browser-use/browser-use.git" $browserUsePath "Browser-Use Core")) {
        return $false
    }
    
    Push-Location $browserUsePath
    try {
        if (!$SkipDependencies) {
            Write-Step "Installing browser-use dependencies..."
            
            if (Get-Command uv -ErrorAction SilentlyContinue) {
                uv venv
                uv pip install -e .
                uv pip install playwright
                uv run playwright install chromium
            }
            else {
                python -m venv .venv
                if ($IsWindows) {
                    & ".\.venv\Scripts\Activate.ps1"
                }
                else {
                    & source .venv/bin/activate
                }
                pip install -e .
                pip install playwright
                playwright install chromium
            }
            
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Browser-use dependencies installed"
            }
            else {
                Write-ErrorMessage "Failed to install browser-use dependencies"
                return $false
            }
        }
        
        return $true
    }
    finally {
        Pop-Location
    }
}

function Setup-WebUI {
    Write-Banner "Setting Up Browser-Use Web-UI"
    
    $webUIPath = Join-Path $WorkingDirectory "browser-use-web-ui"
    
    if (!(Clone-Repository "https://github.com/browser-use/web-ui.git" $webUIPath "Browser-Use Web-UI")) {
        return $false
    }
    
    Push-Location $webUIPath
    try {
        if (!$SkipDependencies) {
            Write-Step "Installing web-ui dependencies..."
            
            # Install Python dependencies
            if (Get-Command uv -ErrorAction SilentlyContinue) {
                uv venv
                uv pip install -r requirements.txt
            }
            else {
                python -m venv .venv
                if ($IsWindows) {
                    & ".\.venv\Scripts\Activate.ps1"
                }
                else {
                    & source .venv/bin/activate
                }
                pip install -r requirements.txt
            }
            
            # Install Node.js dependencies if package.json exists
            if (Test-Path "package.json") {
                Write-Step "Installing Node.js dependencies for web-ui..."
                npm install
            }
            
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Web-UI dependencies installed"
            }
            else {
                Write-ErrorMessage "Failed to install web-ui dependencies"
                return $false
            }
        }
        
        return $true
    }
    finally {
        Pop-Location
    }
}

function Setup-WorkflowUse {
    Write-Banner "Setting Up Workflow-Use"
    
    $workflowPath = Join-Path $WorkingDirectory "workflow-use"
    
    if (!(Clone-Repository "https://github.com/browser-use/workflow-use.git" $workflowPath "Workflow-Use")) {
        return $false
    }
    
    Push-Location $workflowPath
    try {
        if (!$SkipDependencies) {
            Write-Step "Installing workflow-use dependencies..."
            
            if (Get-Command uv -ErrorAction SilentlyContinue) {
                uv venv
                uv pip install -e .
            }
            else {
                python -m venv .venv
                if ($IsWindows) {
                    & ".\.venv\Scripts\Activate.ps1"
                }
                else {
                    & source .venv/bin/activate
                }
                pip install -e .
            }
            
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Workflow-use dependencies installed"
            }
            else {
                Write-ErrorMessage "Failed to install workflow-use dependencies"
                return $false
            }
        }
        
        return $true
    }
    finally {
        Pop-Location
    }
}

function Create-EnvironmentFile {
    Write-Step "Creating environment configuration..."
    
    # Create environment content as separate variables to avoid string issues
    $envLines = @(
        "# Browser-Use Suite Configuration",
        "ENVIRONMENT=development",
        "DEBUG=true",
        "",
        "# API Keys (add your actual keys here)",
        "OPENAI_API_KEY=your_openai_key_here",
        "ANTHROPIC_API_KEY=your_anthropic_key_here", 
        "GOOGLE_API_KEY=your_google_key_here",
        "AZURE_OPENAI_API_KEY=your_azure_key_here",
        "DEEPSEEK_API_KEY=your_deepseek_key_here",
        "",
        "# Service Configuration",
        "WEBUI_PORT=$WebUIPort",
        "WORKFLOW_PORT=$WorkflowPort",
        "BROWSER_PERSISTENT=$($PersistentBrowser.ToString().ToLower())",
        "",
        "# Browser Configuration", 
        "BROWSER_TYPE=chromium",
        "HEADLESS=false",
        "BROWSER_ARGS=--no-sandbox --disable-dev-shm-usage",
        "",
        "# Workflow Configuration",
        "WORKFLOW_STORAGE_PATH=./workflows",
        "WORKFLOW_LOGS_PATH=./logs"
    )
    
    $envPath = Join-Path $WorkingDirectory ".env"
    $envLines | Out-File -FilePath $envPath -Encoding UTF8
    $script:TempFiles += $envPath
    
    Write-Success "Environment file created at $envPath"
}

function Start-WebUI {
    if ($LaunchMode -eq 'workflows' -or $LaunchMode -eq 'browser-only') {
        return $null
    }
    
    Write-Step "Starting Browser-Use Web-UI on port $WebUIPort..."
    
    $webUIPath = Join-Path $WorkingDirectory "browser-use-web-ui"
    
    if (!(Test-Path $webUIPath)) {
        Write-ErrorMessage "Web-UI not found at $webUIPath"
        return $null
    }
    
    try {
        $env:PORT = $WebUIPort
        $env:GRADIO_SERVER_PORT = $WebUIPort
        
        Push-Location $webUIPath
        
        if ($UseDocker) {
            # Docker implementation
            $dockerArgs = @(
                "run", "-d",
                "--name", "browser-use-webui",
                "-p", "${WebUIPort}:7788",
                "-v", "${WorkingDirectory}:/workspace",
                "--env-file", (Join-Path $WorkingDirectory ".env")
            )
            
            if ($PersistentBrowser) {
                $dockerArgs += @("-v", "browser-data:/browser-data")
            }
            
            $dockerArgs += @("browser-use-webui:latest")
            
            $process = Start-Process -FilePath "docker" -ArgumentList $dockerArgs -PassThru
        }
        else {
            # Local Python implementation
            if (Get-Command uv -ErrorAction SilentlyContinue) {
                $process = Start-Process -FilePath "uv" -ArgumentList @("run", "python", "app.py") -PassThru
            }
            else {
                if ($IsWindows) {
                    $process = Start-Process -FilePath ".\.venv\Scripts\python.exe" -ArgumentList @("app.py") -PassThru
                }
                else {
                    $process = Start-Process -FilePath "./.venv/bin/python" -ArgumentList @("app.py") -PassThru
                }
            }
        }
        
        if ($process) {
            $script:Processes += $process
            Write-Success "Web-UI started successfully"
            Write-ColorOutput "   🌐 Web Interface: http://localhost:$WebUIPort" "Cyan"
            
            # Wait a moment for startup
            Start-Sleep -Seconds 3
            
            return $process
        }
        else {
            Write-ErrorMessage "Failed to start Web-UI process"
            return $null
        }
    }
    catch {
        Write-ErrorMessage "Error starting Web-UI: $($_.Exception.Message)"
        return $null
    }
    finally {
        Pop-Location
    }
}

function Start-WorkflowBackend {
    if ($LaunchMode -eq 'webui' -or $LaunchMode -eq 'browser-only') {
        return $null
    }
    
    Write-Step "Starting Workflow-Use backend on port $WorkflowPort..."
    
    $workflowPath = Join-Path $WorkingDirectory "workflow-use"
    
    if (!(Test-Path $workflowPath)) {
        Write-ErrorMessage "Workflow-Use not found at $workflowPath"
        return $null
    }
    
    try {
        $env:PORT = $WorkflowPort
        $env:API_PORT = $WorkflowPort
        
        Push-Location $workflowPath
        
        if ($UseDocker) {
            # Docker implementation
            $dockerArgs = @(
                "run", "-d",
                "--name", "workflow-use-backend",
                "-p", "${WorkflowPort}:8000",
                "-v", "${WorkingDirectory}:/workspace",
                "--env-file", (Join-Path $WorkingDirectory ".env"),
                "workflow-use:latest"
            )
            
            $process = Start-Process -FilePath "docker" -ArgumentList $dockerArgs -PassThru
        }
        else {
            # Local Python implementation
            if (Get-Command uv -ErrorAction SilentlyContinue) {
                $process = Start-Process -FilePath "uv" -ArgumentList @("run", "python", "-m", "workflow_use.main") -PassThru
            }
            else {
                if ($IsWindows) {
                    $process = Start-Process -FilePath ".\.venv\Scripts\python.exe" -ArgumentList @("-m", "workflow_use.main") -PassThru
                }
                else {
                    $process = Start-Process -FilePath "./.venv/bin/python" -ArgumentList @("-m", "workflow_use.main") -PassThru
                }
            }
        }
        
        if ($process) {
            $script:Processes += $process
            Write-Success "Workflow backend started successfully"
            Write-ColorOutput "   📡 API Endpoint: http://localhost:$WorkflowPort" "Cyan"
            Write-ColorOutput "   📚 API Docs: http://localhost:$WorkflowPort/docs" "Cyan"
            
            # Wait a moment for startup
            Start-Sleep -Seconds 3
            
            return $process
        }
        else {
            Write-ErrorMessage "Failed to start Workflow backend process"
            return $null
        }
    }
    catch {
        Write-ErrorMessage "Error starting Workflow backend: $($_.Exception.Message)"
        return $null
    }
    finally {
        Pop-Location
    }
}

function Test-ServiceHealth {
    param(
        [string]$Url,
        [string]$ServiceName,
        [int]$MaxRetries = 10
    )
    
    Write-Step "Testing $ServiceName health at $Url..."
    
    for ($i = 1; $i -le $MaxRetries; $i++) {
        try {
            $response = Invoke-WebRequest -Uri $Url -Method GET -TimeoutSec 5 -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                Write-Success "$ServiceName is healthy"
                return $true
            }
        }
        catch {
            if ($i -eq $MaxRetries) {
                Write-Warning "$ServiceName health check failed after $MaxRetries attempts"
                return $false
            }
            Start-Sleep -Seconds 2
        }
    }
    
    return $false
}

function Show-ServiceStatus {
    Write-Banner "Service Status"
    
    $services = @()
    
    if ($LaunchMode -eq 'all' -or $LaunchMode -eq 'webui') {
        $webUIHealthy = Test-ServiceHealth "http://localhost:$WebUIPort" "Web-UI" 5
        $services += @{
            Name = "Browser-Use Web-UI"
            URL = "http://localhost:$WebUIPort"
            Status = if ($webUIHealthy) { "✅ Running" } else { "❌ Not responding" }
        }
    }
    
    if ($LaunchMode -eq 'all' -or $LaunchMode -eq 'workflows') {
        $workflowHealthy = Test-ServiceHealth "http://localhost:$WorkflowPort/health" "Workflow Backend" 5
        $services += @{
            Name = "Workflow-Use Backend"
            URL = "http://localhost:$WorkflowPort"
            Status = if ($workflowHealthy) { "✅ Running" } else { "❌ Not responding" }
        }
    }
    
    foreach ($service in $services) {
        Write-ColorOutput "📋 $($service.Name): $($service.Status)" "White"
        Write-ColorOutput "   🔗 $($service.URL)" "Cyan"
    }
    
    Write-Host ""
    Write-ColorOutput "💡 Press Ctrl+C to stop all services" "Yellow"
}

function Wait-ForUserInterrupt {
    Write-Host ""
    Write-ColorOutput "🎉 Browser-Use Suite is running!" "Green"
    Write-ColorOutput "Press Ctrl+C to stop all services..." "Yellow"
    
    try {
        while ($true) {
            Start-Sleep -Seconds 1
            
            # Check if any process has exited
            $runningProcesses = $script:Processes | Where-Object { $_ -and !$_.HasExited }
            if ($runningProcesses.Count -eq 0 -and $script:Processes.Count -gt 0) {
                Write-Warning "All services have stopped unexpectedly"
                break
            }
        }
    }
    catch [System.Management.Automation.PipelineStoppedException] {
        Write-Host ""
        Write-Step "Received interrupt signal, stopping services..."
    }
}

function Main {
    try {
        Write-Banner "Browser-Use Complete Suite Launcher"
        
        Write-ColorOutput "🎯 Launch Mode: $LaunchMode" "Magenta"
        Write-ColorOutput "🌐 Web-UI Port: $WebUIPort" "Magenta"
        Write-ColorOutput "📡 Workflow Port: $WorkflowPort" "Magenta"
        Write-ColorOutput "🐳 Docker Mode: $UseDocker" "Magenta"
        Write-ColorOutput "💾 Persistent Browser: $PersistentBrowser" "Magenta"
        Write-Host ""
        
        # Check prerequisites
        if (!(Test-Prerequisites)) {
            Write-ErrorMessage "Prerequisites check failed. Please install missing components."
            exit 1
        }
        
        # Change to working directory
        if (!(Test-Path $WorkingDirectory)) {
            New-Item -ItemType Directory -Path $WorkingDirectory -Force | Out-Null
        }
        Set-Location $WorkingDirectory
        
        # Setup components based on launch mode
        $setupSuccess = $true
        
        if ($LaunchMode -eq 'all' -or $LaunchMode -eq 'browser-only') {
            $setupSuccess = $setupSuccess -and (Setup-BrowserUse)
        }
        
        if ($LaunchMode -eq 'all' -or $LaunchMode -eq 'webui') {
            $setupSuccess = $setupSuccess -and (Setup-WebUI)
        }
        
        if ($LaunchMode -eq 'all' -or $LaunchMode -eq 'workflows') {
            $setupSuccess = $setupSuccess -and (Setup-WorkflowUse)
        }
        
        if (!$setupSuccess) {
            Write-ErrorMessage "Setup failed for one or more components"
            exit 1
        }
        
        # Create environment configuration
        Create-EnvironmentFile
        
        # Start services
        Write-Banner "Starting Services"
        
        $webUIProcess = Start-WebUI
        $workflowProcess = Start-WorkflowBackend
        
        # Show service status
        Start-Sleep -Seconds 5
        Show-ServiceStatus
        
        # Wait for user interrupt
        Wait-ForUserInterrupt
        
    }
    catch {
        $errorMsg = "Unexpected error: " + $_.Exception.Message
        Write-ErrorMessage $errorMsg
        Write-ErrorMessage $_.ScriptStackTrace
        exit 1
    }
    finally {
        Cleanup
    }
}

# Run main function
Main

