# src/project_summary/cli.py
"""Command-line interface for project summary generation."""
import argparse
import logging
import sys
from pathlib import Path
from .config import DirectoryConfig, load_config, create_default_config
from .core import create_project_summary

# Help text for detailed command help
HELP_TEXT = """
Project Summary Tool - Help

Purpose:
  Generates a text summary of a project, including a file tree and
  the content of specified files. Useful for understanding codebases
  or providing context for LLMs.

Usage:
  1. Configure: Create or edit a `project_summary_config.yaml` file
     in the directory you want to analyze (or specify a different path
     using --config).
     If the config file doesn't exist, a default one will be created
     on the first run. Please review and customize it!

  2. Run: Execute `project-summary` (or `python -m project_summary.cli`)
     from your terminal within your project's virtual environment.

Configuration (`project_summary_config.yaml`):
  - `output_dir`: Where to save the summary files (default: 'summaries/').
  - `directories`: A list of sections, each defining a path to analyze
    and rules for including/excluding files:
      - `path`: Directory to scan (e.g., '.', 'src/').
      - `extensions`: List of file extensions to include (e.g., ['.py', '.js']).
      - `files`: List of specific files to include (relative to `path`).
      - `include_no_extension`: List of extensionless files to include (e.g., ['Dockerfile']).
      - `exclude_dirs`: List of directories to ignore.
      - `exclude_files`: List of files to ignore.
      - `max_file_size`: Limit for individual file size (default: 10MB).
      - `output_name`: Custom name for the summary file.

Command Line Options:
  --config <path>, -c <path>: Specify a path to the configuration file
                                (default: 'project_summary_config.yaml').
  --verbose, -v             : Enable verbose output (DEBUG logs) for troubleshooting.
  help                      : Show this help message.

Full Documentation:
  Please refer to the README file or the PyPI page for detailed examples
  and advanced usage: https://pypi.org/project/project-summary/
"""

def main():
    """Main CLI entry point."""
    # Check for 'help' command before argparse processing
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'help':
        print(HELP_TEXT)
        sys.exit(0)  # Exit successfully after showing help

    parser = argparse.ArgumentParser(
        description="Generate project summary based on YAML configuration. Use 'project-summary help' for detailed usage.",
        add_help=False  # Disable default help to avoid conflict with our 'help' command check
    )
    # Re-add help argument manually, but less prominently
    parser.add_argument(
        '-h', '--help', action='help', default=argparse.SUPPRESS,
        help='Show this help message and exit (standard argparse help).'
    )
    parser.add_argument(
        "--config", "-c",
        default="project_summary_config.yaml",
        help="Path to YAML configuration file (default: %(default)s)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose (DEBUG level) output"
    )

    args = parser.parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO  # Default non-verbose to INFO
    log_format = '%(levelname)s - %(message)s'
    logging.basicConfig(level=log_level, format=log_format, stream=sys.stdout)
    logger = logging.getLogger('project_summary')
    logger.setLevel(log_level)

    # Get the config logger for debugging
    config_logger = logging.getLogger('project_summary.config')
    logging.debug(f"Logging level set to: {logging.getLevelName(log_level)}")

    config_path = Path(args.config)
    
    # Handle missing configuration file - create default instead of exiting
    if not config_path.exists():
        logging.warning(f"Configuration file not found at '{config_path}'.")
        logging.warning(f"Creating a default configuration file now...")
        if create_default_config(config_path):
            logging.warning(f"Default configuration file created at '{config_path}'.")
            logging.warning("Please review and customize it for your project, then run the command again.")
            logging.info("Continuing scan using the newly created default configuration.")
        else:
            # If creation failed, exit with error
            logging.error(f"Could not create default configuration file. Please check permissions or path.")
            sys.exit(1)

    try:
        logging.debug(f"Loading configuration from: {config_path}")
        config = load_config(config_path)
    except Exception as e:
        logging.error(f"Error loading configuration from {config_path}: {e}", exc_info=True)
        sys.exit(1)

    output_dir = config.get("output_dir", "summaries")
    output_dir = Path(output_dir)
    
    # Create output directory if it doesn't exist
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        logging.debug(f"Output directory set to: {output_dir.resolve()}")
    except Exception as e:
        logging.error(f"Invalid or inaccessible output directory specified: '{output_dir}'. Error: {e}", 
                     exc_info=log_level == logging.DEBUG)
        sys.exit(1)

    directories_to_process = config.get("directories", [])
    if not directories_to_process:
        logging.warning(f"No 'directories' specified in the configuration file '{config_path}'. Nothing to process.")
        logging.warning("Please add at least one directory entry to the 'directories:' list in the YAML file to specify what to scan.")
        sys.exit(0)

    logging.debug(f"Found {len(directories_to_process)} directory configurations to process.")

    has_errors = False
    for i, dir_config_dict in enumerate(directories_to_process):
        path_for_log = dir_config_dict.get('path', '.') if isinstance(dir_config_dict, dict) else '(Invalid Entry)'
        logging.info(f"--- Processing directory config #{i+1} ('{path_for_log}') ---")
        try:
            # Add validation: Ensure dir_config_dict is actually a dictionary
            if not isinstance(dir_config_dict, dict):
                logging.error(f"Skipping configuration entry #{i+1}: Expected a dictionary (YAML mapping), but got type {type(dir_config_dict)}. Check YAML indentation/format.")
                has_errors = True
                continue  # Skip to the next directory configuration
                
            dir_config = DirectoryConfig(dir_config_dict)
            # Use the config logger to log this
            config_logger.debug(f"Parsed DirectoryConfig: {dir_config}")
            create_project_summary(dir_config, output_dir)
        except Exception as e:
            logging.error(f"Error processing directory configuration for '{path_for_log}': {e}", 
                         exc_info=log_level == logging.DEBUG)
            has_errors = True  # Mark that an error occurred
            # Continue processing other directories

    if has_errors:
        logging.warning("Completed processing, but one or more directory configurations resulted in errors.")
    else:
        logging.info("--- Project summary generation finished successfully. ---")

if __name__ == "__main__":
    main()