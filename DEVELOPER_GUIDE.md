# Developer Guide

This guide is for anyone who wants to modify, extend, or debug the Security-Analyst skill. If you just want to use it, `README.md` is the right place to start.

## Repository layout

```
Security-Analyst/
├── SKILL.md                    routing logic, tool definition, scope boundaries
├── README.md                   user-facing quick start and reference
├── banner.svg                  README header image
├── references/                 one file per analysis domain — this is the core content
├── schemas/
│   └── finding.schema.json     JSON Schema (draft-07) for structured output
├── templates/
│   ├── finding_template.md     blank finding to fill in
│   └── remediation_checklist.md
├── examples/
│   ├── README.md                explains the sample files below
│   ├── finding_example.json    a valid, schema-passing finding
│   ├── load_test_example.json  a valid, schema-passing load test finding
│   └── nmap_samples/           raw scan output used in tests
├── tooling/
│   ├── compute_hash.py         SHA-256 a file
│   ├── validate_stix.py        parse/validate a STIX 2.1 JSON file
│   ├── run_yara_tests.sh       run .yar rules against examples/ (needs yara)
│   └── load_test.py            HTTP load tester — baseline, load, stress, spike, soak
├── analysis-docker/
│   └── Dockerfile              isolated Python 3.11-slim environment
├── tests/
│   ├── test_docs.py            structure and content checks (8 tests)
│   └── test_schema.py          JSON Schema validation (needs jsonschema)
├── .github/
│   ├── workflows/
│   │   ├── ci.yml               unit tests, bandit, pip-audit on every PR
│   │   └── pylint.yml           pylint on every push
│   ├── ISSUE_TEMPLATE/
│   ├── PULL_REQUEST_TEMPLATE.md
│   ├── CODEOWNERS
│   └── dependabot.yml
├── CONTRIBUTING.md             how to propose changes
├── CODE_OF_CONDUCT.md
├── SECURITY.md                  how to report a vulnerability in this repo
├── LICENSE
├── pyproject.toml              build metadata, tool config (black, bandit, pylint)
├── requirements-dev.txt        pinned dev dependencies
├── .editorconfig               editor formatting rules
├── .dockerignore
└── .gitignore
```

## Docker

Build from the repository root (`.dockerignore` prevents secrets and `.git` from entering the image):

```bash
docker build -t security-analyst -f analysis-docker/Dockerfile .
docker run --rm -v "$(pwd)":/workspace security-analyst \
    tooling/compute_hash.py /workspace/sample.bin
```

The container runs as a non-root user (`analyst`, uid 1001). The base image is pinned to a SHA-256 digest — update it periodically or let Dependabot open a PR when a new digest is available.

---

## Setting up a dev environment

```bash
git clone https://github.com/omaromar9091/Security-Analyst.git
cd Security-Analyst

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements-dev.txt
```

## Running the checks

```bash
# Unit tests
python -m unittest discover -s tests -v

# SAST — static security analysis on Python scripts
bandit -r tooling/ -f txt

# Dependency audit — check for known CVEs
pip-audit -r requirements-dev.txt

# Lint — needs `pip install -e .[dev]`
pylint tooling/ tests/ --errors-only
```

All four should pass before you open a pull request. The first three run in `ci.yml` on every PR; pylint runs in `pylint.yml` on every push.

## Adding a new reference file

1. Create `references/<domain>.md`. Model it on an existing file — each one has an introduction, a classification section (MITRE ATT&CK + CVSS guidance), and worked examples in input → analysis → output shape.
2. Add a row to the domain table in `SKILL.md` under `## Analysis Domains`.
3. Add a row to the domain table in `README.md` under `## Domains`.
4. Update `SKILL.md`'s routing section to describe when to open the new file.
5. Run the tests — `test_domain_tables_match_seven_references` will fail if the count is off.

## Adding a tooling script

- Keep it focused: one script, one purpose.
- Add a module-level docstring explaining usage, inputs, and outputs.
- Handle missing arguments and missing files gracefully (print usage, exit 2).
- Do not shell out with `os.system` or `subprocess` on unsanitised user input.
- `validate_stix.py` accepts `--require-stix` to force a hard failure when `stix2` is not installed — use this flag in CI steps that specifically test STIX output.
- Add a usage example to `README.md` under "Tooling".

## Commit message convention

```
<type>(<scope>): <short summary>

type:  fix | feat | docs | test | ci | refactor | chore
scope: references | tooling | schema | tests | ci | docs
```

Examples:
```
docs(references): add worked example for LFI in vulnerability-analysis.md
feat(tooling): add log_parser.py for Apache access log triage
fix(schema): make cvss field optional not required
ci: add bandit step to CI workflow
```

## Release process

This project follows [Semantic Versioning](https://semver.org/):
- **PATCH** (1.0.x): fixes, typos, minor example improvements
- **MINOR** (1.x.0): new reference file, new tooling script, schema additions
- **MAJOR** (x.0.0): breaking changes to SKILL.md interface or schema shape

Tag the release commit: `git tag -a v1.1.0 -m "Release 1.1.0"`.

## Code style

Python scripts follow PEP 8 and are formatted with `black --line-length 100`. Run `black tooling/` before committing. The `.editorconfig` covers indentation for all file types.

## Questions and discussions

Open a GitHub Discussion or an issue tagged `question`. Check existing issues before opening a new one.
