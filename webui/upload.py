"""Upload validation and temporary-file foundation for the Web UI.

Reused by later Web UI endpoints (see Issue #80). Nothing in this module
parses CSV/PDF content, calls into `revenue_kun`, or generates a workbook --
it only handles the transport-level concerns of accepting an upload safely:

- extension allow-listing
- server-generated temporary filenames (never the client-supplied name)
- an isolated, always-cleaned-up per-request temporary directory
- a chunked, size-limited write helper that never buffers a whole upload
  in memory
"""
from __future__ import annotations

import contextlib
import shutil
import tempfile
import uuid
from pathlib import Path, PurePosixPath
from typing import BinaryIO, Iterator

ALLOWED_EXTENSIONS: frozenset[str] = frozenset({".csv", ".pdf"})

_DEFAULT_CHUNK_SIZE = 1024 * 1024  # 1 MiB


class UploadValidationError(ValueError):
    """Raised when an uploaded file fails a transport-level validation check."""


class UploadTooLargeError(UploadValidationError):
    """Raised when an upload exceeds the configured size limit."""


def validate_extension(client_filename: str | None) -> str:
    """Validate the client-supplied filename's extension.

    Only the final suffix is considered, so a disguised name such as
    ``evil.csv.exe`` is rejected (final suffix ``.exe``) while a name such
    as ``evil.exe.csv`` is accepted at this transport-level check (final
    suffix ``.csv``); deeper content validation (e.g. a PDF signature
    check) is out of scope for this module and belongs to the endpoint
    that actually reads the file.

    The client-supplied filename is used only to read its extension here.
    It must never be reused as an on-disk path -- see
    ``generate_temp_filename``.

    Returns the lowercase extension (``.csv`` or ``.pdf``).
    Raises ``UploadValidationError`` for anything else, including a
    missing extension.
    """
    suffix = PurePosixPath(client_filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise UploadValidationError(
            "Unsupported file type. Only .csv and .pdf are accepted."
        )
    return suffix


def generate_temp_filename(extension: str) -> str:
    """Return a server-generated filename for the given extension.

    Always derived from a fresh UUID, never from the client-supplied
    filename, a room number, a tenant name, or any other extracted value.
    """
    return f"{uuid.uuid4().hex}{extension}"


@contextlib.contextmanager
def request_temp_dir() -> Iterator[Path]:
    """Create an isolated, per-request temporary directory.

    Deleted on both normal completion and exception. Never reuses a fixed
    shared location such as the CLI's ``output/`` directory. Callers must
    not write the yielded path to normal logs.
    """
    path = Path(tempfile.mkdtemp(prefix="revenue_kun_webui_"))
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


def write_limited(
    source: BinaryIO,
    destination: Path,
    max_bytes: int,
    chunk_size: int = _DEFAULT_CHUNK_SIZE,
) -> int:
    """Copy from a file-like ``source`` to ``destination``, enforcing ``max_bytes``.

    Reads in fixed-size chunks rather than loading the whole upload into
    memory. ``source`` only needs a synchronous ``.read(n)`` method, so
    this works with a plain file object or FastAPI's
    ``UploadFile.file`` without depending on FastAPI itself.

    On any failure (including exceeding ``max_bytes``), the partially
    written destination file is removed before the error propagates.

    Returns the total number of bytes written.
    """
    written = 0
    try:
        with destination.open("wb") as out:
            while True:
                chunk = source.read(chunk_size)
                if not chunk:
                    break
                written += len(chunk)
                if written > max_bytes:
                    raise UploadTooLargeError(
                        f"Upload exceeds the configured limit of {max_bytes} bytes."
                    )
                out.write(chunk)
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    return written
