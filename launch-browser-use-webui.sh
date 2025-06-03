#!/bin/bash

# Browser-Use Web-UI Launcher for Workflow-Use
# This script sets up and launches the official browser-use web-ui integrated with workflow-use

set -e

# Default values
WORKING_DIR="."
WEBUI_PORT="7788"
WORKFLOW_PORT="8000"
WEBUI_IP="127.0.0.1"
USE_DOCKER=false
PERSISTENT_BROWSER=false
LAUNCH_WORKFLOW=false
SKIP_DEPS=false

# Color functions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_success() { echo -e "${GREEN}$1${NC}"; }
print_warning() { echo -e "${YELLOW}$1${NC}"; }
print_error() { echo -e "${RED}$1${NC}"; }
print_info() { echo -e "${CYAN}$1${NC}"; }

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --working-dir)
            WORKING_DIR="$2"
            shift 2
            ;;
        --webui-port)
            WEBUI_PORT="$2"
            shift 2
            ;;
        --workflow-port)
            WORKFLOW_PORT="$2"
            shift 2
            ;;
        --webui-ip)
            WEBUI_IP="$2"
            shift 2
            ;;
        --use-docker)
            USE_DOCKER=true
            shift
            ;;
        --persistent-browser)
            PERSISTENT_BROWSER=true
            shift
            ;;
        --launch-workflow)
            LAUNCH_WORKFLOW=true
            shift
            ;;
        --skip-deps)
            SKIP_DEPS=true
            shift
            ;;
        -h|--help)
            echo "Browser-Use Web-UI Launcher for Workflow-Use"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --working-dir DIR      Working directory (default: .)"
            echo "  --webui-port PORT      Web-UI port (default: 7788)"
            echo "  --workflow-port PORT   Workflow backend port (default: 8000)"
            echo "  --webui-ip IP          Web-UI IP address (default: 127.0.0.1)"
            echo "  --use-docker           Use Docker for deployment"
            echo "  --persistent-browser   Keep browser open between tasks"
            echo "  --launch-workflow      Also launch workflow-use backend"
            echo "  --skip-deps            Skip dependency checks"
            echo "  -h, --help             Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Header
echo ""
print_success "🚀 Browser-Use Web-UI Launcher for Workflow-Use"
echo "=================================================="
print_info "Integrating official browser-use web-ui with workflow-use"
echo ""

# Change to working directory
cd "$WORKING_DIR"

# Check prerequisites
if [ "$SKIP_DEPS" = false ]; then
    print_info "🔍 Checking prerequisites..."
    
    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1)
        if [[ $PYTHON_VERSION =~ Python\ 3\.1[1-9]|Python\ 3\.[2-9][0-9] ]]; then
            print_success "✅ Python found: $PYTHON_VERSION"
            PYTHON_CMD="python3"
        else
            print_error "❌ Python 3.11+ required. Found: $PYTHON_VERSION"
            exit 1
        fi
    elif command -v python &> /dev/null; then
        PYTHON_VERSION=$(python --version 2>&1)
        if [[ $PYTHON_VERSION =~ Python\ 3\.1[1-9]|Python\ 3\.[2-9][0-9] ]]; then
            print_success "✅ Python found: $PYTHON_VERSION"
            PYTHON_CMD="python"
        else
            print_error "❌ Python 3.11+ required. Found: $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "❌ Python not found. Please install Python 3.11+"
        exit 1
    fi

    # Check Git
    if command -v git &> /dev/null; then
        print_success "✅ Git found"
    else
        print_error "❌ Git not found. Please install Git"
        exit 1
    fi

    # Check Node.js for workflow-use UI
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version 2>&1)
        print_success "✅ Node.js found: $NODE_VERSION"
    else
        print_warning "⚠️ Node.js not found. Workflow-use UI may not work"
    fi
fi

