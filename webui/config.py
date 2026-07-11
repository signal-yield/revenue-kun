"""Web UI transport configuration.

Currently limited to the upload-size limit. Kept separate from
`src/revenue_kun/` because this is Web UI transport configuration, not
domain logic.
"""
from __future__ import annotations

import os

ENV_MAX_UPLOAD_MB = "REVENUE_KUN_MAX_UPLOAD_MB"
DEFAULT_MAX_UPLOAD_MB = 20

_BYTES_PER_MIB = 1024 * 1024


class WebUIConfigError(ValueError):
    """Raised when a Web UI environment-variable setting is invalid.

    A set-but-invalid value is rejected outright rather than silently
    falling back to the default, so a misconfigured limit never becomes a
    silent, unbounded upload allowance.
    """


def get_max_upload_mb() -> int:
    """Return the configured upload-size limit in MiB.

    Reads ``REVENUE_KUN_MAX_UPLOAD_MB``. Returns ``DEFAULT_MAX_UPLOAD_MB``
    when the variable is unset. Raises ``WebUIConfigError`` when the
    variable is set to anything other than a positive integer.
    """
    raw = os.environ.get(ENV_MAX_UPLOAD_MB)
    if raw is None:
        return DEFAULT_MAX_UPLOAD_MB

    raw = raw.strip()
    if not raw:
        raise WebUIConfigError(
            f"{ENV_MAX_UPLOAD_MB} is set but empty; expected a positive integer."
        )

    try:
        value = int(raw)
    except ValueError:
        raise WebUIConfigError(
            f"{ENV_MAX_UPLOAD_MB} must be a positive integer; "
            "the configured value is not numeric."
        ) from None

    if value <= 0:
        raise WebUIConfigError(
            f"{ENV_MAX_UPLOAD_MB} must be a positive integer; "
            f"the configured value ({value}) is not."
        )

    return value


def get_max_upload_bytes() -> int:
    """Return the configured upload-size limit in bytes."""
    return get_max_upload_mb() * _BYTES_PER_MIB
