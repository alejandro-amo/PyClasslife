"""Run either the unit or integration test suite with environment safeguards."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("suite", choices=("unit", "integration"))
    parser.add_argument("--env-file", type=Path)
    args = parser.parse_args()
    if args.suite == "unit":
        if args.env_file is not None:
            parser.error("unit tests must not receive an environment file")
        test_path = "tests/unit"
    else:
        if args.env_file is None:
            parser.error("integration tests require --env-file")
        name = args.env_file.name.upper()
        if "TEST" not in name or "PROD" in name:
            parser.error("integration environment file must contain TEST and must not contain PROD")
        if not args.env_file.is_file():
            parser.error(f"environment file not found: {args.env_file}")
        for line in args.env_file.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip().strip('"').strip("'")
        test_path = "tests/integration"
    return subprocess.call([sys.executable, "-m", "pytest", "-q", test_path])


if __name__ == "__main__":
    raise SystemExit(main())
