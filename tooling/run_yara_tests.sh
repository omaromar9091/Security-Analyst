#!/usr/bin/env bash
# Run YARA rules in this repository against the examples/ directory.
#
# Usage:
#   bash tooling/run_yara_tests.sh
#
# Requires the `yara` command-line tool to be installed.
# If not installed, the script exits 0 with an informational message
# so that CI does not fail on an optional native dependency.
#
# Exit codes:
#   0 — all rules matched or yara not installed (skip)
#   1 — one or more yara invocations returned an error

set -euo pipefail

RULES_DIR="."
SAMPLES_DIR="examples"

if ! command -v yara >/dev/null 2>&1; then
  echo "yara not found — skipping YARA tests (install yara-python or the yara binary)"
  exit 0
fi

rule_files=()
while IFS= read -r -d '' f; do
  rule_files+=("$f")
done < <(find "$RULES_DIR" -name "*.yar" -o -name "*.yara" -print0 2>/dev/null)

if [ "${#rule_files[@]}" -eq 0 ]; then
  echo "no .yar / .yara rule files found — nothing to run"
  exit 0
fi

echo "found ${#rule_files[@]} rule file(s); scanning $SAMPLES_DIR/"
errors=0

for rule in "${rule_files[@]}"; do
  echo "--- $rule"
  if ! yara -r "$rule" "$SAMPLES_DIR/"; then
    echo "error running: yara $rule $SAMPLES_DIR/" >&2
    errors=$((errors + 1))
  fi
done

if [ "$errors" -gt 0 ]; then
  echo "$errors rule file(s) produced errors"
  exit 1
fi

echo "all YARA checks passed"
