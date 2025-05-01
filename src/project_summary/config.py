# src/project_summary/config.py
"""Configuration handling for Project Summary."""
from pathlib import Path
from typing import Set, Optional, Dict, Any, List
import yaml
import logging

logger = logging.getLogger(__name__)

# Default configuration content as YAML string
DEFAULT_CONFIG_CONTENT: str = """
# Default configuration for project-summary tool
# Documentation: https://pypi.org/project/project-summary/

# Directory where the summary files will be saved.
output_dir: summaries/

# List of directories to analyze. You can add multiple entries.
directories:
  - path: . # Analyze the current directory (.) or specify a path (e.g., src/)

    # == Inclusion Rules ==
    # Files with these extensions will be included. Case-insensitive.
    # Example: ['.py', '.md', '.txt']
    extensions:
      - .py
      - .md
      # Add other extensions you need

    # Specific files to include, path relative to 'path' above.
    # Useful for config files or files without standard extensions.
    # Example: ['config/settings.ini', 'scripts/run_job.sh']
    files: []
      # - path/to/specific/file.ext

    # Specific files WITHOUT extensions to include by name. Case-sensitive.
    # Example: ['Dockerfile', 'Makefile', 'LICENSE']
    include_no_extension: []
      # - Dockerfile
      # - LICENSE
      # - Makefile

    # == Exclusion Rules ==
    # Directories to completely exclude from the scan (by name or relative path).
    # Common examples: virtual environments, build artifacts, git directory.
    exclude_dirs:
      - __pycache__
      - .git
      - venv
      - .venv
      - node_modules
      - build
      - dist
      # Add other directories to exclude

    # Specific files to exclude (by name or relative path).
    exclude_files:
      - .env
      # - secret_key.txt

    # == Other Options ==
    # Maximum size for a single file in bytes. Files larger than this will be skipped.
    # Default is 10MB (10 * 1024 * 1024 = 10485760 bytes).
    max_file_size: 10485760 # 10MB

    # Custom base name for the output file (e.g., 'backend_summary').
    # If not set, the name of the directory specified in 'path' is used.
    # output_name: my_project_summary
"""

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
        self.max_file_size: int = config.get('max_file_size', 10 * 1024 * 1024) # 10MB default
        self.output_name: Optional[str] = config.get('output_name', None)
        self.include_no_extension: Set[str] = set(config.get('include_no_extension', []))

    def __str__(self) -> str:
        """Return string representation of configuration."""
        return (
            f"DirectoryConfig(path='{self.path}', "
            f"extensions={self.extensions}, "
            f"files={self.files}, "
            f"include_no_extension={self.include_no_extension}, "
            f"dirs={self.dirs}, "
            f"exclude_dirs={self.exclude_dirs}, "
            f"exclude_files={self.exclude_files}, "
            f"max_file_size={self.max_file_size}, "
            f"output_name='{self.output_name}')"
        )

def create_default_config(config_path: Path) -> bool:
    """
    Creates a default configuration file at the specified path.

    Args:
        config_path: The Path object representing the desired config file location.

    Returns:
        True if the file was created successfully, False otherwise.
    """
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(DEFAULT_CONFIG_CONTENT.strip())  # Use strip() to remove leading/trailing whitespace
        logger.info(f"Successfully created default configuration file: {config_path}")
        return True
    except IOError as e:
        logger.error(f"Failed to create default configuration file at {config_path}: {e}")
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred while creating default config {config_path}: {e}")
        return False

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