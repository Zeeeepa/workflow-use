#!/usr/bin/env python3
"""
Workflow-Use Suite - Single Python Deployment Script
Comprehensive deployment with fallback error handling
"""

import os
import sys
import subprocess
import shutil
import time
import json
from pathlib import Path
from typing import Optional, List, Dict, Any

# Color codes for Windows console
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    
    @staticmethod
    def print_colored(text: str, color: str = 'WHITE') -> None:
        """Print colored text to console"""
        color_code = getattr(Colors, color.upper(), Colors.WHITE)
        print(f"{color_code}{text}{Colors.RESET}")

def print_banner():
    """Print deployment banner"""
    Colors.print_colored("\n" + "="*50, "CYAN")
    Colors.print_colored("   🚀 Workflow-Use Suite - Python Deployer", "CYAN")
    Colors.print_colored("="*50, "CYAN")
    print()

def check_python_version() -> bool:
    """Check if Python version is 3.11+"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        Colors.print_colored(f"✅ Python {version.major}.{version.minor}.{version.micro} found", "GREEN")
        return True
    else:
        Colors.print_colored(f"❌ Python {version.major}.{version.minor}.{version.micro} found, need 3.11+", "RED")
        return False

def check_uv_available() -> bool:
    """Check if uv is available, install if needed"""
    try:
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            Colors.print_colored(f"✅ {result.stdout.strip()} ready", "GREEN")
            return True
    except FileNotFoundError:
        pass
    
    Colors.print_colored("⚠️ Installing uv...", "YELLOW")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "uv"], check=True)
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            Colors.print_colored(f"✅ {result.stdout.strip()} installed", "GREEN")
            return True
    except subprocess.CalledProcessError:
        Colors.print_colored("❌ Failed to install uv", "RED")
        return False
    
    return False

def create_virtual_environment() -> bool:
    """Create virtual environment"""
    Colors.print_colored("🔧 Setting up environment...", "CYAN")
    
    venv_path = Path(".venv")
    if venv_path.exists():
        Colors.print_colored("✅ Virtual environment exists", "GREEN")
        return True
    
    try:
        subprocess.run(["uv", "venv"], check=True)
        Colors.print_colored("✅ Virtual environment created", "GREEN")
        return True
    except subprocess.CalledProcessError:
        Colors.print_colored("❌ Failed to create virtual environment", "RED")
        return False

def install_dependencies_direct() -> bool:
    """Install dependencies directly without package building"""
    Colors.print_colored("📦 Installing dependencies directly...", "CYAN")
    
    dependencies = [
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0", 
        "pydantic>=2.5.0",
        "playwright>=1.40.0",
        "gradio>=4.0.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "rich>=13.7.0",
        "psutil>=5.9.0",
        "click>=8.1.0",
    ]
    
    for dep in dependencies:
        try:
            Colors.print_colored(f"Installing {dep.split('>=')[0]}...", "BLUE")
            subprocess.run(["uv", "pip", "install", dep], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            Colors.print_colored(f"❌ Failed to install {dep}", "RED")
            return False
    
    Colors.print_colored("✅ All dependencies installed", "GREEN")
    return True

def install_browsers() -> bool:
    """Install Playwright browsers"""
    Colors.print_colored("🌐 Installing browsers...", "CYAN")
    
    try:
        subprocess.run(["uv", "run", "playwright", "install", "chromium"], 
                      check=True, capture_output=True)
        Colors.print_colored("✅ Browsers ready", "GREEN")
        return True
    except subprocess.CalledProcessError:
        Colors.print_colored("⚠️ Browser installation had issues", "YELLOW")
        return False

def create_directories() -> None:
    """Create necessary directories"""
    directories = ["data", "logs", "workflows"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)

def create_env_file() -> None:
    """Create .env configuration file"""
    env_path = Path(".env")
    if not env_path.exists():
        env_content = """# Workflow-Use Suite Configuration
ENVIRONMENT=development
DEBUG=true

# API Keys (add your keys here)
# OPENAI_API_KEY=your_key_here
# ANTHROPIC_API_KEY=your_key_here
# GOOGLE_API_KEY=your_key_here

