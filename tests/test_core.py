"""Tests for core functionality."""

import pytest
from pathlib import Path
from project_summary.core import should_include_file, should_exclude_dir
from project_summary.config import DirectoryConfig

@pytest.fixture
def basic_config():
    """Basic configuration for tests."""
    return DirectoryConfig({
        'extensions': ['.py', '.yml'],
        'exclude_dirs': ['__pycache__', '.git'],
        'exclude_files': ['secret.txt']
    })

def test_should_include_file(basic_config, tmp_path):
    """Test file inclusion logic."""
    python_file = tmp_path / "test.py"
    python_file.touch()
    
    text_file = tmp_path / "test.txt"
    text_file.touch()
    
    assert should_include_file(python_file, basic_config, [], tmp_path)
    assert not should_include_file(text_file, basic_config, [], tmp_path)