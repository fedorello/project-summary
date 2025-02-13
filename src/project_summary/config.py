"""Configuration handling for Project Summary."""

from pathlib import Path
from typing import Set, Optional, Dict, Any
import yaml
import logging

logger = logging.getLogger(__name__)

class DirectoryConfig:
    """Configuration for a single directory to process."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize directory configuration.
        
        Args:
            config: Dictionary with configuration parameters
        """
        self.path = config.get('path', '.')
        self.extensions: Set[str] = set(
            ext.lower() if ext.startswith('.') else f'.{ext.lower()}'
            for ext in config.get('extensions', [])
        )
        self.files: Set[str] = set(config.get('files', []))
        self.dirs: Set[str] = set(config.get('dirs', []))
        self.exclude_dirs: Set[str] = set(config.get('exclude_dirs', []))
        self.exclude_files: Set[str] = set(config.get('exclude_files', []))
        self.max_file_size: int = config.get('max_file_size', 10 * 1024 * 1024)  # 10MB default
        self.output_name: Optional[str] = config.get('output_name', None)

    def __str__(self) -> str:
        """Return string representation of configuration."""
        return (
            f"DirectoryConfig(path='{self.path}', "
            f"extensions={self.extensions}, "
            f"files={self.files}, "
            f"dirs={self.dirs})"
        )

def load_config(config_path: Path) -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Dictionary with configuration
        
    Raises:
        FileNotFoundError: If configuration file doesn't exist
        yaml.YAMLError: If configuration file is invalid
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            if not isinstance(config, dict):
                raise yaml.YAMLError("Configuration must be a dictionary")
            return config
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_path}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"Invalid YAML in configuration file: {e}")
        raise