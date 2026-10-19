# Security Policy

## Supported Versions

| Version | Supported |
| --- | --- |
| 1.x | ✅ Yes |

## Scope

This repository is a knowledge and analysis skill — it contains Python tooling scripts, reference files, and JSON schemas. There is no running service or user-facing application. Vulnerabilities worth reporting include:

- Unsafe code patterns in `tooling/` scripts (e.g., command injection, path traversal)
- A reference file or example that inadvertently demonstrates harmful offensive techniques
- A dependency with a known CVE in `requirements-dev.txt`

Out of scope: findings from scanning the repo for secrets (there are none stored) or misuse of the skill by downstream systems.

## Reporting a Vulnerability

Do not open a public GitHub issue for security-sensitive findings.

1. Email the maintainer directly, or use GitHub's private vulnerability reporting feature if enabled on this repo.
2. Include: a clear description of the issue, the affected file(s), reproduction steps if applicable, and your assessment of impact.
3. You will receive an acknowledgement within 72 hours and a resolution timeline within 7 days.

All confirmed vulnerabilities will be fixed in the next patch release and credited to the reporter unless they prefer anonymity.

## Disclosure Policy

Once a fix is merged and tagged, the maintainer will publish a brief disclosure note in the release changelog. There is no embargo period for issues that have no working exploit.
