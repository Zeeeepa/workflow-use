#!/usr/bin/env python3
"""
Workflow-Use Suite Main Entry Point
Unified launcher for workflow backend, browser-use web-ui, and integrated suite
"""

import asyncio
import os
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from typing import Optional
import signal
import threading
import argparse


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


class WorkflowSuite:
    def __init__(self):
        self.processes = []
        self.project_root = Path(__file__).parent
        self.workflows_dir = self.project_root / "workflows"
        self.ui_dir = self.project_root / "ui"
        self.webui_dir = self.project_root / "browser-use-web-ui"
        
    def print_colored(self, message: str, color: str = Colors.WHITE):
        """Print colored message to terminal"""
        print(f"{color}{message}{Colors.END}")
        
    def print_header(self):
        """Print application header"""
        print()
        self.print_colored("🚀 Workflow-Use Suite", Colors.BOLD + Colors.CYAN)
        self.print_colored("=" * 50, Colors.CYAN)
        self.print_colored("Unified launcher for workflow automation", Colors.BLUE)
        print()
        
    def check_prerequisites(self) -> bool:
        """Check if required tools are installed"""
        self.print_colored("🔍 Checking prerequisites...", Colors.CYAN)
        
        # Check Python
        try:
            version = sys.version_info
            if version.major == 3 and version.minor >= 11:
                self.print_colored(f"✅ Python {version.major}.{version.minor}.{version.micro}", Colors.GREEN)
            else:
                self.print_colored(f"❌ Python 3.11+ required. Found: {version.major}.{version.minor}", Colors.RED)
                return False
        except Exception as e:
            self.print_colored(f"❌ Python check failed: {e}", Colors.RED)
            return False
            
        # Check uv
        try:
            result = subprocess.run(["uv", "--version"], capture_output=True, text=True, check=True)
            self.print_colored(f"✅ uv found: {result.stdout.strip()}", Colors.GREEN)
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.print_colored("❌ uv not found. Please install uv: https://docs.astral.sh/uv/", Colors.RED)
            return False
            
        return True
        
    def setup_environment(self) -> bool:
        """Setup environment files"""
        self.print_colored("⚙️ Setting up environment...", Colors.CYAN)
        
        # Setup workflows .env
        workflows_env = self.workflows_dir / ".env"
        workflows_env_example = self.workflows_dir / ".env.example"
        
        if not workflows_env.exists() and workflows_env_example.exists():
            try:
                workflows_env.write_text(workflows_env_example.read_text())
                self.print_colored("✅ Created workflows/.env from example", Colors.GREEN)
                self.print_colored("📝 Please edit workflows/.env to add your API keys", Colors.YELLOW)
            except Exception as e:
                self.print_colored(f"❌ Failed to create workflows/.env: {e}", Colors.RED)
                return False
                
        # Setup browser-use web-ui .env if it exists
        if self.webui_dir.exists():
            webui_env = self.webui_dir / ".env"
            webui_env_example = self.webui_dir / ".env.example"
            
            if not webui_env.exists() and webui_env_example.exists():
                try:
                    webui_env.write_text(webui_env_example.read_text())
                    self.print_colored("✅ Created browser-use-web-ui/.env from example", Colors.GREEN)
                except Exception as e:
                    self.print_colored(f"⚠️ Could not create web-ui .env: {e}", Colors.YELLOW)
                    
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
                ], check=True, cwd=self.project_root)
                self.print_colored("✅ Browser-use web-ui cloned successfully", Colors.GREEN)
            except subprocess.CalledProcessError as e:
                self.print_colored(f"❌ Failed to clone browser-use web-ui: {e}", Colors.RED)
                return False
        else:
            self.print_colored("✅ Browser-use web-ui already exists", Colors.GREEN)
            
        return True
        
    def setup_webui_environment(self) -> bool:
        """Setup browser-use web-ui Python environment"""
        if not self.webui_dir.exists():
            return True
            
        self.print_colored("🐍 Setting up browser-use web-ui environment...", Colors.CYAN)
        
        try:
            # Create virtual environment in web-ui directory
            subprocess.run([
                "uv", "venv", str(self.webui_dir / ".venv")
            ], check=True, cwd=self.webui_dir)
            
            # Install dependencies
            subprocess.run([
                "uv", "pip", "install", "-r", "requirements.txt"
            ], check=True, cwd=self.webui_dir)
            
            # Install Playwright browsers
            subprocess.run([
                "uv", "run", "playwright", "install", "--with-deps"
            ], check=True, cwd=self.webui_dir)
            
            self.print_colored("✅ Browser-use web-ui environment ready", Colors.GREEN)
            return True
            
        except subprocess.CalledProcessError as e:
            self.print_colored(f"❌ Failed to setup web-ui environment: {e}", Colors.RED)
            return False
            
    def start_backend(self, host: str = "127.0.0.1", port: int = 8000) -> Optional[subprocess.Popen]:
        """Start workflow-use backend"""
        self.print_colored(f"🔧 Starting workflow backend on {host}:{port}...", Colors.CYAN)
        
        try:
            # Use uv to run the backend
            process = subprocess.Popen([
                "uv", "run", "python", "-m", "backend.api"
            ], cwd=self.workflows_dir, env={**os.environ, "HOST": host, "PORT": str(port)})
            
            self.processes.append(process)
            self.print_colored(f"✅ Workflow backend started (PID: {process.pid})", Colors.GREEN)
            return process
            
        except Exception as e:
            self.print_colored(f"❌ Failed to start workflow backend: {e}", Colors.RED)
            return None
            
    def start_webui(self, host: str = "127.0.0.1", port: int = 7788) -> Optional[subprocess.Popen]:
        """Start browser-use web-ui"""
        if not self.webui_dir.exists():
            self.print_colored("⚠️ Browser-use web-ui not found, skipping...", Colors.YELLOW)
            return None
            
        self.print_colored(f"🌐 Starting browser-use web-ui on {host}:{port}...", Colors.CYAN)
        
        try:
            process = subprocess.Popen([
                "uv", "run", "python", "webui.py", 
                "--ip", host, "--port", str(port)
            ], cwd=self.webui_dir)
            
            self.processes.append(process)
            self.print_colored(f"✅ Browser-use web-ui started (PID: {process.pid})", Colors.GREEN)
            return process
            
        except Exception as e:
            self.print_colored(f"❌ Failed to start web-ui: {e}", Colors.RED)
            return None
            
    def start_ui_dev(self, port: int = 5173) -> Optional[subprocess.Popen]:
        """Start workflow-use UI development server"""
        if not self.ui_dir.exists():
            self.print_colored("⚠️ UI directory not found, skipping...", Colors.YELLOW)
            return None
            
        self.print_colored(f"⚛️ Starting workflow UI dev server on port {port}...", Colors.CYAN)
        
        try:
            # Install dependencies if needed
            if not (self.ui_dir / "node_modules").exists():
                subprocess.run(["npm", "install"], check=True, cwd=self.ui_dir)
                
            process = subprocess.Popen([
                "npm", "run", "dev", "--", "--port", str(port)
            ], cwd=self.ui_dir)
            
            self.processes.append(process)
            self.print_colored(f"✅ Workflow UI started (PID: {process.pid})", Colors.GREEN)
            return process
            
        except Exception as e:
            self.print_colored(f"❌ Failed to start UI: {e}", Colors.RED)
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
        if self.processes:
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


