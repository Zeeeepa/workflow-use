#!/usr/bin/env python3
"""
Integrated Browser-Use Web-UI and Workflow-Use Launcher
This script launches the official browser-use web-ui alongside workflow-use backend
"""

import argparse
import asyncio
import os
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from typing import Optional, List
import signal
import threading


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'


class IntegratedLauncher:
    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        self.webui_dir = Path("browser-use-web-ui")
        self.workflow_dir = Path("workflows")
        
    def print_colored(self, message: str, color: str = Colors.WHITE):
        """Print colored message to terminal"""
        print(f"{color}{message}{Colors.END}")
        
    def print_header(self):
        """Print application header"""
        print()
        self.print_colored("🚀 Integrated Browser-Use Web-UI & Workflow-Use Launcher", Colors.BOLD + Colors.CYAN)
        self.print_colored("=" * 60, Colors.CYAN)
        self.print_colored("Launching official browser-use web-ui with workflow-use integration", Colors.BLUE)
        print()
        
    def check_prerequisites(self) -> bool:
        """Check if required tools are installed"""
        self.print_colored("🔍 Checking prerequisites...", Colors.CYAN)
        
        # Check Python
        try:
            result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
            version = result.stdout.strip()
            self.print_colored(f"✅ Python found: {version}", Colors.GREEN)
        except Exception as e:
            self.print_colored(f"❌ Python check failed: {e}", Colors.RED)
            return False
            
        # Check Git
        try:
            subprocess.run(["git", "--version"], capture_output=True, check=True)
            self.print_colored("✅ Git found", Colors.GREEN)
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.print_colored("❌ Git not found. Please install Git", Colors.RED)
            return False
            
        return True
        
    def clone_webui_if_needed(self) -> bool:
        """Clone browser-use web-ui if it doesn't exist"""
        if not self.webui_dir.exists():
            self.print_colored("📥 Cloning browser-use web-ui...", Colors.CYAN)
            try:
                subprocess.run([
                    "git", "clone", 
                    "https://github.com/browser-use/web-ui.git", 
                    str(self.webui_dir)
                ], check=True)
                self.print_colored("✅ Browser-use web-ui cloned successfully", Colors.GREEN)
            except subprocess.CalledProcessError as e:
                self.print_colored(f"❌ Failed to clone browser-use web-ui: {e}", Colors.RED)
                return False
        else:
            self.print_colored("✅ Browser-use web-ui already exists", Colors.GREEN)
            # Update existing repository
            try:
                subprocess.run(["git", "pull", "origin", "main"], 
                             cwd=self.webui_dir, check=True, capture_output=True)
                self.print_colored("🔄 Updated browser-use web-ui", Colors.BLUE)
            except subprocess.CalledProcessError:
                self.print_colored("⚠️ Could not update web-ui (continuing anyway)", Colors.YELLOW)
                
        return True
        
    def setup_webui_environment(self) -> bool:
        """Setup browser-use web-ui environment"""
        self.print_colored("🐍 Setting up browser-use web-ui environment...", Colors.CYAN)
        
        # Create virtual environment if it doesn't exist
        venv_path = self.webui_dir / ".venv"
        if not venv_path.exists():
            self.print_colored("Creating virtual environment...", Colors.BLUE)
            try:
                subprocess.run([
                    sys.executable, "-m", "venv", str(venv_path)
                ], check=True)
            except subprocess.CalledProcessError as e:
                self.print_colored(f"❌ Failed to create virtual environment: {e}", Colors.RED)
                return False
                
        # Get Python executable path
        if sys.platform == "win32":
            python_exe = venv_path / "Scripts" / "python.exe"
            pip_exe = venv_path / "Scripts" / "pip.exe"
        else:
            python_exe = venv_path / "bin" / "python"
            pip_exe = venv_path / "bin" / "pip"
            
        # Install dependencies
        self.print_colored("📦 Installing dependencies...", Colors.BLUE)
        try:
            # Upgrade pip
            subprocess.run([str(pip_exe), "install", "--upgrade", "pip"], 
                         cwd=self.webui_dir, check=True, capture_output=True)
            
            # Install requirements
            subprocess.run([str(pip_exe), "install", "-r", "requirements.txt"], 
                         cwd=self.webui_dir, check=True)
            
            # Install Playwright browsers
            subprocess.run([str(python_exe), "-m", "playwright", "install", "--with-deps"], 
                         cwd=self.webui_dir, check=True, capture_output=True)
            
            self.print_colored("✅ Dependencies installed successfully", Colors.GREEN)
        except subprocess.CalledProcessError as e:
            self.print_colored(f"❌ Failed to install dependencies: {e}", Colors.RED)
            return False
            
        return True
        
    def setup_environment_file(self) -> bool:
        """Setup .env file for web-ui"""
        env_file = self.webui_dir / ".env"
        env_example = self.webui_dir / ".env.example"
        
        if not env_file.exists() and env_example.exists():
            self.print_colored("⚙️ Setting up environment configuration...", Colors.CYAN)
            try:
                # Copy example file
                with open(env_example, 'r') as src, open(env_file, 'w') as dst:
                    dst.write(src.read())
                    
                self.print_colored("✅ Environment file created", Colors.GREEN)
                self.print_colored("📝 Please edit .env file to add your API keys:", Colors.YELLOW)
                self.print_colored("   Required: At least one of OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY", Colors.BLUE)
                
                return True
            except Exception as e:
                self.print_colored(f"❌ Failed to setup environment file: {e}", Colors.RED)
                return False
        elif env_file.exists():
            self.print_colored("✅ Environment file already exists", Colors.GREEN)
            return True
        else:
            self.print_colored("⚠️ No .env.example found, continuing without environment setup", Colors.YELLOW)
            return True
            
    def start_workflow_backend(self, port: int = 8000) -> Optional[subprocess.Popen]:
        """Start workflow-use backend if available"""
        if not self.workflow_dir.exists():
            self.print_colored("⚠️ Workflow-use backend not found, skipping...", Colors.YELLOW)
            return None
            
        self.print_colored(f"🔧 Starting workflow-use backend on port {port}...", Colors.CYAN)
        
        try:
            # Start the backend
            process = subprocess.Popen([
                sys.executable, "-m", "backend.api", 
                "--host", "127.0.0.1", "--port", str(port)
            ], cwd=self.workflow_dir)
            
            self.processes.append(process)
            self.print_colored(f"✅ Workflow-use backend started (PID: {process.pid})", Colors.GREEN)
            return process
            
        except Exception as e:
            self.print_colored(f"❌ Failed to start workflow backend: {e}", Colors.RED)
            return None
            
    def start_webui(self, ip: str = "127.0.0.1", port: int = 7788) -> Optional[subprocess.Popen]:
        """Start browser-use web-ui"""
        self.print_colored(f"🚀 Starting browser-use web-ui on {ip}:{port}...", Colors.CYAN)
        
        # Get Python executable path
        venv_path = self.webui_dir / ".venv"
        if sys.platform == "win32":
            python_exe = venv_path / "Scripts" / "python.exe"
        else:
            python_exe = venv_path / "bin" / "python"
            
        try:
            process = subprocess.Popen([
                str(python_exe), "webui.py", 
                "--ip", ip, "--port", str(port)
            ], cwd=self.webui_dir)
            
            self.processes.append(process)
            self.print_colored(f"✅ Browser-use web-ui started (PID: {process.pid})", Colors.GREEN)
            return process
            
        except Exception as e:
            self.print_colored(f"❌ Failed to start web-ui: {e}", Colors.RED)
            return None
            
    def wait_for_service(self, url: str, timeout: int = 30) -> bool:
        """Wait for a service to become available"""
        import urllib.request
        import urllib.error
        
        for _ in range(timeout):
            try:
                urllib.request.urlopen(url, timeout=1)
                return True
            except (urllib.error.URLError, OSError):
                time.sleep(1)
        return False
        
    def open_browser(self, url: str):
        """Open URL in default browser"""
        try:
            webbrowser.open(url)
            self.print_colored(f"🌐 Opened {url} in browser", Colors.GREEN)
        except Exception as e:
            self.print_colored(f"⚠️ Could not open browser: {e}", Colors.YELLOW)
            
    def cleanup(self):
        """Clean up running processes"""
        self.print_colored("\n🛑 Shutting down services...", Colors.YELLOW)
        
        for process in self.processes:
            if process.poll() is None:  # Process is still running
                try:
                    process.terminate()
                    process.wait(timeout=5)
                    self.print_colored(f"✅ Stopped process {process.pid}", Colors.GREEN)
                except subprocess.TimeoutExpired:
                    process.kill()
                    self.print_colored(f"🔪 Force killed process {process.pid}", Colors.RED)
                except Exception as e:
                    self.print_colored(f"⚠️ Error stopping process {process.pid}: {e}", Colors.YELLOW)
                    
    def run(self, args):
        """Main execution function"""
        try:
            self.print_header()
            
            # Check prerequisites
            if not self.check_prerequisites():
                return 1
                
            # Clone and setup web-ui
            if not self.clone_webui_if_needed():
                return 1
                
            if not self.setup_webui_environment():
                return 1
                
            if not self.setup_environment_file():
                return 1
                
            # Start services
            workflow_process = None
            if args.launch_workflow:
                workflow_process = self.start_workflow_backend(args.workflow_port)
                
            webui_process = self.start_webui(args.ip, args.webui_port)
            if not webui_process:
                return 1
                
            # Wait for services to start
            webui_url = f"http://{args.ip}:{args.webui_port}"
            self.print_colored(f"⏳ Waiting for web-ui to start at {webui_url}...", Colors.BLUE)
            
            if self.wait_for_service(webui_url):
                self.print_colored("✅ Web-UI is ready!", Colors.GREEN)
                if args.open_browser:
                    self.open_browser(webui_url)
            else:
                self.print_colored("⚠️ Web-UI may not be ready yet", Colors.YELLOW)
                
            # Print status
            print()
            self.print_colored("🎉 Services are running:", Colors.BOLD + Colors.GREEN)
            self.print_colored(f"   🌐 Browser-Use Web-UI: {webui_url}", Colors.CYAN)
            if workflow_process:
                self.print_colored(f"   🔧 Workflow-Use Backend: http://127.0.0.1:{args.workflow_port}", Colors.CYAN)
            print()
            self.print_colored("Press Ctrl+C to stop all services", Colors.YELLOW)
            
            # Wait for interrupt
            try:
                while True:
                    time.sleep(1)
                    # Check if processes are still running
                    if webui_process.poll() is not None:
                        self.print_colored("❌ Web-UI process stopped unexpectedly", Colors.RED)
                        break
            except KeyboardInterrupt:
                self.print_colored("\n🛑 Received interrupt signal", Colors.YELLOW)
                
            return 0
            
        except Exception as e:
            self.print_colored(f"❌ Unexpected error: {e}", Colors.RED)
            return 1
        finally:
            self.cleanup()


def main():
    parser = argparse.ArgumentParser(
        description="Integrated Browser-Use Web-UI and Workflow-Use Launcher"
    )
    parser.add_argument("--ip", default="127.0.0.1", help="IP address to bind web-ui to")
    parser.add_argument("--webui-port", type=int, default=7788, help="Port for browser-use web-ui")
    parser.add_argument("--workflow-port", type=int, default=8000, help="Port for workflow-use backend")
    parser.add_argument("--launch-workflow", action="store_true", help="Also launch workflow-use backend")
    parser.add_argument("--open-browser", action="store_true", help="Open browser automatically")
    
    args = parser.parse_args()
    
    launcher = IntegratedLauncher()
    
    # Setup signal handlers
    def signal_handler(signum, frame):
        launcher.cleanup()
        sys.exit(0)
        
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    return launcher.run(args)


if __name__ == "__main__":
    sys.exit(main())

