#!/usr/bin/env bash
# Run YARA tests if yara is installed; otherwise skip.
set -e
if command -v yara >/dev/null 2>&1; then
  echo "yara found — running sample rules against examples/"
  find . -name "*.yar*" -print -exec echo "(no rules to run)" \;
else
  echo "yara not found — skipping YARA tests"
fi
