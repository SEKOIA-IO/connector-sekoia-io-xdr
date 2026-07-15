# connector-sekoia-io-xdr

[![Lint](https://github.com/fortinet-fortisoar/connector-sekoia-io-xdr/actions/workflows/lint.yml/badge.svg)](https://github.com/fortinet-fortisoar/connector-sekoia-io-xdr/actions/workflows/lint.yml)
[![Tests](https://github.com/fortinet-fortisoar/connector-sekoia-io-xdr/actions/workflows/tests.yml/badge.svg)](https://github.com/fortinet-fortisoar/connector-sekoia-io-xdr/actions/workflows/tests.yml)
[![Normalize Info JSON](https://github.com/fortinet-fortisoar/connector-sekoia-io-xdr/actions/workflows/normalize_info_json.yml/badge.svg)](https://github.com/fortinet-fortisoar/connector-sekoia-io-xdr/actions/workflows/normalize_info_json.yml)
[![Normalize Operations](https://github.com/fortinet-fortisoar/connector-sekoia-io-xdr/actions/workflows/normalize_operations.yml/badge.svg)](https://github.com/fortinet-fortisoar/connector-sekoia-io-xdr/actions/workflows/normalize_operations.yml)

This connector enable you to make full use of the SEKOIA.IO XDR platform.

It includes the following actions:

- Retrieve a list of alerts that could be filtered by `creation date`, `status name`, `status uuid`, `short id of the alerts`, and/or the `rule name`.
- Retrieve events from sekoia.io, the required parameters are: `query` to filter the events, `earliest_time` and `latest_time` that forms a date range to filter the search.
- Add a comment to an alert.
- Update the status of an alert.
- Retrieve a specific alert.
- Activate a countermeasure.
- Deny a countermeasure.
- Get a specific asset.
- Update an asset.
- Delete an asset. 


Further information about the installation of the `fortisoar_sdk` and more were provided by Fortinet through the following link:

https://fndn.fortinet.net/index.php?/tools/file/101-fortisoar%E2%84%A2-connector-sdk/

More details could be found in the fortisoar_sdk `README.md` file

## Local development with uv

This repository now supports `uv` for local dependency management.

### Python compatibility

The local development environment is configured for Python `>=3.9,<3.15`.

### Quick start

```bash
uv sync
```

This creates or updates the local virtual environment and installs dependencies from `pyproject.toml`.

### Add or update dependencies

```bash
uv add <package>
uv lock
```

### Run tests

```bash
uv run pytest tests/ --color=yes -vv
```

### Run linters (uv)

Install dev and lint tools first:

```bash
uv sync --group dev --group lint
```

Run formatting/fix commands locally on connector and tests:

```bash
uv run black .
uv run isort .
uv run mypy .
uv run ruff check . --fix
```

Run lint checks in read-only mode (CI-equivalent):

```bash
uv run black --check .
uv run isort --check-only .
uv run mypy .
uv run ruff check .
```

Notes:

- `mypy` defaults are configured in `pyproject.toml` (`ignore_missing_imports`, column numbers).
- `ruff` defaults to `F401` selection from `pyproject.toml`.
- If needed, replace `.` with your own target paths.

### Scripts (uv)

This repository includes utility scripts to normalize metadata and source files.

#### Sort connector manifest

```bash
uv run python -m scripts.sort_info_json
```

This sorts `configuration.fields` and `operations` alphabetically in `sekoia-io-xdr/info.json`.

For CI-style validation without writing changes:

```bash
uv run python -m scripts.sort_info_json --check
```

#### Sort operation payload keys

Sort operation `build_payload` dict keys in operation modules:

```bash
uv run python -m scripts.sort_operation_payload_keys
```

Check-only mode:

```bash
uv run python -m scripts.sort_operation_payload_keys --check
```

#### Deprecation actions

##### Deprecate one operation

```bash
uv run python -m scripts.deprecate_operation <operation> --replacement <new_operation>
```

Without replacement:

```bash
uv run python -m scripts.deprecate_operation <operation>
```

##### Deprecate one operation parameter

```bash
uv run python -m scripts.deprecate_operation_parameter <operation> <parameter> --replacement <new_parameter>
```

Without replacement:

```bash
uv run python -m scripts.deprecate_operation_parameter <operation> <parameter>
```

##### Normalize deprecated metadata

Normalize deprecated operation and parameter metadata in `sekoia-io-xdr/info.json`:

```bash
uv run python -m scripts.normalize_deprecated_parameters
```

Check-only mode:

```bash
uv run python -m scripts.normalize_deprecated_parameters --check
```

## Operation naming convention

To minimize remapping in FortiSOAR, this connector follows a simple naming policy:

- `operation` in `sekoia-io-xdr/info.json` is derived from the action `slug` in [automation-library/Sekoia.io/action_*.json](https://github.com/SEKOIA-IO/automation-library/tree/develop/Sekoia.io).
- When multiple action definitions exist for the same capability, prefer the non-deprecated action as the functional source of truth.
- `title` and `description` are aligned with action metadata (`name` and `description`) whenever possible.
- The [Sekoia.io full OpenAPI 3.1 schema in JSON format](https://docs.sekoia.com/developer/api/) is the source of truth for HTTP method, endpoint, parameters, and constraints.

In short: action `slug` drives operation keys, and OpenAPI drives request/response contract details.

Scope rule:

- Prefer adding or updating operations that map to existing Sekoia actions.
- Add an OpenAPI-only operation only when no action definition exists and the need is explicit.

Example:

- The action file can be named `action_lists_cases.json`, while its action `slug` is `search_cases`.
- The connector operation key is therefore `search_cases` in `sekoia-io-xdr/info.json`.
- The Python module name can differ over time during refactors; the stable key exposed to FortiSOAR remains the action `slug`.

## Deprecation

### Deprecated operation migration

Use this migration rule when replacing an existing connector operation:

1. Create the new operation using the current action slug.
2. Deprecate the old operation in `sekoia-io-xdr/info.json` with a replacement message.
3. Keep the old operation implementation available until removal.

Parameter compatibility policy:

- If the operation slug does not change, parameter aliases can be used to preserve backward compatibility during migration.
- If the operation slug changes, do not carry over legacy parameter aliases to the new operation unless the action definition explicitly documents backward-compatible aliases.

### Deprecation conventions

This repository uses explicit conventions for deprecated metadata in
`sekoia-io-xdr/info.json`.

### Deprecated operation

- `description`: `Deprecated operation. Use <new_operation> operation instead.`
- `description` (no replacement): `Deprecated operation. There is no replacement.`
- `title`: `[Deprecated] <Title>`

Script:

```bash
uv run python -m scripts.deprecate_operation <operation> --replacement <new_operation>
```

Without replacement:

```bash
uv run python -m scripts.deprecate_operation <operation>
```

### Deprecated operation parameter

- `description`: `Deprecated parameter. Use <new_parameter> parameter instead.`
- `description` (no replacement): `Deprecated alias. There is no replacement.`
- `title`: `[Deprecated] <Title>`

Script:

```bash
uv run python -m scripts.deprecate_operation_parameter <operation> <parameter> --replacement <new_parameter>
```

Without replacement:

```bash
uv run python -m scripts.deprecate_operation_parameter <operation> <parameter>
```

### Normalize deprecated metadata

Use one command to normalize both deprecated operation and parameter metadata in
`info.json`:

```bash
uv run python -m scripts.normalize_deprecated_parameters
```

Check-only mode:

```bash
uv run python -m scripts.normalize_deprecated_parameters --check
```

## CI pipeline

GitHub Actions currently uses four independent workflows:

- `lint.yml`: runs code linting and static quality checks in parallel.
- `tests.yml`: runs the unit test suite on multiple Python versions (`3.9` to `3.14`).
- `normalize_info_json.yml`: runs read-only validation on `sekoia-io-xdr/info.json` metadata rules.
- `normalize_operations.yml`: runs read-only normalization checks on operation source files.

The `normalize_info_json` and `normalize_operations` stages are intentionally separated from linting, so repository normalization checks can evolve independently as new rules are added.

Any failure in one workflow marks the CI pipeline as failed.

### Current test limitations

The current test suite is unit-test oriented and uses mocks extensively:

- Sekoia API calls are mocked (no live HTTP calls to `app.sekoia.io`).
- FortiSOAR SDK/runtime dependencies are stubbed or mocked for local execution.

As a result, tests validate connector logic, payload construction, and operation routing,
but they do not validate end-to-end behavior against a real Sekoia tenant or a real FortiSOAR runtime.

Note: `fortisoar_sdk` remains an external dependency provided through Fortinet's distribution process.

## Authors

- [Clement Burtscher](https://github.com/clement-burtscher-sekoia)
