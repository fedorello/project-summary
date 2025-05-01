# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-05-01

### Added
- **Inclusion of Extensionless Files:** Added configuration option `include_no_extension` to explicitly include specific files that lack file extensions (e.g., `Dockerfile`, `LICENSE`, `Makefile`).
- **Default Configuration File:** The tool now automatically creates a default `project_summary_config.yaml` file with detailed comments and examples if none is found at the expected location (`./project_summary_config.yaml` or path specified by `--config`).
- **`help` Command:** Added a simple `help` command (`project-summary help`) to display usage instructions, configuration overview, and links to documentation directly from the command line.

### Changed
- **Combined Inclusion Logic:** Inclusion rules (`files`, `extensions`, `include_no_extension`) are now evaluated additively. Specifying `files` no longer prevents `extensions` or `include_no_extension` from working in the same configuration block.
- **Verbose Flag Level:** The `-v`/`--verbose` command-line flag now correctly sets the logging level to `DEBUG` (previously it might have resulted in `INFO` or `WARNING` depending on prior state), providing detailed logs essential for troubleshooting.
- **Default Log Level:** The default logging level (when `-v` is *not* used) is now `INFO` (previously `WARNING`), providing users with more feedback on the process (e.g., which directory config is being processed, when file scanning starts/ends).
- **Error Handling:** Improved error reporting for configuration file loading issues (e.g., invalid YAML, incorrect types) and inaccessible output directories.

## [0.1.0] - 2024-02-13

### Added
- Initial release
- Basic project structure analysis
- YAML configuration support
- File content extraction
- Directory filtering
- Size limits
- Gitignore support