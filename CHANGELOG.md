# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.0] - 2026-07-19

### Added

- Add new operations, based on Sekoia API 3.1 documentation and automation-library playbook action JSON files:
  - `add_to_ioc_collection` operation
  - `comment_case` operation
  - `create_content_proposal` operation
  - `create_content_proposal_from_pdf` operation
  - `create_content_proposal_from_url` operation
  - `edit_alert` operation
  - `edit_case` operation
  - `get_case` operation
  - `get_custom_priority` operation
  - `get_custom_status` operation
  - `get_custom_verdict` operation
  - `list_assets` operation
  - `list_case_comments` operation
  - `revoke_assetv2` operation
  - `search_cases` operation
  - `update_assets` operation
  - `upload_observables` operation
- Add runtime, development, and lint dependency groups in `pyproject.toml` for reproducible local and CI environments
- Add GitHub Actions:
  - `lint` stage to run `black`, `isort`, `mypy`, and `ruff` checks in parallel
  - `normalize_metadata` stage to run read-only checks dedicated to `info.json` metadata normalization
  - `prepare_package` stage to run package quality gates (including requirements synchronization checks), build a `.tgz` connector archive, and publish it as a workflow artifact
  - `normalize_operations` stage to run read-only checks dedicated to operation source normalization
  - `tests` stage to run the unit test suite across multiple supported Python versions (`3.9` to `3.14`)

### Changed

- Deprecate existing operations, based on Sekoia API 3.1 documentation and automation-library playbook action JSON files:
  - `delete_asset` operation in favor of `revoke_assetv2`
  - `update_asset` operation in favor of `update_assets`
- Update existing operations, based on Sekoia API 3.1 documentation and automation-library playbook action JSON files:
  - `activate_countermeasure` operation:
    - add `cm_uuid` parameter
    - add `comment` parameter
    - deprecate `author` parameter in favor of `comment`
    - deprecate `content` parameter in favor of `comment`
    - deprecate `countermeasure_uuid` parameter in favor of `cm_uuid`
  - `add_comment_to_alert` operation:
    - add `content` parameter
    - add `uuid` parameter
    - deprecate `alert_uuid` parameter in favor of `uuid`
    - deprecate `comment` parameter in favor of `content`
  - `deny_countermeasure` operation:
    - add `cm_uuid` parameter
    - add `comment` parameter
    - deprecate `author` parameter in favor of `comment`
    - deprecate `content` parameter in favor of `comment`
    - deprecate `countermeasure_uuid` parameter in favor of `cm_uuid`
  - `get_alert` operation:
    - add `include_cases` parameter
    - add `include_custom_status` parameter
  - `get_asset` operation:
    - add `uuid` parameter
    - add `with_compliance` parameter
    - add `with_telemetry` parameter
    - deprecate `asset_uuid` parameter in favor of `uuid`
  - `get_events` operation:
    - add `limit` parameter
  - `list_alerts` operation:
    - add `date[created_at]` parameter
    - add `date[updated_at]` parameter
    - add `match[rule_uuid]` parameter
    - add `match[status_uuid]` parameter
    - deprecate `creation_end_date` parameter in favor of `date[created_at]`
    - deprecate `creation_start_date` parameter in favor of `date[created_at]`
    - deprecate `rule_uuid` parameter in favor of `match[rule_uuid]`
    - deprecate `status_uuid` parameter in favor of `match[status_uuid]`
    - deprecate `updated_end_date` parameter in favor of `date[updated_at]`
    - deprecate `updated_start_date` parameter in favor of `date[updated_at]`
  - `update_alert_status` operation:
    - add `uuid` parameter
    - deprecate `alert_uuid` parameter in favor of `uuid`
- Refactor source code and tests into operation-specific files organized under feature subdirectories:
  - `alerts`
  - `assets`
  - `cases`
  - `countermeasures`
  - `events`
- Align connector packaging layout with FortiSOAR requirements by using a top-level `sekoia-io-xdr` directory (matching `info.json` name) while keeping Python modules importable under `sekoia_io_xdr`
- Modernize dependency management with uv (`pyproject.toml` + `uv.lock`)
- Move test execution to `uv run pytest` and align CI to run tests across supported Python versions
- Refactor operation Python modules to a unified class-based architecture using Pydantic v2 input models

## [1.1.0] - 2023-07-27

### Added

- Add `Updated Start Date`, `Updated End Date`, `Records Offset` and `Records Per Page` in `List Alerts` operation
- Add the ability to configure data ingestion (using the `Data Ingestion Wizard`)
- The `Data Ingestion Wizard` also supports multiple configurations specified on the `Configurations` tab of the SEKOIA.IO XDR connector, ensuring respective global variables based on the selected configuration are used while ingesting data
