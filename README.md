# Security Analyst Skill

A cybersecurity analysis skill for any AI model or agent. Covers six domains — reconnaissance, vulnerability analysis, AI-generated code review, threat and malware analysis, social engineering, and remediation — each backed by a reference file grounded in established methodology.

## What it covers

| Domain | Use it for | Reference |
| --- | --- | --- |
| **Reconnaissance & OSINT** | Nmap/Shodan/Sublist3r output, attack-surface mapping | `references/reconnaissance.md` |
| **Vulnerability & Exploit Logic** | Code review, CVE triage, crash dumps, assembly | `references/vulnerability-analysis.md` |
| **AI-Generated Code Review** | Code written by a chat assistant, IDE autocomplete, or agent | `references/ai-generated-code.md` |
| **Threat & Binary Analysis** | Suspicious files, process/log forensics, post-breach evidence | `references/threat-analysis.md` |
| **Human & Attack Vectors** | Phishing messages, social engineering scenarios, awareness checks | `references/social-engineering.md` |
| **Defense & Countermeasures** | Patching plans, incident remediation, OPSEC and privacy review | `references/remediation.md` |

## How it works

Each domain maps to a reference file that explains how to reason through the problem, what to look for, how to classify findings, and what output to produce. The routing logic in `SKILL.md` picks the right file (or files) for a given task before analysis starts.

For multi-domain tasks — a vulnerability confirmed in a code review that now needs a remediation plan — read both files.

## File structure

```
Security-Analyst/
├── SKILL.md
├── references/
│   ├── reconnaissance.md
│   ├── vulnerability-analysis.md
│   ├── ai-generated-code.md
│   ├── threat-analysis.md
│   ├── social-engineering.md
│   └── remediation.md
├── schemas/
│   └── finding.schema.json
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
│   └── Dockerfile
└── tests/
    ├── test_docs.py
    └── test_schema.py
```

## Installation

**Claude (claude.ai projects):** drop the `Security-Analyst/` folder into your project's skills directory.

**Other agent frameworks** (LangChain, Semantic Kernel, MCP, direct API): use the tool definition in `SKILL.md` under "Tool Definition" and pass the relevant `references/` files as context or system instructions.

## Running the checks

```bash
pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

## Scope

Analytical and defensive. The output is analysis, classification, and remediation guidance — not working exploit code, ready-to-deploy payloads, or offensive tooling. The reasoning for where that line sits is in `SKILL.md` under "Scope and Boundaries."

## License

MIT — see `LICENSE`.
