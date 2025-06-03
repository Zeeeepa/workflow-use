#!/usr/bin/env python3
"""
Workflow-Use Suite Launcher
Central entry point for launching workflow-use components
"""

import os
import sys
import time
import signal
import subprocess
import threading
from pathlib import Path
from typing import List, Optional

def print_colored(message: str, color: str = "white") -> None:
    """Print colored message to console"""
    colors = {
        "red": "\033[91m",
        "green": "\033[92m", 
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "reset": "\033[0m"
    }
    print(f"{colors.get(color, colors['white'])}{message}{colors['reset']}")

def print_banner():
    """Print startup banner"""
    print_colored("\n" + "="*50, "cyan")
    print_colored("   🚀 Workflow-Use Suite Launcher", "cyan")
    print_colored("="*50, "cyan")

def check_environment() -> bool:
    """Check if environment is properly set up"""
    if not Path(".venv").exists():
        print_colored("❌ Virtual environment not found", "red")
        print_colored("   Please run deploy-dev.bat first", "yellow")
        return False
    
    # Check if main dependencies exist
    venv_python = Path(".venv/Scripts/python.exe") if os.name == "nt" else Path(".venv/bin/python")
    if not venv_python.exists():
        print_colored("❌ Python not found in virtual environment", "red")
        return False
    
    return True

def wait_for_service(url: str, timeout: int = 30) -> bool:
    """Wait for service to become available"""
    import requests
    
    for i in range(timeout):
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(1)
    return False

