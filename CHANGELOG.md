# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.0] - 2026-07-08

### Added

- Add operation parameters, based on Sekoia API 3.1 documentation and automation-library playbook action JSON files:
    - `get_alert` operation:
        - add `include_cases` parameter
        - add `include_custom_status` parameter

### Changed

- Modernize dependency management with uv (`pyproject.toml` + `uv.lock`)
- Add runtime and development dependency groups for reproducible local and CI environments
- Move test execution to `uv run pytest` and aligned CI to run tests across supported Python versions
- Standardize Python support window for this connector package to match the FortiSOAR SDK compatibility baseline used by this repository
- Align `get_alert` operation parameters with Sekoia API 3.1 by adding support for related cases and custom status details
