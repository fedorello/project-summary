"""Core functionality for project summary generation."""

import os
import logging
import fnmatch
from pathlib import Path
from typing import List, Set

from .config import DirectoryConfig

logger = logging.getLogger(__name__)

def parse_gitignore(gitignore_path: Path) -> List[str]:
    """Parse .gitignore file and return list of patterns."""
    if not gitignore_path.exists():
        return []
    with open(gitignore_path, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

def should_ignore(path: Path, gitignore_patterns: List[str], root: Path) -> bool:
    """Check if path should be ignored based on gitignore patterns."""
    rel_path = os.path.relpath(path, root)
    for pattern in gitignore_patterns:
        if pattern.endswith('/'):
            if rel_path.startswith(pattern) or fnmatch.fnmatch(rel_path + '/', pattern):
                return True
        elif fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(path.name, pattern):
            return True
    return False

def should_include_file(file_path: Path, dir_config: DirectoryConfig, 
                       gitignore_patterns: List[str], root: Path) -> bool:
    """Determine if file should be included in summary."""
    if not file_path.exists():
        return False
        
    if should_ignore(file_path, gitignore_patterns, root):
        return False
        
    if file_path.stat().st_size > dir_config.max_file_size:
        logger.warning(f"Skipping {file_path}: file size exceeds limit")
        return False

    if file_path.name in dir_config.exclude_files:
        return False

    rel_path = os.path.relpath(file_path, root)
    
    if rel_path in dir_config.files:
        return True
        
    if dir_config.dirs:
        for dir_path in dir_config.dirs:
            if rel_path.startswith(dir_path):
                return file_path.suffix.lower() in dir_config.extensions
        return False
    
    return file_path.suffix.lower() in dir_config.extensions

def should_exclude_dir(dir_path: Path, dir_config: DirectoryConfig, 
                      gitignore_patterns: List[str], root: Path) -> bool:
    """Determine if directory should be excluded."""
    if should_ignore(dir_path, gitignore_patterns, root):
        return True
    return any(excluded in str(dir_path) for excluded in dir_config.exclude_dirs)

def get_file_tree(startpath: Path, dir_config: DirectoryConfig, 
                  gitignore_patterns: List[str]) -> List[str]:
    """Generate tree-like structure of included files."""
    tree = []
    
    if dir_config.dirs:
        processed_dirs: Set[str] = set()
        all_files = get_all_files(startpath, dir_config, gitignore_patterns)
        rel_files = sorted(os.path.relpath(f, startpath) for f in all_files)
        
        for file_path in rel_files:
            parts = Path(file_path).parts
            current_path = startpath
            
            for i, part in enumerate(parts[:-1]):
                current_path = current_path / part
                dir_level = i
                if str(current_path) not in processed_dirs:
                    indent = '│   ' * dir_level + '├── ' if dir_level > 0 else ''
                    tree.append(f"{indent}{part}/")
                    processed_dirs.add(str(current_path))
            
            file_level = len(parts) - 1
            indent = '│   ' * file_level + '├── '
            tree.append(f"{indent}{parts[-1]}")
            
    elif dir_config.files and not dir_config.extensions:
        sorted_files = sorted(dir_config.files)
        processed_dirs = set()
        
        for file_path in sorted_files:
            parts = Path(file_path).parts
            current_path = startpath
            
            for i, part in enumerate(parts[:-1]):
                current_path = current_path / part
                dir_level = i
                if str(current_path) not in processed_dirs:
                    indent = '│   ' * dir_level + '├── ' if dir_level > 0 else ''
                    tree.append(f"{indent}{part}/")
                    processed_dirs.add(str(current_path))
            
            file_level = len(parts) - 1
            indent = '│   ' * file_level + '├── '
            tree.append(f"{indent}{parts[-1]}")
    else:
        for root, dirs, files in os.walk(startpath):
            root_path = Path(root)
            dirs[:] = [d for d in dirs if not should_exclude_dir(
                root_path / d, dir_config, gitignore_patterns, startpath)]
                
            level = len(Path(root).relative_to(startpath).parts)
            indent = '│   ' * (level - 1) + '├── ' if level > 0 else ''
            tree.append(f"{indent}{root_path.name}/")
            
            subindent = '│   ' * level + '├── '
            for f in files:
                file_path = root_path / f
                if should_include_file(file_path, dir_config, gitignore_patterns, startpath):
                    tree.append(f"{subindent}{f}")
    
    return tree

def get_all_files(startpath: Path, dir_config: DirectoryConfig, 
                  gitignore_patterns: List[str]) -> List[Path]:
    """Get all files that should be included in summary."""
    all_files = []
    startpath = Path(startpath)
    
    if dir_config.dirs:
        for dir_path in dir_config.dirs:
            dir_full_path = startpath / dir_path
            if not dir_full_path.is_relative_to(startpath):
                continue
            if not dir_full_path.exists() or not dir_full_path.is_dir():
                logger.warning(f"Directory not found: {dir_path}")
                continue
                
            for root, dirs, files in os.walk(dir_full_path):
                root_path = Path(root)
                dirs[:] = [d for d in dirs if not should_exclude_dir(
                    root_path / d, dir_config, gitignore_patterns, startpath)]
                    
                for file in files:
                    file_path = root_path / file
                    if should_include_file(file_path, dir_config, gitignore_patterns, startpath):
                        all_files.append(file_path)
        return all_files
    
    if dir_config.files and not dir_config.extensions:
        for file_path in dir_config.files:
            full_path = startpath / file_path
            if full_path.exists() and not should_ignore(full_path, gitignore_patterns, startpath):
                all_files.append(full_path)
    else:
        for root, dirs, files in os.walk(startpath):
            root_path = Path(root)
            dirs[:] = [d for d in dirs if not should_exclude_dir(
                root_path / d, dir_config, gitignore_patterns, startpath)]
                
            for file in files:
                file_path = root_path / file
                if should_include_file(file_path, dir_config, gitignore_patterns, startpath):
                    all_files.append(file_path)
    
    return all_files

def create_project_summary(dir_config: DirectoryConfig, output_dir: Path) -> None:
    """Create project summary based on configuration."""
    logger.info(f"Starting project summary creation for {dir_config.path}...")
    
    current_dir = Path(dir_config.path).resolve()
    logger.info(f"Current directory: {current_dir}")

    gitignore_path = current_dir / '.gitignore'
    gitignore_patterns = parse_gitignore(gitignore_path)

    output_filename = f"{dir_config.output_name}.txt" if dir_config.output_name else f"{current_dir.name}_summary.txt"
    output_path = Path(output_dir) / output_filename
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        logger.info("Creating file structure...")
        f.write("1. Project Structure:\n\n")
        tree = get_file_tree(current_dir, dir_config, gitignore_patterns)
        for line in tree:
            f.write(line + '\n')
        f.write('\n\n')

        logger.info("Writing file contents...")
        f.write("2. File Contents:\n\n")
        all_files = get_all_files(current_dir, dir_config, gitignore_patterns)
        
        for i, file_path in enumerate(all_files, start=1):
            rel_path = file_path.relative_to(current_dir)
            f.write(f"File {i}: {rel_path}\n")
            f.write('-' * 50 + '\n')
            
            try:
                content = file_path.read_text(encoding='utf-8')
                f.write(content)
                logger.info(f"Processed file {i} of {len(all_files)}")
            except Exception as e:
                f.write(f"Error reading file: {str(e)}")
            f.write('\n\n' + '=' * 50 + '\n\n')

    logger.info(f"Project summary created in {output_path}")