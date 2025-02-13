# Project Summary Generator

A Python tool for generating comprehensive project documentation by analyzing your project's structure and files. It creates detailed summaries of your project's files and directories, making it easier to understand and document large codebases.

## Features

- Tree-style visualization of project structure
- Flexible configuration using YAML
- Support for multiple directory configurations
- Intelligent file filtering by extensions
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

1. Create a configuration file `project_summary_config.yaml`:

```yaml
output_dir: summaries/

directories:
  - path: .
    extensions:
      - .py
      - .yml
    exclude_dirs:
      - __pycache__
      - .git
      - venv
    max_file_size: 5242880  # 5MB
```

2. Run the tool:

```bash
project-summary
```

## Configuration Options

### Basic Configuration

```yaml
output_dir: summaries/  # Directory where summaries will be saved

directories:  # List of directories to analyze
  - path: .  # Directory path (relative or absolute)
    extensions:  # File extensions to include
      - .py
      - .yml
    exclude_dirs:  # Directories to exclude
      - __pycache__
    exclude_files:  # Files to exclude
      - .env
    max_file_size: 5242880  # Maximum file size in bytes (5MB)
    output_name: my_summary  # Custom name for output file (optional)
```

### Advanced Configuration

You can specify multiple directory configurations:

```yaml
output_dir: docs/summaries/

directories:
  - path: src/
    extensions:
      - .py
    exclude_dirs:
      - __pycache__
    output_name: backend_summary

  - path: frontend/
    extensions:
      - .js
      - .ts
      - .vue
    exclude_dirs:
      - node_modules
    files:
      - package.json
    output_name: frontend_summary

  - path: docs/
    extensions:
      - .md
      - .rst
    output_name: documentation_summary
```

## Command Line Options

```bash
# Use default config (project_summary_config.yaml)
project-summary

# Specify custom config file
project-summary --config my_config.yaml

# Enable verbose output
project-summary -v
```

## Configuration Parameters

Each directory configuration supports the following parameters:

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| path | string | Directory path to analyze | "." |
| extensions | list | File extensions to include | [] |
| files | list | Specific files to include | [] |
| dirs | list | Specific directories to include | [] |
| exclude_dirs | list | Directories to exclude | [] |
| exclude_files | list | Files to exclude | [] |
| max_file_size | int | Maximum file size in bytes | 10MB |
| output_name | string | Custom name for output file | None |

## Output Format

The tool generates a text file containing:

1. Project structure in tree format
2. Full content of included files

Example output structure:
```
1. Project Structure:

├── src/
│   ├── main.py
│   └── utils.py
├── tests/
│   └── test_main.py
└── README.md

2. File Contents:

File 1: src/main.py
--------------------------------------------------
[file content here]

File 2: src/utils.py
--------------------------------------------------
[file content here]
...
```

## Using as a Python Package

You can also use Project Summary programmatically:

```python
from pathlib import Path
from project_summary.config import DirectoryConfig
from project_summary.core import create_project_summary

config = {
    'path': '.',
    'extensions': ['.py', '.md'],
    'exclude_dirs': ['__pycache__'],
    'max_file_size': 1048576  # 1MB
}

dir_config = DirectoryConfig(config)
create_project_summary(dir_config, Path('summaries'))
```

## Development

To set up for development:

```bash
# Clone the repository
git clone https://github.com/fedorello/project-summary.git
cd project-summary

# Install in development mode
pip install -e .
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