# Service Configuration
API_HOST=127.0.0.1
API_PORT=8000
WEBUI_HOST=127.0.0.1
WEBUI_PORT=7788
"""
        env_path.write_text(env_content)
        Colors.print_colored("✅ Configuration file created", "GREEN")

def create_launcher_script() -> None:
    """Create main launcher Python script"""
    Colors.print_colored("⚡ Creating launcher...", "CYAN")
    
    launcher_content = '''#!/usr/bin/env python3
"""
Workflow-Use Suite Launcher
Simple launcher without package building
"""

import os
import sys
import time
import subprocess
import signal
from pathlib import Path
from typing import List, Optional

def print_colored(text: str, color: str = "white") -> None:
    """Print colored message to console"""
    colors = {
        "red": "\\033[91m",
        "green": "\\033[92m", 
        "yellow": "\\033[93m",
        "blue": "\\033[94m",
        "magenta": "\\033[95m",
        "cyan": "\\033[96m",
        "white": "\\033[97m",
        "reset": "\\033[0m"
    }
    print(f"{colors.get(color, colors['white'])}{text}{colors['reset']}")

def print_banner():
    """Print startup banner"""
    print_colored("\\n" + "="*50, "cyan")
    print_colored("   🚀 Workflow-Use Suite Launcher", "cyan")
    print_colored("="*50, "cyan")

def start_backend() -> Optional[subprocess.Popen]:
    """Start the workflow backend"""
    print_colored("🔧 Starting workflow backend...", "blue")
    
    workflows_dir = Path("workflows")
    if not workflows_dir.exists():
        print_colored("⚠️ Workflows directory not found, creating minimal backend...", "yellow")
        
        # Create minimal backend structure
        backend_dir = workflows_dir / "backend"
        backend_dir.mkdir(parents=True, exist_ok=True)
        
        # Create minimal API
        api_content = """
import uvicorn
from fastapi import FastAPI

