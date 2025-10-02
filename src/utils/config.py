"""
Configuration management for the YouTube Comment Scraper.

This module provides centralized configuration handling using YAML files.
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigManager:
    """Manages application configuration from YAML files."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to the configuration file. If None, uses default.
        """
        if config_path is None:
            # Default to config.yaml in the project root
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config.yaml"
        
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from the YAML file."""
        try:
            if not self.config_path.exists():
                raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
            
            with open(self.config_path, 'r', encoding='utf-8') as file:
                self._config = yaml.safe_load(file) or {}
                
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in configuration file: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to load configuration: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.
        
        Args:
            key: Configuration key in dot notation (e.g., 'youtube.api_key')
            default: Default value if key is not found
            
        Returns:
            Configuration value or default
            
        Examples:
            >>> config = ConfigManager()
            >>> api_key = config.get('youtube.api_key')
            >>> max_results = config.get('youtube.max_results_per_request', 100)
        """
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value using dot notation.
        
        Args:
            key: Configuration key in dot notation
            value: Value to set
        """
        keys = key.split('.')
        config = self._config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
    
    def save(self) -> None:
        """Save the current configuration back to the file."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as file:
                yaml.safe_dump(self._config, file, default_flow_style=False, indent=2)
        except Exception as e:
            raise RuntimeError(f"Failed to save configuration: {e}")
    
    def reload(self) -> None:
        """Reload configuration from the file."""
        self._load_config()
    
    def get_youtube_config(self) -> Dict[str, Any]:
        """Get YouTube-specific configuration."""
        return self.get('youtube', {})
    
    def get_storage_config(self) -> Dict[str, Any]:
        """Get storage-specific configuration."""
        return self.get('storage', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging-specific configuration."""
        return self.get('logging', {})
    
    def get_rate_limit_config(self) -> Dict[str, Any]:
        """Get rate limiting configuration."""
        return self.get('rate_limit', {})
    
    def validate_required_config(self) -> None:
        """
        Validate that all required configuration values are present.
        
        Raises:
            ValueError: If required configuration is missing
        """
        required_keys = [
            'youtube.api_key',
            'storage.database_path',
            'logging.level'
        ]
        
        missing_keys = []
        for key in required_keys:
            if self.get(key) is None:
                missing_keys.append(key)
        
        if missing_keys:
            raise ValueError(f"Missing required configuration keys: {missing_keys}")
        
        # Validate API key is not the placeholder
        api_key = self.get('youtube.api_key')
        if api_key == "YOUR_YOUTUBE_API_KEY_HERE":
            raise ValueError("Please set a valid YouTube API key in config.yaml")
    
    def create_directories(self) -> None:
        """Create necessary directories based on configuration."""
        paths_to_create = [
            self.get('storage.raw_data_path'),
            self.get('storage.processed_data_path'),
            self.get('storage.exports_path'),
            os.path.dirname(self.get('logging.log_file', 'logs/scraper.log'))
        ]
        
        for path in paths_to_create:
            if path:
                Path(path).mkdir(parents=True, exist_ok=True)
    
    def __repr__(self) -> str:
        """String representation of the configuration manager."""
        return f"ConfigManager(config_path='{self.config_path}')"
