# Project Summary Generator

A Python tool for generating comprehensive project documentation by analyzing your project's structure and files. It creates detailed summaries of your project's files and directories, making it easier to understand and document large codebases.

## Features

- Tree-style visualization of project structure
- Flexible configuration using YAML
- **Automatic default config creation:** Creates a well-commented `project_summary_config.yaml` if none is found.
- **Built-in help command:** Use `project-summary help` for quick usage guidance.
- Support for multiple directory configurations
- Intelligent file filtering by extensions
- Inclusion of specific extensionless files (e.g., `Dockerfile`, `LICENSE`)
- Combined filtering: Use specific files, extensions, and extensionless files together
- Directory and file exclusion patterns
- Gitignore support
- Custom output naming
- File size limits
- Full file content extraction

## Installation

```bash
pip install project-summary
```

## Quick Start

1.  **Navigate to your project directory** in the terminal.
2.  **Run the tool:**
    ```bash
    project-summary
    ```
3.  **First Run?** If `project_summary_config.yaml` doesn't exist in the current directory, the tool will create a default one for you and notify you.
4.  **Customize:** Open the generated `project_summary_config.yaml` and adjust the settings (extensions, excludes, etc.) to fit your project needs. See the **Configuration Options** section below for details.
5.  **Run again:**
    ```bash
    project-summary
    ```
    This time, it will use your customized configuration to generate the summary file (e.g., `summaries/your_project_name_summary.txt`).

**Example Default `project_summary_config.yaml` (created on first run):**
```yaml
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
```

## Configuration Options

The `project_summary_config.yaml` file controls how the summary is generated.

### Basic Structure

```yaml
# Directory where all summary files will be saved
output_dir: summaries/

# List of configurations, one for each part of the project you want to summarize
directories:
  # Configuration Block 1
  - path: . # Analyze the current directory
    # ... inclusion/exclusion rules ...
    output_name: my_project_summary # Optional: custom output filename

  # Configuration Block 2 (Optional)
  - path: src/ # Analyze a specific subdirectory
    # ... different rules if needed ...
    output_name: source_code_summary
```

### Advanced Example

Combine multiple blocks with different rules:

```yaml
output_dir: docs/summaries/

directories:
  # Analyze the main source code
  - path: src/
    output_name: backend_summary
    extensions:
      - .py
    exclude_dirs:
      - __pycache__

  # Analyze the frontend code
  - path: frontend/
    output_name: frontend_summary
    extensions:
      - .js
      - .ts
      - .vue
    files: # Explicitly include package config
      - package.json
      - vite.config.ts
    exclude_dirs:
      - node_modules

  # Analyze documentation files
  - path: docs/
    output_name: documentation_summary
    extensions:
      - .md
      - .rst

  # Analyze configuration and root-level files
  - path: . # Analyze from the root for specific files
    output_name: config_and_root_files
    # Only include specific files, regardless of extension
    files:
      - pyproject.toml
      - poetry.lock
      - .gitlab-ci.yml
    # Include common extensionless files found at the root
    include_no_extension:
      - Dockerfile
      - LICENSE
      - Makefile
      - .gitignore # Include .gitignore itself if needed
    # Important: Set max_file_size if necessary for potentially large files like lock files
    max_file_size: 2097152 # 2MB
    # No 'extensions' key means only files listed in 'files' or 'include_no_extension' will match
```

## Command Line Options

```bash
# Generate summary using 'project_summary_config.yaml' in the current directory
# Creates the config file if it doesn't exist.
project-summary

# Specify a custom path to the configuration file
project-summary --config path/to/your_config.yaml
project-summary -c path/to/your_config.yaml

# Enable verbose output (DEBUG level logs) for troubleshooting
project-summary -v
project-summary --verbose

# Show built-in help message explaining usage and configuration
project-summary help
```

## Inclusion Logic

A file is included in the summary if it meets **all** of the following conditions:
1.  It is not excluded by `exclude_files`.
2.  It is not located within a directory excluded by `exclude_dirs`.
3.  It is not ignored by `.gitignore` patterns (if `.gitignore` exists).
4.  Its size does not exceed `max_file_size`.
5.  If the `dirs` parameter is specified for the configuration block, the file must be within one of those directories.

AND it meets **at least one** of the following conditions:
*   Its relative path (from the configured `path`) is listed in the `files` list.
*   It has **no** file extension (like `Makefile`) AND its name is listed in the `include_no_extension` list.
*   Its file extension (like `.py`) is listed in the `extensions` list.

You can combine `files`, `extensions`, and `include_no_extension` in the same configuration block.

## Configuration Parameters

Each entry under the `directories` list in your YAML file supports the following parameters:

| Parameter             | Type   | Description                                                                                                                                  | Default           |
| :-------------------- | :----- | :------------------------------------------------------------------------------------------------------------------------------------------- | :---------------- |
| `path`                | string | Directory path to analyze (relative to where `project-summary` is run, or absolute)                                                        | `.`               |
| `extensions`          | list   | File extensions to include (e.g., `.py`, `.md`). Case-insensitive.                                                                             | `[]`              |
| `files`               | list   | Specific files to include, specified by their path relative to `path` (e.g., `src/config/settings.py`).                                        | `[]`              |
| `include_no_extension` | list   | Names of files **without extensions** to include (e.g., `Dockerfile`, `Makefile`). Case-sensitive matching of the filename.                    | `[]`              |
| `dirs`                | list   | Specific subdirectories (relative to `path`) to exclusively scan. If provided, only files within these directories (matching other criteria) will be included. | `[]`              |
| `exclude_dirs`        | list   | Directory names or relative paths (from `path`) to exclude. Also checks `.gitignore`.                                                        | `[]`              |
| `exclude_files`       | list   | File names or relative paths (from `path`) to exclude.                                                                                       | `[]`              |
| `max_file_size`       | int    | Maximum file size in bytes. Files larger than this are skipped.                                                                              | `10485760` (10MB) |
| `output_name`         | string | Custom base name for the output summary file (e.g., `backend_summary` results in `backend_summary.txt`). If None, uses the directory name.     | `None`            |

## Output Format

The tool generates a text file containing:

1.  Project structure in tree format (showing included files and directories)
2.  Full content of included files, separated by headers

Example output structure:
```
1. Project Structure:

my_project/
├── src/
│   ├── main.py
│   └── utils.py
├── tests/
│   └── test_main.py
├── Dockerfile
└── README.md

2. File Contents:

File 1: Dockerfile
--------------------------------------------------
FROM python:3.10-slim
...

==================================================

File 2: README.md
--------------------------------------------------
# My Project
...

==================================================

File 3: src/main.py
--------------------------------------------------
print("Hello World")

==================================================

File 4: src/utils.py
--------------------------------------------------
def helper():
    pass

==================================================

File 5: tests/test_main.py
--------------------------------------------------
assert True

==================================================
```

## Using as a Python Package

You can also use Project Summary programmatically:

```python
from pathlib import Path
from project_summary.config import DirectoryConfig, load_config # load_config might be needed if reading external config
from project_summary.core import create_project_summary

# Example configuration dictionary
config_dict = {
    'path': '../my_other_project', # Can be relative or absolute
    'extensions': ['.py', '.md'],
    'files': ['config/production.yaml'],
    'include_no_extension': ['Procfile', 'Makefile'],
    'exclude_dirs': ['__pycache__', '.venv', 'build/'],
    'exclude_files': ['.env.local'],
    'max_file_size': 1048576,  # 1MB
    'output_name': 'my_other_project_summary'
}

# Create DirectoryConfig object directly
dir_config = DirectoryConfig(config_dict)

# Define output directory
output_path = Path('generated_summaries')

# Create the summary
# Note: output_dir needs to be created if it doesn't exist when using programmatically
output_path.mkdir(parents=True, exist_ok=True)
create_project_summary(dir_config, output_path)

print(f"Summary created in {output_path}")

# Alternatively, load from a YAML file first (if needed)
# config_path = Path('path/to/your_config.yaml')
# try:
#     full_config = load_config(config_path)
#     output_dir = Path(full_config.get("output_dir", "summaries"))
#     output_dir.mkdir(parents=True, exist_ok=True)
#     for dir_conf_dict in full_config.get("directories", []):
#         dir_config = DirectoryConfig(dir_conf_dict)
#         create_project_summary(dir_config, output_dir)
# except Exception as e:
#     print(f"Error using project summary programmatically: {e}")

```

## Development

To set up for development:

```bash
# Clone the repository
git clone https://github.com/fedorello/project-summary.git
cd project-summary

# Create and activate a virtual environment (HIGHLY RECOMMENDED)
python3 -m venv .venv # or python -m venv .venv
source .venv/bin/activate # or .\.venv\Scripts\activate on Windows

# Install in development mode (includes dependencies)
pip install -e .

# Run the development version (use one of these methods):
# Method 1 (Recommended): Execute as a module
python -m project_summary.cli [OPTIONS]

# Method 2: Execute the script directly from .venv
./.venv/bin/project-summary [OPTIONS]

# Example: Run with verbose logging using method 1
python -m project_summary.cli -v

# Run tests (if tests are set up, e.g., with pytest)
# pip install pytest # If not already installed
# pytest
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request or open an Issue on GitHub.
