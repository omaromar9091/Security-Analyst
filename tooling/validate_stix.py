#!/usr/bin/env python3
"""Validate a STIX 2.1 JSON file using the stix2 library.

Usage:
    python tooling/validate_stix.py <file.json> [--require-stix]

By default, if the stix2 library is not installed the script prints a
warning and exits 0 — useful when stix2 is an optional dependency in a
local dev environment.

Pass --require-stix to make a missing stix2 installation a hard failure
(exit 3). Use this flag in CI to catch environment misconfiguration.

Exit codes:
    0 — file is valid, or stix2 not installed and --require-stix not set
    1 — STIX parse failed
    2 — usage error or file not found
    3 — stix2 not installed and --require-stix was set

Example:
    python tooling/validate_stix.py exports/indicators.json
    python tooling/validate_stix.py exports/indicators.json --require-stix
"""

import argparse
import json
import sys
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser.

    Returns:
        Configured ArgumentParser instance.
    """
    p = argparse.ArgumentParser(
        prog="validate_stix.py",
        description="Validate a STIX 2.1 JSON file.",
    )
    p.add_argument("file", type=Path, help="Path to the STIX JSON file")
    p.add_argument(
        "--require-stix",
        action="store_true",
        dest="require_stix",
        help="Exit 3 if the stix2 library is not installed (use in CI)",
    )
    return p


def load_json(path: Path) -> str:
    """Read a file and return its text content.

    Args:
        path: Path to the JSON file.

    Returns:
        Raw file text.

    Raises:
        SystemExit: On I/O error or non-UTF-8 encoding.
    """
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"error: cannot read file — {exc}", file=sys.stderr)
        sys.exit(2)


def main() -> None:
    """Entry point: validate the STIX file supplied on the command line."""
    args = build_parser().parse_args()

    if not args.file.exists():
        print(f"error: file not found: {args.file}", file=sys.stderr)
        sys.exit(2)

    # Validate that the file is at least valid JSON before attempting STIX parse
    raw = load_json(args.file)
    try:
        json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"error: not valid JSON — {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        import stix2  # type: ignore[import]
    except ImportError:
        if args.require_stix:
            print(
                "error: stix2 is not installed — install it with: pip install stix2\n"
                "       (pass --require-stix in CI to catch this; omit it locally if stix2 is optional)",
                file=sys.stderr,
            )
            sys.exit(3)
        print("warning: stix2 not installed — JSON structure is valid but STIX semantics were not checked")
        sys.exit(0)

    try:
        stix2.parse(raw)
        print(f"OK: {args.file} is a valid STIX 2.1 document")
    except Exception as exc:  # stix2 raises various custom exception types
        print(f"error: STIX parse failed — {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
