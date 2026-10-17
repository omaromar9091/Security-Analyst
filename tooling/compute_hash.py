#!/usr/bin/env python3
"""Compute SHA-256 for a file and print it."""
import hashlib
import sys
from pathlib import Path

if len(sys.argv) != 2:
    print("usage: compute_hash.py <file>")
    sys.exit(2)

p = Path(sys.argv[1])
if not p.exists():
    print(f"file not found: {p}")
    sys.exit(2)

h = hashlib.sha256()
with p.open("rb") as f:
    for chunk in iter(lambda: f.read(8192), b""):
        h.update(chunk)
print(h.hexdigest())
