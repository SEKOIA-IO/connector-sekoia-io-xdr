from pathlib import Path

# Bridge package name (valid Python identifier) to connector source directory.
__path__ = [str(Path(__file__).resolve().parents[1] / "sekoia-io-xdr")]
