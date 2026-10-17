![Security Analyst Skill](banner.svg)

# Security Analyst Skill

A cybersecurity analysis skill for any AI model or agent — Claude, LangChain, Semantic Kernel, MCP, or a direct API call. Six analysis domains, each backed by a methodology reference file. Drop it in, point the agent at the right file, and get structured output scored against MITRE ATT&CK and CVSS v3.1.

---

## Quick start

```bash
# clone
git clone https://github.com/omaromar9091/Security-Analyst.git
cd Security-Analyst

# install dev dependencies
pip install -r requirements-dev.txt

# run the test suite
python -m unittest discover -s tests -v
```

**Claude (claude.ai projects):** drop the `Security-Analyst/` folder into your project's skills directory — no further configuration needed.

**Other agent frameworks:** use the tool definition in `SKILL.md` under "Tool Definition" and pass the relevant `references/` files as context or system instructions.

---

## What it covers

| # | Domain | Trigger | Reference |
| --- | --- | --- | --- |
| 0 | **Reconnaissance & OSINT** | Nmap / Shodan / Sublist3r output, attack-surface mapping | `references/reconnaissance.md` |
| 1 | **Vulnerability & Exploit Logic** | Code review, CVE triage, crash dumps, assembly snippets | `references/vulnerability-analysis.md` |
| 2 | **AI-Generated Code Review** | Code from a chat assistant, IDE autocomplete, or coding agent | `references/ai-generated-code.md` |
| 3 | **Threat & Binary Analysis** | Suspicious files, process/log forensics, post-breach evidence | `references/threat-analysis.md` |
| 4 | **Human & Attack Vectors** | Phishing messages, social engineering scenarios, awareness checks | `references/social-engineering.md` |
| 5 | **Defense & Countermeasures** | Patching plans, incident remediation, OPSEC and privacy review | `references/remediation.md` |

## How it works

`SKILL.md` contains the routing logic that picks the right file (or files) for a task before analysis starts. A task that spans two domains — a confirmed vulnerability that now needs a remediation plan — reads both files.

---

## Output format

Every finding follows a consistent shape:

```json
{
  "id": "F-2026-0001",
  "title": "Internet-exposed MySQL instance",
  "analysis_domain": "reconnaissance",
  "evidence": "Port 3306 open on 203.0.113.12, reachable from the internet",
  "impact": "Database accessible without VPN or firewall restriction",
  "confidence": "high",
  "cwe": [],
  "mitre_attck": [],
  "cvss": "",
  "remediation": "Restrict to internal network or VPN; enforce least-privilege on DB accounts",
  "verification_steps": [
    "Confirm port is closed from an external scanning service",
    "Confirm application connectivity from inside the network"
  ]
}
```

The schema lives in `schemas/finding.schema.json`. Validate a finding against it:

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
| `tooling/compute_hash.py <file>` | SHA-256 a file for use in IOC records |
| `tooling/validate_stix.py <file.json>` | Parse and validate a STIX 2.1 JSON file |
| `tooling/run_yara_tests.sh` | Run YARA rules against `examples/` if `yara` is installed |

```bash
# hash a suspicious file before analysis
python tooling/compute_hash.py /path/to/sample.bin

# validate a STIX export
python tooling/validate_stix.py exports/indicators.json
```

---

## Repository layout

```
Security-Analyst/
├── SKILL.md                        routing logic, tool definition, classification standards
├── references/
│   ├── reconnaissance.md
│   ├── vulnerability-analysis.md
│   ├── ai-generated-code.md
│   ├── threat-analysis.md
│   ├── social-engineering.md
│   └── remediation.md
├── schemas/
│   └── finding.schema.json         JSON Schema (draft-07) for structured findings
├── templates/
│   ├── finding_template.md
│   └── remediation_checklist.md
├── examples/
│   ├── finding_example.json
│   └── nmap_samples/
├── tooling/
│   ├── compute_hash.py
│   ├── validate_stix.py
│   └── run_yara_tests.sh
├── analysis-docker/
│   └── Dockerfile                  isolated analysis environment
└── tests/
    ├── test_docs.py
    └── test_schema.py
```

---

## Running in Docker

For analyzing untrusted samples, run inside the isolated environment:

```bash
docker build -t security-analyst analysis-docker/
docker run --rm -v "$(pwd)":/workspace security-analyst \
  python tooling/compute_hash.py /workspace/sample.bin
```

---

## Scope

Analytical and defensive. The output is analysis, classification, and remediation guidance — not working exploit code, ready-to-deploy payloads, or offensive tooling. Where that line sits and why is in `SKILL.md` under "Scope and Boundaries."

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Run the test suite before opening a PR:

```bash
python -m unittest discover -s tests -v
```

---

## License

MIT — see [LICENSE](LICENSE).