if [ "$USE_DOCKER" = true ]; then
    # Docker setup
    print_info "🐳 Setting up Docker environment..."
    
    if command -v docker &> /dev/null; then
        print_success "✅ Docker found"
    else
        print_error "❌ Docker not found. Please install Docker"
        exit 1
    fi

    # Clone browser-use web-ui if not exists
    if [ ! -d "browser-use-web-ui" ]; then
        print_info "📥 Cloning browser-use web-ui..."
        git clone https://github.com/browser-use/web-ui.git browser-use-web-ui
    else
        print_success "✅ Browser-use web-ui already exists"
    fi

    cd browser-use-web-ui

    # Setup environment file
    if [ ! -f ".env" ]; then
        print_info "⚙️ Setting up environment configuration..."
        cp .env.example .env
        print_warning "📝 Please edit .env file to add your API keys before running"
        print_info "   Required: At least one of OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY"
    fi

    # Build and run with Docker
    print_info "🏗️ Building and starting Docker containers..."
    
    export WEBUI_PORT="$WEBUI_PORT"
    if [ "$PERSISTENT_BROWSER" = true ]; then
        export CHROME_PERSISTENT_SESSION="true"
    fi
    
    docker compose up --build

else
    # Local setup
    print_info "💻 Setting up local environment..."

    # Clone browser-use web-ui if not exists
    if [ ! -d "browser-use-web-ui" ]; then
        print_info "📥 Cloning browser-use web-ui..."
        git clone https://github.com/browser-use/web-ui.git browser-use-web-ui
    else
        print_success "✅ Browser-use web-ui already exists"
        cd browser-use-web-ui
        print_info "🔄 Updating browser-use web-ui..."
        git pull origin main || print_warning "⚠️ Could not update (continuing anyway)"
    fi

    cd browser-use-web-ui

    # Setup Python virtual environment
    print_info "🐍 Setting up Python environment..."
    
    if [ ! -d ".venv" ]; then
        print_info "Creating virtual environment..."
        $PYTHON_CMD -m venv .venv
    fi

    # Activate virtual environment
    print_info "Activating virtual environment..."
    source .venv/bin/activate

    # Install dependencies
    print_info "📦 Installing Python dependencies..."
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt

    # Install Playwright browsers
    print_info "🎭 Installing Playwright browsers..."
    playwright install --with-deps || print_warning "⚠️ Playwright installation had issues, but continuing..."

    # Setup environment file
    if [ ! -f ".env" ]; then
        print_info "⚙️ Setting up environment configuration..."
        cp .env.example .env
        print_warning "📝 Please edit .env file to add your API keys"
        print_info "   Required: At least one of OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY"
        
        # Try to open .env file for editing
        if command -v code &> /dev/null; then
            print_info "🔧 Opening .env in VS Code for editing..."
            code .env
        elif command -v nano &> /dev/null; then
            print_info "🔧 Opening .env in nano for editing..."
            nano .env
        elif command -v vim &> /dev/null; then
            print_info "🔧 Opening .env in vim for editing..."
            vim .env
        fi
    fi

    # Start workflow-use backend if requested
    if [ "$LAUNCH_WORKFLOW" = true ]; then
        print_info "🔧 Starting workflow-use backend..."
        cd ..
        
        if [ -d "workflows" ]; then
            (cd workflows && $PYTHON_CMD -m backend.api --host 127.0.0.1 --port "$WORKFLOW_PORT") &
            WORKFLOW_PID=$!
            print_success "✅ Workflow-use backend starting on port $WORKFLOW_PORT (PID: $WORKFLOW_PID)"
        else
            print_warning "⚠️ Workflow-use backend not found. Skipping..."
        fi
        
        cd browser-use-web-ui
    fi

    # Launch browser-use web-ui
    print_success "🚀 Launching browser-use web-ui..."
    print_info "   Web-UI will be available at: http://$WEBUI_IP:$WEBUI_PORT"
    print_info "   Press Ctrl+C to stop the server"
    echo ""

    # Cleanup function
    cleanup() {
        echo ""
        print_warning "🛑 Shutting down services..."
        if [ ! -z "$WORKFLOW_PID" ]; then
            kill $WORKFLOW_PID 2>/dev/null || true
            print_success "✅ Stopped workflow backend"
        fi
        exit 0
    }

    # Set up signal handlers
    trap cleanup SIGINT SIGTERM

    python webui.py --ip "$WEBUI_IP" --port "$WEBUI_PORT"
fi

echo ""
print_success "🎉 Browser-Use Web-UI setup complete!"
print_info "📖 For more information, visit: https://docs.browser-use.com"
echo ""

