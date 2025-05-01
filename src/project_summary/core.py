# src/project_summary/core.py
"""Core functionality for project summary generation."""
import os
import logging
import fnmatch
from pathlib import Path
from typing import List, Set

from .config import DirectoryConfig

# Standard logger setup
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
    """
    Determine if file should be included in summary based on combined criteria.
    Includes detailed debug logging.

    Args:
        file_path: Absolute path to the file.
        dir_config: Configuration for the directory being processed.
        gitignore_patterns: List of patterns from .gitignore.
        root: The absolute root path of the scan defined in dir_config.

    Returns:
        True if the file should be included, False otherwise.
    """
    # Log entry point only if debug is enabled to avoid spamming
    if logger.isEnabledFor(logging.DEBUG):
        try:
            rel_path_debug = file_path.relative_to(root)
            logger.debug(f"Checking file: '{rel_path_debug}' (Abs: {file_path})")
        except ValueError:
             logger.debug(f"Checking file outside root?: {file_path}")
             rel_path_debug = file_path # Fallback for logging

    # Check 1: Is it a file?
    if not file_path.is_file():
        # Add Debug Logging
        logger.debug(f"Excluding '{rel_path_debug}': Not a file.")
        return False
        
    # Check 2: Is it ignored by gitignore?
    if should_ignore(file_path, gitignore_patterns, root):
        # Add Debug Logging
        logger.debug(f"Excluding '{rel_path_debug}': Matched gitignore pattern.")
        return False
        
    # Check 3: Is it too large?
    try:
        file_size = file_path.stat().st_size
        if file_size > dir_config.max_file_size:
            # Warning is logged by default, add debug log for consistency
            logger.debug(f"Excluding '{rel_path_debug}': Size ({file_size}) > max_size ({dir_config.max_file_size}).")
            logger.warning(f"Skipping {file_path}: file size exceeds limit")
            return False
    except OSError as e:
        # Add Error Logging
        logger.error(f"Could not get stat for file '{file_path}': {e}. Skipping.")
        return False

    # Check 4: Is its NAME explicitly excluded?
    if file_path.name in dir_config.exclude_files:
        # Add Debug Logging
        logger.debug(f"Excluding '{rel_path_debug}': Name ('{file_path.name}') is in exclude_files.")
        return False

    # Calculate relative path (relative to the start path defined in config)
    try:
        rel_path_str = str(file_path.relative_to(root))
    except ValueError:
        # This case should ideally not happen if called from get_all_files with os.walk results
        logger.warning(f"File {file_path} seems outside the root {root}. Skipping.")
        # Add Debug Logging
        logger.debug(f"Excluding '{file_path}': Cannot determine relative path to root '{root}'.")
        return False

    # Check 5: Is its RELATIVE PATH explicitly excluded?
    if rel_path_str in dir_config.exclude_files:
        # Add Debug Logging
        logger.debug(f"Excluding '{rel_path_str}': Relative path is in exclude_files.")
        return False
    
    # --- Start of Inclusion Logic ---
    include = False
    inclusion_reason = "No inclusion criteria met" # Default reason

    # 1. Check if file is explicitly listed in 'files'
    if rel_path_str in dir_config.files:
        include = True
        inclusion_reason = f"Matched 'files' config: '{rel_path_str}'"
        # Add Debug Logging
        logger.debug(f"Found potential match for '{rel_path_str}': In 'files' list.")

    # 2. Check if file has no extension and is listed in 'include_no_extension'
    if not include and file_path.suffix == '' and file_path.name in dir_config.include_no_extension:
        include = True
        inclusion_reason = f"Matched 'include_no_extension': '{file_path.name}'"
        # Add Debug Logging
        logger.debug(f"Found potential match for '{rel_path_str}': No extension and name '{file_path.name}' in 'include_no_extension'.")

    # 3. Check if file extension is in 'extensions'
    file_suffix_lower = file_path.suffix.lower()
    if not include and file_suffix_lower in dir_config.extensions:
        include = True
        inclusion_reason = f"Matched 'extensions': '{file_suffix_lower}'"
        # Add Debug Logging
        logger.debug(f"Found potential match for '{rel_path_str}': Extension '{file_suffix_lower}' in 'extensions'.")

    # If the file wasn't included by any criteria above, it shouldn't be included.
    if not include:
        # Add Debug Logging
        logger.debug(f"Excluding '{rel_path_str}': Did not match any inclusion criteria (files, include_no_extension, extensions).")
        return False
    else:
        # Log the reason only if it passed the inclusion criteria stage
        logger.debug(f"Passed inclusion criteria for '{rel_path_str}': {inclusion_reason}")
    
    # If 'dirs' config is used, the file MUST reside within one of the specified directories.
    if dir_config.dirs:
        # Add Debug Logging
        logger.debug(f"Applying 'dirs' constraint for '{rel_path_str}': Allowed dirs = {dir_config.dirs}")
        is_in_specified_dir = False
        normalized_rel_path = Path(rel_path_str).as_posix() # Use Posix paths for reliable matching
        
        for allowed_dir in dir_config.dirs:
            normalized_allowed_dir = Path(allowed_dir).as_posix()
            
            if normalized_rel_path == normalized_allowed_dir or normalized_rel_path.startswith(normalized_allowed_dir + '/'):
                is_in_specified_dir = True
                # Add Debug Logging
                logger.debug(f"'{rel_path_str}' is WITHIN specified dir '{allowed_dir}'.")
                break  # Found a match, no need to check further

        if not is_in_specified_dir:
            # Add Debug Logging
            logger.debug(f"Excluding '{rel_path_str}': Matched inclusion criteria BUT not within any specified 'dirs' {dir_config.dirs}.")
            return False  # File matched criteria but is not in the allowed directories
        else:
            logger.debug(f"Passed 'dirs' constraint for '{rel_path_str}'.")

    # If we passed all checks, return True
    # Add Debug Logging
    logger.debug(f"Including '{rel_path_str}': Passed all checks.")
    return True

