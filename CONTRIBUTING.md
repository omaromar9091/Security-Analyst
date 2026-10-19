# Contributing to Security-Analyst

Thanks for taking the time to contribute. These guidelines keep the review process smooth and the repository consistent.

## Before you start

- Check existing issues and pull requests — your idea may already be in progress.
- For anything beyond a small fix, open an issue first and describe what you want to change and why.
- Read `DEVELOPER_GUIDE.md` for the full technical setup and repo layout.

## Getting your environment ready

```bash
git clone https://github.com/omaromar9091/Security-Analyst.git
cd Security-Analyst

python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate

pip install -r requirements-dev.txt
```

## Before opening a pull request

Run all three checks and make sure they pass:

```bash
# 1. Unit tests
python -m unittest discover -s tests -v

# 2. Static security analysis
bandit -r tooling/ -f txt -ll

# 3. Dependency audit
pip-audit -r requirements-dev.txt
```

## Types of contribution

**Reference files** (`references/`): add depth, fix a methodology error, or add a worked example. Follow the existing file structure — introduction, classification guidance, worked examples in input → analysis → output shape.

**Tooling scripts** (`tooling/`): one script, one purpose, Google-style docstring, proper error handling, no shell-out on unsanitised input.

**Schema** (`schemas/`): additions should remain backward-compatible; if a field becomes required, update `examples/finding_example.json` too.

**Tests** (`tests/`): new content that changes the structure or adds a domain should come with a test or an update to an existing one.

## Code style

- Python: PEP 8, formatted with `black --line-length 100`.
- Commit messages follow the convention in `DEVELOPER_GUIDE.md`.
- Keep pull requests small and focused — one logical change per PR.

## Scope

This repository is for **defensive analysis only**. Do not add content that enables unauthorized access, exploitation, payload delivery, or data exfiltration. Redact any real secrets, IP addresses, or PII from examples.

## Labelling issues

| Label | Meaning |
| --- | --- |
| `bug` | Something produces wrong or unexpected output |
| `enhancement` | Improvement to existing content or tooling |
| `good first issue` | Well-scoped task for a first contribution |
| `security` | Report involving a vulnerability in the repo itself |
| `question` | General discussion |

## Code of Conduct

All contributors are expected to follow the [Code of Conduct](CODE_OF_CONDUCT.md).
