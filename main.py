#!/usr/bin/env python3
"""
Workflow-Use Suite Launcher - Enhanced Version
Central entry point with improved error handling, monitoring, and deployment capabilities
"""

import os
import sys
import time
import signal
import subprocess
import threading
import asyncio
from pathlib import Path
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager

import psutil
import requests
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.table import Table
from rich.live import Live

# Add workflow_use to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from workflow_use.core.config import get_settings
    from workflow_use.core.logger import get_logger, log_exception, performance_logger
    from workflow_use.core.exceptions import WorkflowError, BrowserError, ConfigError
except ImportError:
    # Fallback if workflow_use package is not available
    print("⚠️ Workflow-Use package not found, using basic functionality")
    get_settings = lambda: type('Settings', (), {
        'debug': False,
        'api': type('API', (), {'host': '127.0.0.1', 'port': 8000})(),
        'webui': type('WebUI', (), {'host': '127.0.0.1', 'port': 7788})(),
        'browser': type('Browser', (), {'headless': True})()
    })()
    get_logger = lambda name: type('Logger', (), {
        'info': print, 'error': print, 'warning': print, 'debug': print
    })()
    log_exception = lambda exc, **kwargs: print(f"Exception: {exc}")
    performance_logger = type('PerfLogger', (), {'log_timing': lambda *args, **kwargs: None})()
    WorkflowError = Exception
    BrowserError = Exception
    ConfigError = Exception

console = Console()
logger = get_logger(__name__)