def start_backend():
    """Entry point for backend only"""
    suite = WorkflowSuite()
    suite.print_header()
    
    if not suite.check_prerequisites():
        sys.exit(1)
        
    if not suite.setup_environment():
        sys.exit(1)
        
    try:
        process = suite.start_backend()
        if not process:
            sys.exit(1)
            
        print()
        suite.print_colored("🎉 Workflow backend is running!", Colors.BOLD + Colors.GREEN)
        suite.print_colored("   📡 API: http://127.0.0.1:8000", Colors.CYAN)
        suite.print_colored("   📚 Docs: http://127.0.0.1:8000/docs", Colors.CYAN)
        print()
        suite.print_colored("Press Ctrl+C to stop", Colors.YELLOW)
        
        # Wait for interrupt
        try:
            process.wait()
        except KeyboardInterrupt:
            suite.print_colored("\n🛑 Received interrupt signal", Colors.YELLOW)
            
    except Exception as e:
        suite.print_colored(f"❌ Unexpected error: {e}", Colors.RED)
        sys.exit(1)
    finally:
        suite.cleanup()


def start_webui():
    """Entry point for web-ui only"""
    suite = WorkflowSuite()
    suite.print_header()
    
    if not suite.check_prerequisites():
        sys.exit(1)
        
    if not suite.clone_webui_if_needed():
        sys.exit(1)
        
    if not suite.setup_webui_environment():
        sys.exit(1)
        
    if not suite.setup_environment():
        sys.exit(1)
        
    try:
        process = suite.start_webui()
        if not process:
            sys.exit(1)
            
        print()
        suite.print_colored("🎉 Browser-use web-ui is running!", Colors.BOLD + Colors.GREEN)
        suite.print_colored("   🌐 Web-UI: http://127.0.0.1:7788", Colors.CYAN)
        print()
        suite.print_colored("Press Ctrl+C to stop", Colors.YELLOW)
        
        # Wait for interrupt
        try:
            process.wait()
        except KeyboardInterrupt:
            suite.print_colored("\n🛑 Received interrupt signal", Colors.YELLOW)
            
    except Exception as e:
        suite.print_colored(f"❌ Unexpected error: {e}", Colors.RED)
        sys.exit(1)
    finally:
        suite.cleanup()