def should_exclude_dir(dir_path: Path, dir_config: DirectoryConfig, 
                      gitignore_patterns: List[str], root: Path) -> bool:
    """Determine if directory should be excluded."""
    if should_ignore(dir_path, gitignore_patterns, root):
        return True
    return any(excluded in str(dir_path) for excluded in dir_config.exclude_dirs)

def get_all_files(startpath: Path, dir_config: DirectoryConfig, 
                  gitignore_patterns: List[str]) -> List[Path]:
    """
    Get all files that should be included in summary using the unified inclusion logic.

    Args:
        startpath: The absolute root path to start scanning from.
        dir_config: The configuration for this directory scan.
        gitignore_patterns: Parsed gitignore patterns.

    Returns:
        A list of absolute Paths for all included files, sorted alphabetically by relative path.
    """
    included_files: List[Path] = []
    logger.debug(f"Scanning directory: {startpath} with config: {dir_config}")

    for root, dirs, files in os.walk(startpath, topdown=True):
        root_path = Path(root)

        # Filter directories based on exclude_dirs and gitignore before descending further
        original_dirs_count = len(dirs)
        dirs[:] = [d for d in dirs if not should_exclude_dir(
            root_path / d, dir_config, gitignore_patterns, startpath
        )]
        
        # Check each file in the current directory
        for filename in files:
            file_path = root_path / filename
            if should_include_file(file_path, dir_config, gitignore_patterns, startpath):
                included_files.append(file_path)

    # Sort files based on their relative path for consistent output
    included_files.sort(key=lambda p: p.relative_to(startpath))
    logger.info(f"Found {len(included_files)} files to include in {startpath}")
    return included_files

