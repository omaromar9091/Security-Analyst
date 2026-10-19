#!/usr/bin/env python3
"""Compute the SHA-256 digest of a file.

Usage:
    python tooling/compute_hash.py <file>

Output:
    The hex-encoded SHA-256 digest printed to stdout.

Exit codes:
    0 — success
    2 — wrong number of arguments or file not found

Example:
    python tooling/compute_hash.py examples/finding_example.json
"""

import hashlib
import sys
from pathlib import Path


def sha256_file(path: Path) -> str:
    """Read a file in chunks and return its SHA-256 hex digest.

    Args:
        path: Path to the file to hash.

    Returns:
        64-character lowercase hex string.

    Raises:
        OSError: If the file cannot be read.
    """
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    """Entry point: parse CLI arguments and print the hash."""
    if len(sys.argv) != 2:
        print("usage: compute_hash.py <file>")
        sys.exit(2)

    p = Path(sys.argv[1])
    if not p.exists():
        print(f"error: file not found: {p}", file=sys.stderr)
        sys.exit(2)

    print(sha256_file(p))


if __name__ == "__main__":
    main()
