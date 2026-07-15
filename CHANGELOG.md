# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-07-08

### Added

- Add new operations, based on Sekoia API 3.1 documentation and automation-library playbook action JSON files:
    - `edit_case` operation
    - `get_case` operation
    - `list_assets` operation
    - `revoke_assetv2` operation
    - `search_cases` operation
    - `update_assets` operation
- Add runtime, development, and lint dependency groups in `pyproject.toml` for reproducible local and CI environments
- Add GitHub Actions:
    - `lint` stage to run `black`, `isort`, `mypy` and `ruff`
    - `normalize_info_json` stage to run read-only checks dedicated to `info.json`
    - `normalize_operations` stage to run read-only checks dedicated to operation source normalization
    - `tests` stage to run the unit test suite across multiple supported Python versions

### Changed

- Deprecate existing operations, based on Sekoia API 3.1 documentation and automation-library playbook action JSON files:
    - `update_asset` operation in favor of `update_assets` operation
- Update existing operations, based on Sekoia API 3.1 documentation and automation-library playbook action JSON files:
    - `get_alert` operation:
        - add `include_cases` parameter
        - add `include_custom_status` parameter
    - `get_asset` operation:
        - add `uuid` parameter
        - add `with_compliance` parameter
        - add `with_telemetry` parameter
        - deprecate `asset_uuid` parameter
    - `get_events` operation:
        - add `limit` parameter
    - `list_alerts` operation:
        - add `date[created_at]` parameter
        - add `date[updated_at]` parameter
        - add `match[rule_uuid]` parameter
        - add `match[status_uuid]` parameter
        - deprecate `creation_end_date` parameter
        - deprecate `creation_start_date` parameter
        - deprecate `rule_uuid` parameter
        - deprecate `status_uuid` parameter
        - deprecate `updated_end_date` parameter
        - deprecate `updated_start_date` parameter
    - `update_alert_status` operation:
        - add `uuid` parameter
        - deprecate `alert_uuid` parameter
- Refactor source code and tests into operation-specific files organized under feature subdirectories:
    - `alerts`
    - `assets`
    - `cases`
    - `countermeasures`
    - `events`
- Modernize dependency management with uv (`pyproject.toml` + `uv.lock`)
- Move test execution to `uv run pytest` and align CI to run tests across supported Python versions
- Refactor operation Python modules to a unified class-based architecture using Pydantic v2 input models
