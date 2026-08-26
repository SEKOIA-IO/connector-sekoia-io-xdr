# FortiSOAR Connector Upload Runbook (SEKOIA.IO)

This guide is ordered chronologically so a developer can execute the workflow step by step.

## Step 1 - Access FortiSOAR

Open an SSH tunnel:

```bash
ssh -L 15443:192.168.122.71:443 clement_burtscher@51.77.165.22
```

Then open:

```text
https://127.0.0.1:15443
```

Use FortiSOAR credentials from Bitwarden.

> [!NOTE]
> Keep the SSH session open while you use the UI. Closing it breaks access immediately.

## Step 2 - Verify Role Permissions and BYOC

Before trying any upload, verify the account configuration.

Required role permissions:

- Connectors: `Create`, `Read`, `Update`, `Delete`
- Content Hub: `Read`

Required platform setting:

- `System > System Configuration > Advanced Development Features`
- Enable `Build Your Own Connector (BYOC)`

Expected UI result:

- In `Content Hub > Manage > Upload`, you must see `Upload Connector`.

> [!WARNING]
> If only `Upload Solution Pack` is visible, do not debug the archive first. This is usually a permission/BYOC issue.

> [!TIP]
> Typical misleading errors in this situation:
> - `.tgz`: `The file type is invalid. Please upload a valid exported zip file`
> - `.zip`: `Incorrect required metadata in info.json file. Upload a valid solution pack.`

## Step 3 - Decide the Correct Workflow (Create vs Update)

Choose the workflow before packaging.

### 3.1 New connector

- Use archive upload (`Upload Connector`).

### 3.2 Existing connector update

- Do not rely on archive upload.
- Update manually in editor, file by file.
- Upload/rename/delete actions are one-by-one.

> [!WARNING]
> For updates, do not delete `info.json` or `connector.py`.

> [!NOTE]
> Current UI limitations: no multi-file upload and no move operation.

## Step 4 - Build the Archive (for New Connector Creation)

Standard build:

```bash
uv run python -m scripts.build_connector_archives
```

Build without internal parent directory:

```bash
uv run python -m scripts.build_connector_archives \
  --no-parent-dir \
  --zip-name sekoia-io-xdr_clement-2.0.0.zip \
  --tgz-name sekoia-io-xdr_clement-2.0.0.tgz
```

> [!NOTE]
> Packaging with `uv` requires `requirements.txt` to exist and be synchronized.

## Step 5 - Validate Archive Structure Before Upload

Inspect the zip content:

```bash
unzip -Z1 dist/sekoia-io-xdr_clement-2.0.0.zip | sort
```

Minimum required files:

- `connector.py`
- `info.json`
- `requirements.txt`

Must be excluded:

- `.github/`
- `.gitignore`

> [!WARNING]
> If two different `connector.py` files exist in the package, FortiSOAR rejects publication with an invalid connector structure error.

## Step 6 - Upload and Verify

In FortiSOAR:

1. Go to `Content Hub > Manage > Upload`.
2. Select `Upload Connector`.
3. Upload archive and check import logs.

> [!TIP]
> If import fails, first confirm the menu used was `Upload Connector` and not `Upload Solution Pack`.

## Step 7 - Troubleshooting Quick Map

- **Only "Upload Solution Pack" visible**
  - Fix roles + BYOC.
- **"Invalid connector structure :: connector.py file ... multiple or not provided"**
  - Ensure exactly one `connector.py` in the archive.
- **Archive builds but import fails early**
  - Recheck required files (`connector.py`, `info.json`, `requirements.txt`) and excluded files (`.github`, `.gitignore`).

## Final Checklist

- FortiSOAR reachable through SSH tunnel.
- Account has connector permissions and BYOC enabled.
- Correct workflow selected (create via archive vs manual update).
- Archive validated locally before upload.
- Upload performed from `Upload Connector`.
