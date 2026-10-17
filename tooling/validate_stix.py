#!/usr/bin/env python3
"""Validate a STIX JSON file with stix2 if installed."""
import sys
from pathlib import Path

if len(sys.argv) != 2:
    print("usage: validate_stix.py <file.json>")
    sys.exit(2)

p = Path(sys.argv[1])
if not p.exists():
    print("file not found")
    sys.exit(2)

try:
    import stix2
except Exception:
    print("stix2 not installed — skipping STIX validation")
    sys.exit(0)

try:
    data = p.read_text(encoding="utf-8")
    stix2.parse(data)
    print("STIX parse OK")
except Exception as e:
    print("STIX parse error:", e)
    sys.exit(1)
