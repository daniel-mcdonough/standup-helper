"""Configuration management for standup automation."""

import configparser
import json
import os
from pathlib import Path
from typing import Dict, List, Optional


class Config:
    """Configuration manager for the application."""
    
    def __init__(self, config_path: str = "config.ini"):
        """Initialize configuration from file.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = config_path
        self._config = configparser.ConfigParser()
        self._load_config()
        self._load_secrets()
    
    def _load_config(self) -> None:
        """Load configuration from file."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        self._config.read(self.config_path)
    
    def _load_secrets(self) -> None:
        """Load secrets from environment variables or secrets file."""
        # Try to load from secrets file if it exists
        secrets_dir = Path(self._config.get("secrets", "SECRETS_DIR", fallback="./secrets"))
        secrets_file = secrets_dir / "secrets.env"
        
        if secrets_file.exists():
            self._load_env_file(secrets_file)
    
    def _load_env_file(self, env_file: Path) -> None:
        """Load environment variables from a .env file.
        
        Args:
            env_file: Path to the .env file
        """
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        os.environ[key] = value
        except Exception as e:
            # Don't fail if secrets file can't be loaded
            pass
    
    def _get_secret(self, key: str, fallback: Optional[str] = None) -> str:
        """Get a secret value from environment variables or config.
        
        Args:
            key: The secret key to retrieve
            fallback: Fallback value if not found in environment
            
        Returns:
            Secret value
        """
        # Try environment variable first
        env_value = os.getenv(key)
        if env_value:
            return env_value
        
        # Fall back to config file (for backward compatibility)
        if fallback is not None:
            return fallback
        
        raise ValueError(f"Secret '{key}' not found in environment variables or config")
    
    @property
    def project_id(self) -> str:
        """Google Cloud project ID."""
        return self._config.get("settings", "PROJECT_ID")
    
    @property
    def location(self) -> str:
        """Google Cloud location."""
        return self._config.get("settings", "LOCATION")
    
    @property
    def jira_domain(self) -> str:
        """Jira domain."""
        return self._config.get("settings", "JIRA_DOMAIN")
    
    @property
    def email(self) -> str:
        """User email."""
        return self._config.get("settings", "EMAIL")
    
    @property
    def jira_api_key(self) -> str:
        """Jira API key."""
        return self._get_secret(
            "JIRA_API_KEY",
            self._config.get("settings", "JIRA_API_KEY", fallback=None)
        )
    
    @property
    def git_author(self) -> str:
        """Git author name."""
        return self._config.get("settings", "GIT_AUTHOR")
    
    @property
    def github_app_id(self) -> Optional[str]:
        """GitHub App ID."""
        return self._config.get("settings", "GITHUB_APP_ID", fallback=None)
    
    @property
    def github_installation_id(self) -> Optional[str]:
        """GitHub Installation ID."""
        return self._config.get("settings", "GITHUB_INSTALLATION_ID", fallback=None)
    
    @property
    def private_key_path(self) -> Optional[str]:
        """Path to GitHub App private key."""
        try:
            return self._get_secret(
                "PRIVATE_KEY_PATH",
                self._config.get("settings", "PRIVATE_KEY_PATH", fallback=None)
            )
        except ValueError:
            return None
    
    @property
    def github_username(self) -> Optional[str]:
        """GitHub username."""
        return self._config.get("settings", "GITHUB_USERNAME", fallback=None)
    
    @property
    def notes_directory(self) -> Path:
        """Directory containing work notes."""
        return Path(self._config.get("paths", "NOTES_DIRECTORY"))
    
    @property
    def output_directory(self) -> Path:
        """Output directory for summaries."""
        return Path(self._config.get("paths", "OUTPUT_DIRECTORY"))
    
    @property
    def git_directories(self) -> List[str]:
        """List of Git directories to monitor."""
        return json.loads(self._config.get("paths", "GIT_DIRECTORIES"))
    
    @property
    def vertex_instruction(self) -> str:
        """Vertex AI instruction prompt."""
        return self._config.get("vertex", "INSTRUCTION")
    
    @property
    def vertex_model(self) -> str:
        """Vertex AI model name."""
        return self._config.get("vertex", "MODEL")
    
    @property
    def context_switcher_enabled(self) -> bool:
        """Whether context switcher integration is enabled."""
        return self._config.getboolean("context_switcher", "ENABLED", fallback=False)
    
    @property
    def context_switcher_url(self) -> str:
        """Context switcher API URL."""
        return self._config.get("context_switcher", "URL", fallback="http://127.0.0.1:5000")
    
    @property
    def context_switcher_days_back(self) -> int:
        """Number of days to look back for context switching data."""
        return self._config.getint("context_switcher", "DAYS_BACK", fallback=2)
    
    def get(self, section: str, key: str, fallback: str = None) -> str:
        """Get a configuration value.
        
        Args:
            section: Configuration section
            key: Configuration key
            fallback: Default value if key not found
            
        Returns:
            Configuration value
        """
        return self._config.get(section, key, fallback=fallback)