def start_suite():
    """Entry point for complete suite"""
    suite = WorkflowSuite()
    suite.print_header()
    
    if not suite.check_prerequisites():
        sys.exit(1)
        
    if not suite.clone_webui_if_needed():
        sys.exit(1)
        
    if not suite.setup_webui_environment():
        sys.exit(1)
        
    if not suite.setup_environment():
        sys.exit(1)
        
    try:
        # Start all services
        backend_process = suite.start_backend()
        webui_process = suite.start_webui()
        ui_process = suite.start_ui_dev()
        
        # Wait for services to start
        time.sleep(3)
        
        print()
        suite.print_colored("🎉 Workflow-Use Suite is running!", Colors.BOLD + Colors.GREEN)
        if backend_process:
            suite.print_colored("   📡 Backend API: http://127.0.0.1:8000", Colors.CYAN)
        if webui_process:
            suite.print_colored("   🌐 Browser Web-UI: http://127.0.0.1:7788", Colors.CYAN)
        if ui_process:
            suite.print_colored("   ⚛️ Workflow UI: http://127.0.0.1:5173", Colors.CYAN)
        print()
        suite.print_colored("Press Ctrl+C to stop all services", Colors.YELLOW)
        
        # Open browser to main interface
        if webui_process:
            time.sleep(2)
            suite.open_browser("http://127.0.0.1:7788")
        
        # Wait for interrupt
        try:
            while True:
                time.sleep(1)
                # Check if any critical process stopped
                if backend_process and backend_process.poll() is not None:
                    suite.print_colored("❌ Backend process stopped unexpectedly", Colors.RED)
                    break
                if webui_process and webui_process.poll() is not None:
                    suite.print_colored("❌ Web-UI process stopped unexpectedly", Colors.RED)
                    break
        except KeyboardInterrupt:
            suite.print_colored("\n🛑 Received interrupt signal", Colors.YELLOW)
            
    except Exception as e:
        suite.print_colored(f"❌ Unexpected error: {e}", Colors.RED)
        sys.exit(1)
    finally:
        suite.cleanup()


def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(description="Workflow-Use Suite Launcher")
    parser.add_argument("command", nargs="?", default="suite", 
                       choices=["backend", "webui", "suite"],
                       help="Component to launch (default: suite)")
    
    args = parser.parse_args()
    
    # Setup signal handlers
    def signal_handler(signum, frame):
        print("\n🛑 Received interrupt signal")
        sys.exit(0)
        
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    if args.command == "backend":
        start_backend()
    elif args.command == "webui":
        start_webui()
    else:
        start_suite()


if __name__ == "__main__":
    main()

