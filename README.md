![Security Analyst Skill](banner.svg)

# Security Analyst Skill

Seven analysis domains for any AI agent or model. Point it at the right reference file and get structured output — findings scored against MITRE ATT&CK and CVSS v3.1, load test results with P50/P95/P99 latency, STIX 2.1 indicators, YARA rules.

Works with Claude, LangChain, Semantic Kernel, MCP, or a direct API call.

---

## Quick start

```bash
git clone https://github.com/omaromar9091/Security-Analyst.git
cd Security-Analyst
pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

**Claude projects:** add the `Security-Analyst/` folder to your project's skills directory.

**Other frameworks:** copy the tool definition from `SKILL.md → Tool Definition` and pass the relevant `references/` file as a system instruction.

---

## Domains

| # | Domain | Use when you have |
| --- | --- | --- |
| 0 | **Reconnaissance & OSINT** | Nmap / Shodan / Sublist3r output, an attack surface to map |
| 1 | **Vulnerability & Exploit Logic** | Source code, a CVE, a crash dump, assembly to triage |
| 2 | **AI-Generated Code Review** | Code from a chat model, IDE autocomplete, or coding agent |
| 3 | **Threat & Binary Analysis** | A suspicious file, process, log, or post-breach evidence |
| 4 | **Human & Attack Vectors** | A phishing message, social engineering scenario, awareness gap |
| 5 | **Defense & Countermeasures** | A patch plan, incident to remediate, OPSEC review |
| 6 | **Load Testing & Performance** | A service to measure under controlled traffic |

## How it works

`SKILL.md` holds the routing logic. Before writing a response the agent reads whichever reference file fits the task — or both files when a task crosses domains (a vulnerability confirmed in code review that now needs a remediation plan, for example).

---

## Output format

Every finding uses the same shape, validated against `schemas/finding.schema.json`:

```json
{
  "id": "F-2026-0001",
  "title": "Internet-exposed MySQL port",
  "analysis_domain": "reconnaissance",
  "evidence": "Port 3306 open on 203.0.113.12, reachable from the public internet",
  "impact": "Database reachable without VPN or firewall; credential brute-force is the next step",
  "confidence": "high",
  "cwe": [],
  "mitre_attck": ["T1046"],
  "cvss": "AV:N/AC:L/PR:N/UI:N — High",
  "remediation": "Restrict 3306 to internal CIDR only; enforce least-privilege on all DB accounts",
  "verification_steps": [
    "Confirm port is closed from an external scanner after the firewall rule is applied",
    "Verify application still connects from inside the network"
  ]
}
```

Load test findings use `"analysis_domain": "load_testing"` and report P50/P95/P99 latency, RPS, and error rate in the `evidence` field. See `examples/load_test_example.json`.

Validate any finding locally:

```bash
python -c "
import json
from jsonschema import validate
schema  = json.load(open('schemas/finding.schema.json'))
finding = json.load(open('examples/finding_example.json'))
validate(instance=finding, schema=schema)
print('valid')
"
```

---

## Tooling

| Script | What it does |
| --- | --- |
| `tooling/compute_hash.py <file>` | SHA-256 a file for IOC records |
| `tooling/validate_stix.py <file.json>` | Parse and validate a STIX 2.1 bundle |
| `tooling/run_yara_tests.sh` | Run `.yar` rules against `examples/` |
| `tooling/load_test.py` | HTTP load tester — baseline, load, stress, spike, soak |

```bash
# hash a file before analysis
python tooling/compute_hash.py /path/to/sample.bin

# validate a STIX export
python tooling/validate_stix.py exports/indicators.json

# 5-user baseline test against a local server
python tooling/load_test.py \
    --target http://localhost:8080/api/health \
    --authorized-by "Self, local dev environment" \
    --type baseline --users 5 --duration 60

# ramp to 50 users, hold 10 minutes, SLA: P95 < 500 ms
python tooling/load_test.py \
    --target https://staging.example.com/v1/search \
    --authorized-by "Ali Hassan, Platform Lead" \
    --type load --users 50 --ramp 60 --duration 600 \
    --latency-sla 500 --output results/search-load.json
```

`load_test.py` requires `--authorized-by` on every run. It refuses to start without it.

---

## Docker

For analyzing untrusted samples in isolation:

```bash
# build from the repo root (.dockerignore keeps .git and secrets out)
docker build -t security-analyst -f analysis-docker/Dockerfile .

# run a tool inside the container (runs as non-root user analyst:1001)
docker run --rm -v "$(pwd)":/workspace security-analyst \
    tooling/compute_hash.py /workspace/sample.bin
```

---

## Repository layout

```
Security-Analyst/
├── SKILL.md
├── references/
│   ├── reconnaissance.md
│   ├── vulnerability-analysis.md
│   ├── ai-generated-code.md
│   ├── threat-analysis.md
│   ├── social-engineering.md
│   ├── remediation.md
│   └── load-testing.md
├── schemas/
│   └── finding.schema.json
├── templates/
│   ├── finding_template.md
│   └── remediation_checklist.md
├── examples/
│   ├── finding_example.json
│   ├── load_test_example.json
│   └── nmap_samples/
├── tooling/
│   ├── compute_hash.py
│   ├── validate_stix.py
│   ├── run_yara_tests.sh
│   └── load_test.py
├── analysis-docker/
│   └── Dockerfile
└── tests/
    ├── test_docs.py
    └── test_schema.py
```

---

## Checks before pushing

```bash
python -m unittest discover -s tests -v   # unit tests
bandit -r tooling/ -f txt -ll             # static security analysis
pip-audit -r requirements-dev.txt         # dependency CVE check
pylint tooling/ tests/ --errors-only      # lint (pip install -e .[dev])
```

All four run automatically via GitHub Actions — tests, bandit, and pip-audit on every pull request (`ci.yml`), pylint on every push (`pylint.yml`).

---

## Scope

Analysis and defense only. No working exploit code, no payloads, no offensive tooling. Load tests run only against systems you own or have written authorization to test — `load_test.py` enforces this. Full scope statement in `SKILL.md → Scope and Boundaries`.

---

## Contributing

[CONTRIBUTING.md](CONTRIBUTING.md) · [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) · [SECURITY.md](SECURITY.md)

---

## License

MIT — see [LICENSE](LICENSE).
