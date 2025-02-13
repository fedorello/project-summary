"""Tests for configuration handling."""

import pytest
from pathlib import Path
from project_summary.config import DirectoryConfig, load_config

def test_directory_config_defaults():
    """Test DirectoryConfig default values."""
    config = DirectoryConfig({})
    assert config.path == '.'
    assert config.extensions == set()
    assert config.files == set()
    assert config.dirs == set()
    assert config.exclude_dirs == set()
    assert config.exclude_files == set()
    assert config.max_file_size == 10 * 1024 * 1024
    assert config.output_name is None

def test_directory_config_extensions():
    """Test extension normalization."""
    config = DirectoryConfig({
        'extensions': ['py', '.py', 'YML', '.YAML']
    })
    assert config.extensions == {'.py', '.yml', '.yaml'}