def start_backend() -> Optional[subprocess.Popen]:
    """Start the workflow backend"""
    print_colored("🔧 Starting workflow backend...", "blue")
    
    # Change to workflows directory
    workflows_dir = Path("workflows")
    if not workflows_dir.exists():
        print_colored("❌ Workflows directory not found", "red")
        return None
    
    try:
        # Start backend process
        if os.name == "nt":
            process = subprocess.Popen(
                [sys.executable, "-m", "backend.api"],
                cwd=workflows_dir,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
        else:
            process = subprocess.Popen(
                [sys.executable, "-m", "backend.api"],
                cwd=workflows_dir,
                preexec_fn=os.setsid
            )
        
        # Wait for backend to start
        if wait_for_service("http://127.0.0.1:8000/health", 30):
            print_colored("✅ Backend started successfully", "green")
            print_colored("   📡 API: http://127.0.0.1:8000", "cyan")
            print_colored("   📚 Docs: http://127.0.0.1:8000/docs", "cyan")
        else:
            print_colored("⚠️ Backend started but health check failed", "yellow")
        
        return process
    except Exception as e:
        print_colored(f"❌ Failed to start backend: {e}", "red")
        return None

def start_webui() -> Optional[subprocess.Popen]:
    """Start the browser-use web-ui"""
    print_colored("🌐 Starting browser-use web-ui...", "blue")
    
    # Clone web-ui if it doesn't exist
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
        # Start web-ui process
        if os.name == "nt":
            process = subprocess.Popen(
                [sys.executable, "app.py"],
                cwd=webui_dir,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
        else:
            process = subprocess.Popen(
                [sys.executable, "app.py"],
                cwd=webui_dir,
                preexec_fn=os.setsid
            )
        
        # Wait for web-ui to start
        if wait_for_service("http://127.0.0.1:7788", 60):
            print_colored("✅ Web-UI started successfully", "green")
            print_colored("   🌐 Interface: http://127.0.0.1:7788", "cyan")
        else:
            print_colored("⚠️ Web-UI started but may still be loading", "yellow")
        
        return process
    except Exception as e:
        print_colored(f"❌ Failed to start web-ui: {e}", "red")
        return None

def start_workflow_ui() -> Optional[subprocess.Popen]:
    """Start the workflow UI"""
    print_colored("⚛️ Starting workflow UI...", "blue")
    
    ui_dir = Path("ui")
    if not ui_dir.exists():
        print_colored("⚠️ UI directory not found, skipping", "yellow")
        return None
    
    # Check if node_modules exists
    if not (ui_dir / "node_modules").exists():
        print_colored("📦 Installing UI dependencies...", "yellow")
        try:
            subprocess.run(["npm", "install"], cwd=ui_dir, check=True)
            print_colored("✅ UI dependencies installed", "green")
        except subprocess.CalledProcessError:
            print_colored("❌ Failed to install UI dependencies", "red")
            return None
    
    try:
        # Start UI development server
        if os.name == "nt":
            process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=ui_dir,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
        else:
            process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=ui_dir,
                preexec_fn=os.setsid
            )
        
        # Wait for UI to start
        if wait_for_service("http://127.0.0.1:5173", 30):
            print_colored("✅ Workflow UI started successfully", "green")
            print_colored("   ⚛️ Interface: http://127.0.0.1:5173", "cyan")
        else:
            print_colored("⚠️ Workflow UI started but may still be loading", "yellow")
        
        return process
    except Exception as e:
        print_colored(f"❌ Failed to start workflow UI: {e}", "red")
        return None

def cleanup_processes(processes: List[subprocess.Popen]):
    """Clean up running processes"""
    print_colored("\n🛑 Stopping services...", "yellow")
    
    for process in processes:
        if process and process.poll() is None:
            try:
                if os.name == "nt":
                    # Windows
                    subprocess.run(["taskkill", "/F", "/T", "/PID", str(process.pid)], 
                                 capture_output=True)
                else:
                    # Unix/Linux
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
        print_colored("Usage: python main.py [backend|webui|ui|suite]", "yellow")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    print_banner()
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    processes = []
    
    try:
        if command == "backend":
            process = start_backend()
            if process:
                processes.append(process)
                print_colored("\n✅ Backend is running. Press Ctrl+C to stop.", "green")
                process.wait()
        
        elif command == "webui":
            process = start_webui()
            if process:
                processes.append(process)
                print_colored("\n✅ Web-UI is running. Press Ctrl+C to stop.", "green")
                process.wait()
        
        elif command == "ui":
            process = start_workflow_ui()
            if process:
                processes.append(process)
                print_colored("\n✅ Workflow UI is running. Press Ctrl+C to stop.", "green")
                process.wait()
        
        elif command == "suite":
            print_colored("\n🚀 Starting complete workflow-use suite...", "magenta")
            print_colored("   This will start all components sequentially", "cyan")
            print_colored("   Please wait for each service to initialize...\n", "cyan")
            
            # Start backend first
            backend_process = start_backend()
            if backend_process:
                processes.append(backend_process)
                time.sleep(3)  # Give backend time to fully start
            
            # Start web-ui
            webui_process = start_webui()
            if webui_process:
                processes.append(webui_process)
                time.sleep(3)  # Give web-ui time to start
            
            # Start workflow UI
            ui_process = start_workflow_ui()
            if ui_process:
                processes.append(ui_process)
            
            if processes:
                print_colored("\n" + "="*50, "green")
                print_colored("🎉 Workflow-Use Suite is running!", "green")
                print_colored("="*50, "green")
                print_colored("\n📋 Available services:", "cyan")
                print_colored("   📡 Backend API: http://127.0.0.1:8000", "white")
                print_colored("   📚 API Docs: http://127.0.0.1:8000/docs", "white")
                print_colored("   🌐 Browser Web-UI: http://127.0.0.1:7788", "white")
                if len(processes) > 2:
                    print_colored("   ⚛️ Workflow UI: http://127.0.0.1:5173", "white")
                print_colored("\n💡 Press Ctrl+C to stop all services", "yellow")
                
                # Wait for any process to exit or Ctrl+C
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
            print_colored("Available commands: backend, webui, ui, suite", "yellow")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print_colored("\n🛑 Received interrupt signal", "yellow")
    except Exception as e:
        print_colored(f"\n❌ Unexpected error: {e}", "red")
    finally:
        cleanup_processes(processes)

if __name__ == "__main__":
    main()
