"""
Configuration management for Workflow-Use Suite.

Handles environment variables, settings validation, and configuration loading
with support for multiple environments and secure secret management.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    
    url: str = Field(
        default="sqlite:///./workflow_use.db",
        description="Database connection URL"
    )
    echo: bool = Field(
        default=False,
        description="Enable SQL query logging"
    )
    pool_size: int = Field(
        default=10,
        description="Database connection pool size"
    )
    max_overflow: int = Field(
        default=20,
        description="Maximum database connection overflow"
    )
    
    model_config = SettingsConfigDict(env_prefix="DB_")


class RedisSettings(BaseSettings):
    """Redis configuration settings."""
    
    url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )
    max_connections: int = Field(
        default=20,
        description="Maximum Redis connections"
    )
    socket_timeout: float = Field(
        default=5.0,
        description="Redis socket timeout in seconds"
    )
    
    model_config = SettingsConfigDict(env_prefix="REDIS_")


class BrowserSettings(BaseSettings):
    """Browser automation configuration."""
    
    headless: bool = Field(
        default=True,
        description="Run browser in headless mode"
    )
    disable_security: bool = Field(
        default=True,
        description="Disable browser security features"
    )
    timeout: int = Field(
        default=30000,
        description="Default browser timeout in milliseconds"
    )
    user_agent: Optional[str] = Field(
        default=None,
        description="Custom user agent string"
    )
    viewport_width: int = Field(
        default=1920,
        description="Browser viewport width"
    )
    viewport_height: int = Field(
        default=1080,
        description="Browser viewport height"
    )
    download_path: Optional[Path] = Field(
        default=None,
        description="Default download directory"
    )
    
    model_config = SettingsConfigDict(env_prefix="BROWSER_")
    
    @validator("download_path", pre=True)
    def validate_download_path(cls, v: Union[str, Path, None]) -> Optional[Path]:
        """Validate and convert download path."""
        if v is None:
            return None
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return path


class AISettings(BaseSettings):
    """AI provider configuration."""
    
    # OpenAI
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key"
    )
    openai_model: str = Field(
        default="gpt-4",
        description="Default OpenAI model"
    )
    
    # Anthropic
    anthropic_api_key: Optional[str] = Field(
        default=None,
        description="Anthropic API key"
    )
    anthropic_model: str = Field(
        default="claude-3-sonnet-20240229",
        description="Default Anthropic model"
    )
    
    # Google
    google_api_key: Optional[str] = Field(
        default=None,
        description="Google AI API key"
    )
    google_model: str = Field(
        default="gemini-pro",
        description="Default Google model"
    )
    
    # Azure OpenAI
    azure_openai_endpoint: Optional[str] = Field(
        default=None,
        description="Azure OpenAI endpoint"
    )
    azure_openai_api_key: Optional[str] = Field(
        default=None,
        description="Azure OpenAI API key"
    )
    azure_openai_api_version: str = Field(
        default="2023-12-01-preview",
        description="Azure OpenAI API version"
    )
    
    # DeepSeek
    deepseek_api_key: Optional[str] = Field(
        default=None,
        description="DeepSeek API key"
    )
    deepseek_model: str = Field(
        default="deepseek-chat",
        description="Default DeepSeek model"
    )
    
    # Ollama
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Ollama base URL"
    )
    ollama_model: str = Field(
        default="llama2",
        description="Default Ollama model"
    )
    
    model_config = SettingsConfigDict(env_prefix="AI_")
    
    def get_available_providers(self) -> List[str]:
        """Get list of available AI providers based on configured API keys."""
        providers = []
        
        if self.openai_api_key:
            providers.append("openai")
        if self.anthropic_api_key:
            providers.append("anthropic")
        if self.google_api_key:
            providers.append("google")
        if self.azure_openai_api_key and self.azure_openai_endpoint:
            providers.append("azure_openai")
        if self.deepseek_api_key:
            providers.append("deepseek")
        
        # Ollama is always available if running locally
        providers.append("ollama")
        
        return providers


class SecuritySettings(BaseSettings):
    """Security and authentication settings."""
    
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT tokens"
    )
    algorithm: str = Field(
        default="HS256",
        description="JWT algorithm"
    )
    access_token_expire_minutes: int = Field(
        default=30,
        description="Access token expiration time in minutes"
    )
    refresh_token_expire_days: int = Field(
        default=7,
        description="Refresh token expiration time in days"
    )
    password_min_length: int = Field(
        default=8,
        description="Minimum password length"
    )
    max_login_attempts: int = Field(
        default=5,
        description="Maximum login attempts before lockout"
    )
    lockout_duration_minutes: int = Field(
        default=15,
        description="Account lockout duration in minutes"
    )
    
    model_config = SettingsConfigDict(env_prefix="SECURITY_")


class APISettings(BaseSettings):
    """API server configuration."""
    
    host: str = Field(
        default="127.0.0.1",
        description="API server host"
    )
    port: int = Field(
        default=8000,
        description="API server port"
    )
    workers: int = Field(
        default=1,
        description="Number of worker processes"
    )
    reload: bool = Field(
        default=False,
        description="Enable auto-reload for development"
    )
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173", "http://localhost:7788"],
        description="Allowed CORS origins"
    )
    cors_methods: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        description="Allowed CORS methods"
    )
    cors_headers: List[str] = Field(
        default=["*"],
        description="Allowed CORS headers"
    )
    rate_limit_requests: int = Field(
        default=100,
        description="Rate limit requests per minute"
    )
    rate_limit_window: int = Field(
        default=60,
        description="Rate limit window in seconds"
    )
    
    model_config = SettingsConfigDict(env_prefix="API_")


class WebUISettings(BaseSettings):
    """Web UI configuration."""
    
    host: str = Field(
        default="127.0.0.1",
        description="Web UI host"
    )
    port: int = Field(
        default=7788,
        description="Web UI port"
    )
    share: bool = Field(
        default=False,
        description="Enable Gradio sharing"
    )
    auth: Optional[tuple] = Field(
        default=None,
        description="Basic authentication (username, password)"
    )
    theme: str = Field(
        default="default",
        description="UI theme"
    )
    title: str = Field(
        default="Workflow-Use Suite",
        description="Application title"
    )
    description: str = Field(
        default="AI-powered workflow automation with browser control",
        description="Application description"
    )
    
    model_config = SettingsConfigDict(env_prefix="WEBUI_")


class LoggingSettings(BaseSettings):
    """Logging configuration."""
    
    level: str = Field(
        default="INFO",
        description="Logging level"
    )
    format: str = Field(
        default="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        description="Log format string"
    )
    file_path: Optional[Path] = Field(
        default=None,
        description="Log file path"
    )
    file_rotation: str = Field(
        default="10 MB",
        description="Log file rotation size"
    )
    file_retention: str = Field(
        default="30 days",
        description="Log file retention period"
    )
    json_logs: bool = Field(
        default=False,
        description="Enable JSON structured logging"
    )
    
    model_config = SettingsConfigDict(env_prefix="LOG_")
    
    @validator("file_path", pre=True)
    def validate_file_path(cls, v: Union[str, Path, None]) -> Optional[Path]:
        """Validate and create log file path."""
        if v is None:
            return None
        path = Path(v)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path


class MonitoringSettings(BaseSettings):
    """Monitoring and metrics configuration."""
    
    enable_metrics: bool = Field(
        default=True,
        description="Enable Prometheus metrics"
    )
    metrics_port: int = Field(
        default=9090,
        description="Metrics server port"
    )
    health_check_interval: int = Field(
        default=30,
        description="Health check interval in seconds"
    )
    performance_tracking: bool = Field(
        default=True,
        description="Enable performance tracking"
    )
    error_tracking: bool = Field(
        default=True,
        description="Enable error tracking"
    )
    
    model_config = SettingsConfigDict(env_prefix="MONITORING_")


class Settings(BaseSettings):
    """Main application settings."""
    
    # Environment
    environment: str = Field(
        default="development",
        description="Application environment"
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode"
    )
    testing: bool = Field(
        default=False,
        description="Enable testing mode"
    )
    
    # Application info
    app_name: str = Field(
        default="Workflow-Use Suite",
        description="Application name"
    )
    app_version: str = Field(
        default="1.0.0",
        description="Application version"
    )
    app_description: str = Field(
        default="Enterprise-grade workflow automation with browser-use integration",
        description="Application description"
    )
    
    # Paths
    base_dir: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent,
        description="Base application directory"
    )
    data_dir: Path = Field(
        default_factory=lambda: Path("data"),
        description="Data directory"
    )
    logs_dir: Path = Field(
        default_factory=lambda: Path("logs"),
        description="Logs directory"
    )
    temp_dir: Path = Field(
        default_factory=lambda: Path("temp"),
        description="Temporary files directory"
    )
    
    # Component settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    browser: BrowserSettings = Field(default_factory=BrowserSettings)
    ai: AISettings = Field(default_factory=AISettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    api: APISettings = Field(default_factory=APISettings)
    webui: WebUISettings = Field(default_factory=WebUISettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    monitoring: MonitoringSettings = Field(default_factory=MonitoringSettings)
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    def __init__(self, **kwargs):
        """Initialize settings and create necessary directories."""
        super().__init__(**kwargs)
        self._create_directories()
    
    def _create_directories(self) -> None:
        """Create necessary directories."""
        for dir_path in [self.data_dir, self.logs_dir, self.temp_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.testing or self.environment.lower() == "testing"
    
    def get_database_url(self) -> str:
        """Get database URL with proper formatting."""
        if self.is_testing:
            return "sqlite:///./test_workflow_use.db"
        return self.database.url
    
    def get_redis_url(self) -> str:
        """Get Redis URL."""
        return self.redis.url
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        return self.model_dump()
    
    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Update settings from dictionary."""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get global settings instance."""
    return settings


def reload_settings() -> Settings:
    """Reload settings from environment."""
    global settings
    settings = Settings()
    return settings

