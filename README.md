# connector-sekoia-io-xdr

[![Lint](https://github.com/fortinet-fortisoar/connector-sekoia-io-xdr/actions/workflows/lint.yml/badge.svg)](https://github.com/fortinet-fortisoar/connector-sekoia-io-xdr/actions/workflows/lint.yml)
[![Tests](https://github.com/fortinet-fortisoar/connector-sekoia-io-xdr/actions/workflows/tests.yml/badge.svg)](https://github.com/fortinet-fortisoar/connector-sekoia-io-xdr/actions/workflows/tests.yml)

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
uv run python scripts/sort_info_json.py
```

Run lint checks in read-only mode (CI-equivalent):

```bash
uv run black --check .
uv run isort --check-only .
uv run mypy .
uv run ruff check .
uv run python scripts/sort_info_json.py --check
```

Notes:

- `mypy` defaults are configured in `pyproject.toml` (`ignore_missing_imports`, column numbers).
- `ruff` defaults to `F401` selection from `pyproject.toml`.
- If needed, replace `.` with your own target paths.

### Sort connector manifest

```bash
uv run python scripts/sort_info_json.py
```

This sorts `configuration.fields` and `operations` alphabetically in `sekoia-io-xdr/info.json`.

For CI-style validation without writing changes:

```bash
uv run python scripts/sort_info_json.py --check
```

## CI pipeline

GitHub Actions currently uses two workflows:

- `lint.yml`: runs lint checks in parallel (one check per matrix job) using direct `uv run` linter commands, and verifies `info.json` is already sorted.
- `tests.yml`: runs the unit test suite on multiple Python versions (`3.9` to `3.14`).

Any failure in either job marks the workflow as failed.

### Current test limitations

The current test suite is unit-test oriented and uses mocks extensively:

- Sekoia API calls are mocked (no live HTTP calls to `app.sekoia.io`).
- FortiSOAR SDK/runtime dependencies are stubbed or mocked for local execution.

As a result, tests validate connector logic, payload construction, and operation routing,
but they do not validate end-to-end behavior against a real Sekoia tenant or a real FortiSOAR runtime.

Note: `fortisoar_sdk` remains an external dependency provided through Fortinet's distribution process.