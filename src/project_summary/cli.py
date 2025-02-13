#!/usr/bin/env python3
import argparse
import logging
import sys
from pathlib import Path

from .config import DirectoryConfig, load_config
from .core import create_project_summary

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate project summary based on YAML configuration"
    )
    parser.add_argument(
        "--config", "-c",
        default="project_summary_config.yaml",
        help="Path to YAML configuration file (default: project_summary_config.yaml)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.INFO if args.verbose else logging.WARNING
    logging.basicConfig(level=log_level, format='%(asctime)s - %(message)s')
    
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: Configuration file not found: {config_path}")
        sys.exit(1)
        
    try:
        config = load_config(config_path)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)
        
    output_dir = config.get("output_dir", "summaries")
    output_dir = Path(output_dir)
    
    for dir_config_dict in config.get("directories", []):
        try:
            dir_config = DirectoryConfig(dir_config_dict)
            create_project_summary(dir_config, output_dir)
        except Exception as e:
            print(f"Error processing directory {dir_config_dict.get('path', '.')}: {e}")

if __name__ == "__main__":
    main()