def get_file_tree(included_files: List[Path], root_path: Path) -> List[str]:
    """
    Generate tree-like structure string from a list of included file paths.

    Args:
        included_files: A list of absolute Paths for files already determined to be included.
        root_path: The absolute root path relative to which the tree should be built.

    Returns:
        A list of strings representing the file tree.
    """
    if not included_files:
        return ["(No files included based on configuration)"]

    tree_lines: List[str] = []
    processed_dirs: Set[Path] = set()  # Keep track of directories already added to the tree

    # Add the root directory name
    tree_lines.append(f"{root_path.name}/")

    # Sort files by their full path to ensure correct tree structure
    sorted_files = sorted(included_files)

    for file_path in sorted_files:
        # Get path relative to the root for tree display
        try:
            relative_path = file_path.relative_to(root_path)
        except ValueError:
            logger.warning(f"File {file_path} is outside root {root_path}, cannot place in tree.")
            continue  # Skip files outside the root

        parts = relative_path.parts
        current_path = root_path  # Start from absolute root

        # Iterate through parent directories of the file
        for i, part in enumerate(parts[:-1]):  # Exclude the filename itself
            current_path = current_path / part
            # If this directory hasn't been added to the tree yet, add it
            if current_path not in processed_dirs:
                # Indentation level based on depth (number of parts processed so far)
                indent = '│   ' * i + '├── '
                tree_lines.append(f"{indent}{part}/")
                processed_dirs.add(current_path)

        # Add the file itself to the tree
        file_level = len(parts) - 1
        indent = '│   ' * file_level + '├── '
        tree_lines.append(f"{indent}{parts[-1]}")  # Add filename

    # Basic cleanup for nicer tree endings
    if len(tree_lines) > 1:
        # Simply fix the last line connector if it's '├── '
        if tree_lines[-1].startswith('│   ' * file_level + '├── '):
            tree_lines[-1] = tree_lines[-1].replace('├── ', '└── ', 1)
        elif tree_lines[-1].startswith('├── '):  # Root level file
            tree_lines[-1] = tree_lines[-1].replace('├── ', '└── ', 1)

    return tree_lines

def create_project_summary(dir_config: DirectoryConfig, output_dir: Path) -> None:
    """Create project summary based on configuration."""
    logger.info(f"Starting project summary creation for {dir_config.path}...")
    
    current_dir = Path(dir_config.path).resolve()
    logger.info(f"Current directory: {current_dir}")

    if not current_dir.is_dir():
        logger.error(f"Directory specified in configuration not found or is not a directory: {current_dir}")
        return

    gitignore_path = current_dir / '.gitignore'
    gitignore_patterns = parse_gitignore(gitignore_path)
    logger.debug(f"Loaded {len(gitignore_patterns)} patterns from {gitignore_path}")

    output_filename = f"{dir_config.output_name}.txt" if dir_config.output_name else f"{current_dir.name}_summary.txt"
    output_filename = "".join(c for c in output_filename if c.isalnum() or c in ('_', '-', '.'))
    output_path = Path(output_dir) / output_filename
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Get all files first using the refactored function
    logger.info("Scanning for files to include...")
    all_included_files = get_all_files(current_dir, dir_config, gitignore_patterns)

    with open(output_path, 'w', encoding='utf-8') as f:
        logger.info("Creating file structure...")
        f.write("1. Project Structure:\n\n")
        tree = get_file_tree(all_included_files, current_dir)
        for line in tree:
            f.write(line + '\n')
        f.write('\n\n')

        logger.info("Writing file contents...")
        f.write("2. File Contents:\n\n")
        
        total_files = len(all_included_files)
        for i, file_path in enumerate(all_included_files, start=1):
            try:
                rel_path = file_path.relative_to(current_dir)
                logger.info(f"Processing file {i}/{total_files}: {rel_path}")
                f.write(f"File {i}: {rel_path}\n")
                f.write('-' * 50 + '\n')
                
                try:
                    content = file_path.read_text(encoding='utf-8')
                    f.write(content)
                except UnicodeDecodeError:
                    logger.warning(f"Could not decode file {rel_path} as UTF-8. Trying latin-1.")
                    try:
                        content = file_path.read_text(encoding='latin-1')
                        f.write(content)
                        f.write("\n[Warning: Read using latin-1 encoding]\n")
                    except Exception as decode_err:
                        logger.error(f"Error reading file {rel_path} even with latin-1: {decode_err}")
                        f.write(f"[Error reading file: Could not decode content - {str(decode_err)}]")
                except Exception as e:
                    logger.error(f"Error reading file {rel_path}: {e}")
                    f.write(f"[Error reading file: {str(e)}]")
                
                f.write('\n\n' + '=' * 50 + '\n\n')
            except ValueError:
                logger.error(f"Internal error: File path {file_path} could not be made relative to root {current_dir}. Skipping file content.")
                f.write(f"File {i}: {file_path} (Error: Could not determine relative path)\n")
                f.write('-' * 50 + '\n')
                f.write("[Error: Could not process this file's path relative to the root.]")
                f.write('\n\n' + '=' * 50 + '\n\n')

    logger.info(f"Project summary created in {output_path}")