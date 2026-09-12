"""Public configuration helpers for PyClasslife."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, Mapping

from .exceptions import ConfigurationError

REQUIRED_CREDENTIALS = ("CLASSLIFE_API_KEY", "CLASSLIFE_CLIENT_ID")


@dataclass(frozen=True, slots=True)
class ClasslifeCredentials:
    """Credentials read from the process environment."""

    api_key: str = field(repr=False)
    client_id: str = field(repr=False)


def get_credentials(
    *,
    source: Literal["env_vars", "env_file"] = "env_vars",
    env_file: str | os.PathLike[str] | None = None,
) -> ClasslifeCredentials:
    """Return Classlife credentials using an explicit configuration method.

    ``source="env_vars"`` reads the current process environment;
    ``source="env_file"``
    reads the file specified by ``env_file``. Values are never logged and the
    process environment is never modified.
    """
    normalized_source = source.strip().lower() if isinstance(source, str) else ""
    if normalized_source not in {"env_vars", "env_file"}:
        raise ConfigurationError("source must be either 'env_vars' or 'env_file'")
    if normalized_source == "env_vars":
        values = {
            "CLASSLIFE_API_KEY": os.environ.get("CLASSLIFE_API_KEY", ""),
            "CLASSLIFE_CLIENT_ID": os.environ.get("CLASSLIFE_CLIENT_ID", ""),
        }
    else:
        if env_file is None:
            raise ConfigurationError("env_file is required when source='env_file'")
        values = _read_credentials_file(path=env_file)
    values = {name: values.get(name, "").strip() for name in REQUIRED_CREDENTIALS}
    missing = [name for name in REQUIRED_CREDENTIALS if not values[name]]
    if missing:
        raise ConfigurationError(
            "Missing required Classlife environment variables: " + ", ".join(missing)
        )
    return ClasslifeCredentials(
        api_key=values["CLASSLIFE_API_KEY"],
        client_id=values["CLASSLIFE_CLIENT_ID"],
    )


def _read_credentials_file(*, path: str | os.PathLike[str]) -> Mapping[str, str]:
    try:
        content = Path(path).read_text(encoding="utf-8")
    except (OSError, TypeError) as error:
        raise ConfigurationError("Unable to read credentials file") from error
    values: dict[str, str] = {}
    for line_number, line in enumerate(content.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            raise ConfigurationError(f"Invalid credentials file at line {line_number}")
        name, value = stripped.split("=", 1)
        name = name.strip()
        if name in REQUIRED_CREDENTIALS:
            values[name] = value.strip().strip("\"'")
    return values