class ServiceManager:
    """Enhanced service management with monitoring and health checks."""
    
    def __init__(self):
        """Initialize service manager."""
        self.processes: Dict[str, subprocess.Popen] = {}
        self.health_checks: Dict[str, str] = {
            "backend": "http://127.0.0.1:8000/health",
            "webui": "http://127.0.0.1:7788",
            "ui": "http://127.0.0.1:5173"
        }
        self.start_times: Dict[str, float] = {}
        self.settings = get_settings()
    
    def print_banner(self) -> None:
        """Print enhanced startup banner."""
        banner = Panel.fit(
            "[bold cyan]🚀 Workflow-Use Suite Launcher v2.0[/bold cyan]\n"
            "[dim]Enterprise-grade workflow automation with browser-use integration[/dim]",
            border_style="cyan"
        )
        console.print(banner)
    
    def check_environment(self) -> bool:
        """Enhanced environment checking."""
        console.print("\n[cyan]🔍 Checking environment...[/cyan]")
        
        checks = []
        
        # Check virtual environment
        venv_path = Path(".venv")
        if venv_path.exists():
            checks.append(("Virtual Environment", "✅", "green"))
        else:
            checks.append(("Virtual Environment", "❌", "red"))
            console.print("[red]❌ Virtual environment not found. Please run deploy-dev.bat first[/red]")
            return False
        
        # Check Python executable
        python_exe = venv_path / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        if python_exe.exists():
            checks.append(("Python Executable", "✅", "green"))
        else:
            checks.append(("Python Executable", "❌", "red"))
        
        # Check dependencies
        try:
            import fastapi, uvicorn, playwright
            checks.append(("Core Dependencies", "✅", "green"))
        except ImportError as e:
            checks.append(("Core Dependencies", "❌", "red"))
            console.print(f"[red]❌ Missing dependencies: {e}[/red]")
        
        # Check directories
        required_dirs = ["workflows", "logs", "data"]
        for dir_name in required_dirs:
            if Path(dir_name).exists():
                checks.append((f"{dir_name.title()} Directory", "✅", "green"))
            else:
                checks.append((f"{dir_name.title()} Directory", "⚠️", "yellow"))
        
        # Display results table
        table = Table(title="Environment Check Results")
        table.add_column("Component", style="cyan")
        table.add_column("Status", justify="center")
        
        for check_name, status, color in checks:
            table.add_row(check_name, f"[{color}]{status}[/{color}]")
        
        console.print(table)
        
        # Check if critical components are missing
        critical_failed = any(
            status == "❌" for _, status, _ in checks 
            if "Virtual Environment" in _ or "Python Executable" in _
        )
        
        return not critical_failed
    
    async def wait_for_service(self, service_name: str, timeout: int = 60) -> bool:
        """Wait for service to become available with progress tracking."""
        url = self.health_checks.get(service_name)
        if not url:
            return True
        
        with Progress(
            SpinnerColumn(),
            TextColumn(f"[cyan]Waiting for {service_name}..."),
            BarColumn(),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            task = progress.add_task(f"health_check_{service_name}", total=timeout)
            
            for i in range(timeout):
                try:
                    response = requests.get(url, timeout=2)
                    if response.status_code == 200:
                        progress.update(task, completed=timeout)
                        return True
                except requests.RequestException:
                    pass
                
                await asyncio.sleep(1)
                progress.update(task, advance=1)
            
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information for monitoring."""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('.').percent,
                "process_count": len(psutil.pids()),
                "boot_time": psutil.boot_time()
            }
        except Exception as e:
            logger.warning(f"Failed to get system info: {e}")
            return {}
    
    async def start_backend(self) -> bool:
        """Start the workflow backend with enhanced monitoring."""
        service_name = "backend"
        console.print(f"\n[blue]🔧 Starting {service_name}...[/blue]")
        
        workflows_dir = Path("workflows")
        if not workflows_dir.exists():
            console.print("[red]❌ Workflows directory not found[/red]")
            return False
        
        try:
            start_time = time.time()
            self.start_times[service_name] = start_time
            
            # Start backend process
            cmd = [sys.executable, "-m", "backend.api"]
            if os.name == "nt":
                process = subprocess.Popen(
                    cmd,
                    cwd=workflows_dir,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            else:
                process = subprocess.Popen(
                    cmd,
                    cwd=workflows_dir,
                    preexec_fn=os.setsid,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            
            self.processes[service_name] = process
            
            # Wait for service to be ready
            if await self.wait_for_service(service_name, 30):
                startup_time = (time.time() - start_time) * 1000
                performance_logger.log_timing(f"{service_name}_startup", startup_time)
                
                console.print(f"[green]✅ {service_name.title()} started successfully[/green]")
                console.print(f"[cyan]   📡 API: http://127.0.0.1:8000[/cyan]")
                console.print(f"[cyan]   📚 Docs: http://127.0.0.1:8000/docs[/cyan]")
                return True
            else:
                console.print(f"[yellow]⚠️ {service_name.title()} started but health check failed[/yellow]")
                return False
        
        except Exception as e:
            log_exception(e, message=f"Failed to start {service_name}")
            console.print(f"[red]❌ Failed to start {service_name}: {e}[/red]")
            return False
    
    async def start_webui(self) -> bool:
        """Start the browser-use web-ui with auto-cloning."""
        service_name = "webui"
        console.print(f"\n[blue]🌐 Starting {service_name}...[/blue]")
        
        webui_dir = Path("browser-use-web-ui")
        
        # Clone web-ui if it doesn't exist
        if not webui_dir.exists():
            console.print("[yellow]📥 Cloning browser-use web-ui...[/yellow]")
            try:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[cyan]Cloning repository..."),
                    console=console
                ) as progress:
                    task = progress.add_task("clone", total=None)
                    
                    result = subprocess.run([
                        "git", "clone", 
                        "https://github.com/browser-use/web-ui.git", 
                        "browser-use-web-ui"
                    ], capture_output=True, text=True, timeout=60)
                    
                    if result.returncode == 0:
                        console.print("[green]✅ Web-UI cloned successfully[/green]")
                    else:
                        console.print(f"[red]❌ Failed to clone web-ui: {result.stderr}[/red]")
                        return False
            
            except subprocess.TimeoutExpired:
                console.print("[red]❌ Git clone timed out[/red]")
                return False
            except Exception as e:
                log_exception(e, message="Failed to clone web-ui")
                console.print(f"[red]❌ Failed to clone web-ui: {e}[/red]")
                return False
        
        try:
            start_time = time.time()
            self.start_times[service_name] = start_time
            
            # Start web-ui process
            cmd = [sys.executable, "app.py"]
            if os.name == "nt":
                process = subprocess.Popen(
                    cmd,
                    cwd=webui_dir,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            else:
                process = subprocess.Popen(
                    cmd,
                    cwd=webui_dir,
                    preexec_fn=os.setsid,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            
            self.processes[service_name] = process
            
            # Wait for service to be ready
            if await self.wait_for_service(service_name, 60):
                startup_time = (time.time() - start_time) * 1000
                performance_logger.log_timing(f"{service_name}_startup", startup_time)
                
                console.print(f"[green]✅ {service_name.title()} started successfully[/green]")
                console.print(f"[cyan]   🌐 Interface: http://127.0.0.1:7788[/cyan]")
                return True
            else:
                console.print(f"[yellow]⚠️ {service_name.title()} started but may still be loading[/yellow]")
                return False
        
        except Exception as e:
            log_exception(e, message=f"Failed to start {service_name}")
            console.print(f"[red]❌ Failed to start {service_name}: {e}[/red]")
            return False
    
    async def start_workflow_ui(self) -> bool:
        """Start the workflow UI with dependency management."""
        service_name = "ui"
        console.print(f"\n[blue]⚛️ Starting workflow {service_name}...[/blue]")
        
        ui_dir = Path("ui")
        if not ui_dir.exists():
            console.print("[yellow]⚠️ UI directory not found, skipping[/yellow]")
            return False
        
        # Check and install Node.js dependencies
        node_modules = ui_dir / "node_modules"
        if not node_modules.exists():
            console.print("[yellow]📦 Installing UI dependencies...[/yellow]")
            try:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[cyan]Installing dependencies..."),
                    console=console
                ) as progress:
                    task = progress.add_task("npm_install", total=None)
                    
                    result = subprocess.run(
                        ["npm", "install"], 
                        cwd=ui_dir, 
                        capture_output=True, 
                        text=True,
                        timeout=300
                    )
                    
                    if result.returncode == 0:
                        console.print("[green]✅ UI dependencies installed[/green]")
                    else:
                        console.print(f"[red]❌ Failed to install UI dependencies: {result.stderr}[/red]")
                        return False
            
            except subprocess.TimeoutExpired:
                console.print("[red]❌ npm install timed out[/red]")
                return False
            except Exception as e:
                log_exception(e, message="Failed to install UI dependencies")
                console.print(f"[red]❌ Failed to install UI dependencies: {e}[/red]")
                return False
        
        try:
            start_time = time.time()
            self.start_times[service_name] = start_time
            
            # Start UI development server
            cmd = ["npm", "run", "dev"]
            if os.name == "nt":
                process = subprocess.Popen(
                    cmd,
                    cwd=ui_dir,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            else:
                process = subprocess.Popen(
                    cmd,
                    cwd=ui_dir,
                    preexec_fn=os.setsid,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            
            self.processes[service_name] = process
            
            # Wait for service to be ready
            if await self.wait_for_service(service_name, 30):
                startup_time = (time.time() - start_time) * 1000
                performance_logger.log_timing(f"{service_name}_startup", startup_time)
                
                console.print(f"[green]✅ Workflow {service_name.title()} started successfully[/green]")
                console.print(f"[cyan]   ⚛️ Interface: http://127.0.0.1:5173[/cyan]")
                return True
            else:
                console.print(f"[yellow]⚠️ Workflow {service_name.title()} started but may still be loading[/yellow]")
                return False
        
        except Exception as e:
            log_exception(e, message=f"Failed to start workflow {service_name}")
            console.print(f"[red]❌ Failed to start workflow {service_name}: {e}[/red]")
            return False
    
    def get_service_status(self) -> Table:
        """Get current status of all services."""
        table = Table(title="Service Status")
        table.add_column("Service", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("PID", justify="center")
        table.add_column("Uptime", justify="center")
        table.add_column("Memory", justify="center")
        
        for service_name in ["backend", "webui", "ui"]:
            process = self.processes.get(service_name)
            
            if process and process.poll() is None:
                try:
                    # Get process info
                    proc = psutil.Process(process.pid)
                    memory_mb = proc.memory_info().rss / 1024 / 1024
                    
                    # Calculate uptime
                    start_time = self.start_times.get(service_name, time.time())
                    uptime_seconds = time.time() - start_time
                    uptime_str = f"{int(uptime_seconds // 60)}m {int(uptime_seconds % 60)}s"
                    
                    table.add_row(
                        service_name.title(),
                        "[green]Running[/green]",
                        str(process.pid),
                        uptime_str,
                        f"{memory_mb:.1f}MB"
                    )
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    table.add_row(
                        service_name.title(),
                        "[yellow]Unknown[/yellow]",
                        str(process.pid) if process else "N/A",
                        "N/A",
                        "N/A"
                    )
            else:
                table.add_row(
                    service_name.title(),
                    "[red]Stopped[/red]",
                    "N/A",
                    "N/A",
                    "N/A"
                )
        
        return table
    
    def cleanup_processes(self) -> None:
        """Enhanced process cleanup with graceful shutdown."""
        if not self.processes:
            return
        
        console.print("\n[yellow]🛑 Stopping services...[/yellow]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[cyan]Shutting down services..."),
            console=console
        ) as progress:
            task = progress.add_task("cleanup", total=len(self.processes))
            
            for service_name, process in self.processes.items():
                if process and process.poll() is None:
                    try:
                        console.print(f"[yellow]Stopping {service_name}...[/yellow]")
                        
                        if os.name == "nt":
                            # Windows
                            subprocess.run(
                                ["taskkill", "/F", "/T", "/PID", str(process.pid)], 
                                capture_output=True,
                                timeout=10
                            )
                        else:
                            # Unix/Linux - graceful shutdown
                            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                            
                            # Wait for graceful shutdown
                            try:
                                process.wait(timeout=5)
                            except subprocess.TimeoutExpired:
                                # Force kill if graceful shutdown fails
                                os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                        
                        console.print(f"[green]✅ {service_name.title()} stopped[/green]")
                    
                    except Exception as e:
                        console.print(f"[red]❌ Failed to stop {service_name}: {e}[/red]")
                
                progress.update(task, advance=1)
        
        self.processes.clear()
        self.start_times.clear()
        console.print("[green]✅ All services stopped[/green]")


async def main():
    """Enhanced main entry point with async support."""
    if len(sys.argv) < 2:
        console.print("[yellow]Usage: python main.py [backend|webui|ui|suite|status][/yellow]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    manager = ServiceManager()
    
    manager.print_banner()
    
    # Check environment
    if not manager.check_environment():
        sys.exit(1)
    
    try:
        if command == "backend":
            success = await manager.start_backend()
            if success:
                console.print("\n[green]✅ Backend is running. Press Ctrl+C to stop.[/green]")
                # Keep running until interrupted
                try:
                    while manager.processes.get("backend") and manager.processes["backend"].poll() is None:
                        await asyncio.sleep(1)
                except KeyboardInterrupt:
                    pass
        
        elif command == "webui":
            success = await manager.start_webui()
            if success:
                console.print("\n[green]✅ Web-UI is running. Press Ctrl+C to stop.[/green]")
                try:
                    while manager.processes.get("webui") and manager.processes["webui"].poll() is None:
                        await asyncio.sleep(1)
                except KeyboardInterrupt:
                    pass
        
        elif command == "ui":
            success = await manager.start_workflow_ui()
            if success:
                console.print("\n[green]✅ Workflow UI is running. Press Ctrl+C to stop.[/green]")
                try:
                    while manager.processes.get("ui") and manager.processes["ui"].poll() is None:
                        await asyncio.sleep(1)
                except KeyboardInterrupt:
                    pass
        
        elif command == "suite":
            console.print("\n[magenta]🚀 Starting complete workflow-use suite...[/magenta]")
            console.print("[cyan]   This will start all components sequentially[/cyan]")
            console.print("[cyan]   Please wait for each service to initialize...\n[/cyan]")
            
            # Start services sequentially
            services_started = []
            
            # Start backend first
            if await manager.start_backend():
                services_started.append("backend")
                await asyncio.sleep(3)  # Give backend time to fully start
            
            # Start web-ui
            if await manager.start_webui():
                services_started.append("webui")
                await asyncio.sleep(3)  # Give web-ui time to start
            
            # Start workflow UI
            if await manager.start_workflow_ui():
                services_started.append("ui")
            
            if services_started:
                # Display success panel
                success_panel = Panel.fit(
                    "[bold green]🎉 Workflow-Use Suite is running![/bold green]\n\n"
                    "[cyan]📋 Available services:[/cyan]\n"
                    "   📡 Backend API: http://127.0.0.1:8000\n"
                    "   📚 API Docs: http://127.0.0.1:8000/docs\n"
                    "   🌐 Browser Web-UI: http://127.0.0.1:7788\n" +
                    ("   ⚛️ Workflow UI: http://127.0.0.1:5173\n" if "ui" in services_started else "") +
                    "\n[yellow]💡 Press Ctrl+C to stop all services[/yellow]",
                    border_style="green"
                )
                console.print(success_panel)
                
                # Monitor services
                try:
                    while any(
                        p and p.poll() is None 
                        for p in manager.processes.values()
                    ):
                        await asyncio.sleep(5)
                        
                        # Optionally display status every 30 seconds
                        if int(time.time()) % 30 == 0:
                            console.print(manager.get_service_status())
                
                except KeyboardInterrupt:
                    pass
            else:
                console.print("[red]❌ Failed to start any services[/red]")
                sys.exit(1)
        
        elif command == "status":
            console.print(manager.get_service_status())
            
            # System information
            sys_info = manager.get_system_info()
            if sys_info:
                sys_panel = Panel.fit(
                    f"[cyan]💻 System Information[/cyan]\n"
                    f"CPU Usage: {sys_info.get('cpu_percent', 'N/A')}%\n"
                    f"Memory Usage: {sys_info.get('memory_percent', 'N/A')}%\n"
                    f"Disk Usage: {sys_info.get('disk_percent', 'N/A')}%\n"
                    f"Process Count: {sys_info.get('process_count', 'N/A')}",
                    border_style="blue"
                )
                console.print(sys_panel)
        
        else:
            console.print(f"[red]❌ Unknown command: {command}[/red]")
            console.print("[yellow]Available commands: backend, webui, ui, suite, status[/yellow]")
            sys.exit(1)
    
    except KeyboardInterrupt:
        console.print("\n[yellow]🛑 Received interrupt signal[/yellow]")
    except Exception as e:
        log_exception(e, message="Unexpected error in main")
        console.print(f"\n[red]❌ Unexpected error: {e}[/red]")
    finally:
        manager.cleanup_processes()


if __name__ == "__main__":
    # Run with asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Goodbye![/yellow]")
    except Exception as e:
        console.print(f"\n[red]❌ Fatal error: {e}[/red]")
        sys.exit(1)

