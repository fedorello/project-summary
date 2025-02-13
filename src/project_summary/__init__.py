"""Project Summary - tool for generating project structure and content summaries."""

from .core import create_project_summary
from .config import DirectoryConfig, load_config

__version__ = "0.1.0"
__all__ = ['create_project_summary', 'DirectoryConfig', 'load_config']