app = FastAPI(title="Workflow Backend", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "Workflow-Use Backend API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "workflow-backend"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
"""
        (backend_dir / "api.py").write_text(api_content)
        (backend_dir / "__init__.py").write_text("")
    
    try:
        # Use direct Python execution instead of uv run to avoid package building
        python_exe = sys.executable
        if os.name == "nt":
            process = subprocess.Popen(
                [python_exe, "-m", "backend.api"],
                cwd=workflows_dir,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
        else:
            process = subprocess.Popen(
                [python_exe, "-m", "backend.api"],
                cwd=workflows_dir,
                preexec_fn=os.setsid
            )
        
        print_colored("✅ Backend started successfully", "green")
        print_colored("   📡 API: http://127.0.0.1:8000", "cyan")
        print_colored("   📚 Docs: http://127.0.0.1:8000/docs", "cyan")
        return process
    except Exception as e:
        print_colored(f"❌ Failed to start backend: {e}", "red")
        return None

def start_webui() -> Optional[subprocess.Popen]:
    """Start the browser-use web-ui"""
    print_colored("🌐 Starting browser-use web-ui...", "blue")
    
    webui_dir = Path("browser-use-web-ui")
    if not webui_dir.exists():
        print_colored("📥 Cloning browser-use web-ui...", "yellow")
        try:
            subprocess.run([
                "git", "clone", 
                "https://github.com/browser-use/web-ui.git", 
                "browser-use-web-ui"
            ], check=True)
            print_colored("✅ Web-UI cloned successfully", "green")
        except subprocess.CalledProcessError:
            print_colored("❌ Failed to clone web-ui", "red")
            return None
    
    try:
        # Use direct Python execution
        python_exe = sys.executable
        if os.name == "nt":
            process = subprocess.Popen(
                [python_exe, "app.py"],
                cwd=webui_dir,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
        else:
            process = subprocess.Popen(
                [python_exe, "app.py"],
                cwd=webui_dir,
                preexec_fn=os.setsid
            )
        
        print_colored("✅ Web-UI started successfully", "green")
        print_colored("   🌐 Interface: http://127.0.0.1:7788", "cyan")
        return process
    except Exception as e:
        print_colored(f"❌ Failed to start web-ui: {e}", "red")
        return None

def cleanup_processes(processes: List[subprocess.Popen]):
    """Clean up running processes"""
    print_colored("\\n🛑 Stopping services...", "yellow")
    
    for process in processes:
        if process and process.poll() is None:
            try:
                if os.name == "nt":
                    subprocess.run(["taskkill", "/F", "/T", "/PID", str(process.pid)], 
                                 capture_output=True)
                else:
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    time.sleep(2)
                    if process.poll() is None:
                        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
            except:
                pass
    
    print_colored("✅ All services stopped", "green")

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print_colored("Usage: python launcher.py [backend|webui|suite]", "yellow")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    print_banner()
    
    processes = []
    
    try:
        if command == "backend":
            process = start_backend()
            if process:
                processes.append(process)
                print_colored("\\n✅ Backend is running. Press Ctrl+C to stop.", "green")
                process.wait()
        
        elif command == "webui":
            process = start_webui()
            if process:
                processes.append(process)
                print_colored("\\n✅ Web-UI is running. Press Ctrl+C to stop.", "green")
                process.wait()
        
        elif command == "suite":
            print_colored("\\n🚀 Starting complete workflow-use suite...", "magenta")
            print_colored("   Please wait for each service to initialize...\\n", "cyan")
            
            # Start backend first
            backend_process = start_backend()
            if backend_process:
                processes.append(backend_process)
                time.sleep(3)
            
            # Start web-ui
            webui_process = start_webui()
            if webui_process:
                processes.append(webui_process)
                time.sleep(2)
            
            if processes:
                print_colored("\\n" + "="*50, "green")
                print_colored("🎉 Workflow-Use Suite is running!", "green")
                print_colored("="*50, "green")
                print_colored("\\n📋 Available services:", "cyan")
                if backend_process:
                    print_colored("   📡 Backend API: http://127.0.0.1:8000", "white")
                    print_colored("   📚 API Docs: http://127.0.0.1:8000/docs", "white")
                if webui_process:
                    print_colored("   🌐 Browser Web-UI: http://127.0.0.1:7788", "white")
                print_colored("\\n💡 Press Ctrl+C to stop all services", "yellow")
                
                try:
                    while any(p.poll() is None for p in processes):
                        time.sleep(1)
                except KeyboardInterrupt:
                    pass
            else:
                print_colored("❌ Failed to start any services", "red")
                sys.exit(1)
        
        else:
            print_colored(f"❌ Unknown command: {command}", "red")
            print_colored("Available commands: backend, webui, suite", "yellow")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print_colored("\\n🛑 Received interrupt signal", "yellow")
    except Exception as e:
        print_colored(f"\\n❌ Unexpected error: {e}", "red")
    finally:
        cleanup_processes(processes)

if __name__ == "__main__":
    main()
'''
    
    Path("launcher.py").write_text(launcher_content)

def create_batch_launchers() -> None:
    """Create batch file launchers"""
    Colors.print_colored("🚀 Creating batch launchers...", "CYAN")
    
    # Main START.bat
    start_bat_content = '''@echo off
echo.
echo ==========================================
echo   🚀 Workflow-Use Suite Launcher
echo ==========================================
echo.
echo Services will be available at:
echo   📡 Backend API: http://127.0.0.1:8000
echo   🌐 Browser Web-UI: http://127.0.0.1:7788
echo.
echo Press Ctrl+C to stop all services
echo.

REM Use direct Python execution to avoid package building
python launcher.py suite

echo.
echo 🛑 All services stopped.
pause
'''
    Path("START.bat").write_text(start_bat_content)
    
    # Backend only
    backend_bat_content = '''@echo off
echo 🔧 Starting Backend Only...
python launcher.py backend
pause
'''
    Path("start-backend.bat").write_text(backend_bat_content)
    
    # Web-UI only
    webui_bat_content = '''@echo off
echo 🌐 Starting Web-UI Only...
python launcher.py webui
pause
'''
    Path("start-webui.bat").write_text(webui_bat_content)

def create_deployment_report() -> Dict[str, Any]:
    """Create deployment report"""
    report = {
        "deployment_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "files_created": [
            ".venv/",
            "START.bat",
            "start-backend.bat", 
            "start-webui.bat",
            "launcher.py",
            ".env",
            "data/",
            "logs/",
            "workflows/"
        ],
        "deployment_method": "direct_dependency_install",
        "status": "success"
    }
    
    Path("deployment_report.json").write_text(json.dumps(report, indent=2))
    return report

def main():
    """Main deployment function"""
    print_banner()
    
    # Step 1: Check Python version
    if not check_python_version():
        Colors.print_colored("Please install Python 3.11+ and try again.", "RED")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Step 2: Check/install uv
    if not check_uv_available():
        Colors.print_colored("Failed to install uv package manager.", "RED")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Step 3: Create virtual environment
    if not create_virtual_environment():
        Colors.print_colored("Failed to create virtual environment.", "RED")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Step 4: Install dependencies directly
    if not install_dependencies_direct():
        Colors.print_colored("Failed to install dependencies.", "RED")
        Colors.print_colored("Try running deploy-simple.bat as fallback.", "YELLOW")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Step 5: Install browsers (optional)
    install_browsers()
    
    # Step 6: Create directories
    create_directories()
    
    # Step 7: Create configuration
    create_env_file()
    
    # Step 8: Create launcher script
    create_launcher_script()
    
    # Step 9: Create batch launchers
    create_batch_launchers()
    
    # Step 10: Create deployment report
    report = create_deployment_report()
    
    # Success message
    print()
    Colors.print_colored("🎉 Deployment complete!", "GREEN")
    print()
    Colors.print_colored("📋 Created files:", "CYAN")
    for file in report["files_created"]:
        print(f"  - {file}")
    print()
    Colors.print_colored("💡 Next steps:", "YELLOW")
    print("  1. Edit .env to add your API keys")
    print("  2. Run START.bat to launch the suite")
    print()
    Colors.print_colored("🚀 Quick commands:", "GREEN")
    print("  - START.bat (complete suite)")
    print("  - start-backend.bat (backend only)")
    print("  - start-webui.bat (web-ui only)")
    print()
    
    # Ask if user wants to start now
    try:
        launch_now = input("Start the suite now? (y/N): ").strip().lower()
        if launch_now == 'y':
            print()
            Colors.print_colored("🚀 Launching...", "CYAN")
            subprocess.run([sys.executable, "launcher.py", "suite"])
        else:
            print()
            Colors.print_colored("✅ Ready! Run START.bat when you want to begin.", "GREEN")
    except KeyboardInterrupt:
        print()
        Colors.print_colored("✅ Deployment completed successfully.", "GREEN")
    
    print()
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()

