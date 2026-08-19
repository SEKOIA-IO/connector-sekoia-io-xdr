# Linter and Type-Checking Recommendations

## 1. Remove global ruff auto-fix in config

In the _mise.toml_ file, as their names suggest, the check tasks must remain read-only and avoid unexpected file mutations

- File _mise.toml_:

```toml
[tasks.lint]
description = "Check code style and types"
run = [
    "uv run ruff check .",
    "uv run ruff format --check .",
    "uv run mypy .",
]

[tasks.format]
description = "Format and auto-fix code"
run = [
    "uv run ruff check --fix .",
    "uv run ruff format .",
]
```

Indeed, in the `[tasks.lint]` task:
- `ruff format --check` is always read-only
- but `ruff check` can still apply fixes when `fix = true`

So you could use `--no-fix` in the `[tasks.lint]` task of the _mise.toml_ file, or prefer removing global `fix = true` in the _pyproject.toml_ file, to avoid unexpected changes:

- File _pyproject.toml_:

```toml
[tool.ruff]
line-length = 119
target-version = "py314"
- fix = true
```

## 2. Restrict mypy to explicit importable targets  

It would allow fewer false positives and faster runs

- File _pyproject.toml_:

```toml
[tool.mypy]
files = ["your_package_name", "tests"]
```

For example in the _HTTP/_ directory:

- File _HTTP/pyproject.toml_:

```toml
[tool.mypy]
files = ["http_module", "tests", "main.py"]
```

**Note:** 
- However, it must be acknowledged that this requires customizing the configuration for each vendor/automation module, which can be difficult to maintain or may conflict with the repository’s standardization/harmonization efforts
- In this case, it might be better to use identical naming conventions and packaging for all vendors/automation modules, such as:
    - _src/_ (instead of _http_module/_, _iknowwhatyoudownload/_, _ilert/_, _mandrill_module/_, etc.)
    - _tests/_

If it is supported by the current mypy version, you could also add the `exclude_gitignore = true` key to prevent mypy from running on directories excluded by the _.gitignore_ file: _.pytest_cache/_, ._mypy_cache/_, _.ruff_cache/_, etc.

```toml
[tool.mypy]
exclude_gitignore = true
```
