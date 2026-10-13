<img src="banner.svg" alt="Security Analyst" width="100%">

# Security Analyst

[![License: MIT](https://img.shields.io/badge/license-MIT-E8A33D.svg)](LICENSE)
[![Framework agnostic](https://img.shields.io/badge/framework-agnostic-3E6B89.svg)](SKILL.md)
[![Analysis domains](https://img.shields.io/badge/analysis%20domains-6-141C26.svg)](SKILL.md)

Security Analyst is a reference-driven skill for AI assistants doing defensive cybersecurity work. It covers six analysis domains and provides a consistent way to route a request, assess the available evidence, describe risk, and recommend practical next steps. It is designed to support an analyst's judgment, not replace testing or turn uncertain observations into confirmed findings.

## What it covers

| Domain | Typical use cases | Guide |
| --- | --- | --- |
| **Reconnaissance and OSINT** | Interpret authorized scan results, map exposed assets, prioritize public-facing services, and handle public-source intelligence carefully. | [`references/reconnaissance.md`](references/reconnaissance.md) |
| **Vulnerability analysis** | Review application code and architecture, examine known weaknesses, and triage crashes or potential exploitability. | [`references/vulnerability-analysis.md`](references/vulnerability-analysis.md) |
| **AI-generated code review** | Look for missing controls, unsafe defaults, questionable dependencies, hardcoded secrets, and prompt-injection risks in AI-assisted code. | [`references/ai-generated-code.md`](references/ai-generated-code.md) |
| **Threat and binary analysis** | Assess suspicious files and activity, organize incident evidence, and draft candidate detection indicators. | [`references/threat-analysis.md`](references/threat-analysis.md) |
| **Social-engineering assessment** | Evaluate phishing, vishing, pretexting, business email compromise, and authorized awareness exercises. | [`references/social-engineering.md`](references/social-engineering.md) |
| **Defense and remediation** | Prioritize fixes, plan containment and recovery, improve hardening, and review privacy and data-handling practices. | [`references/remediation.md`](references/remediation.md) |

## How it works

1. **Route the request.** Choose the reference that matches the evidence and the decision that needs to be made. Consult more than one guide when a case spans domains.
2. **Assess the evidence.** Separate observed facts from interpretation and assumptions. Identify what is known, what remains uncertain, and what evidence would resolve the uncertainty.
3. **Explain the risk.** Describe the realistic impact and relevant preconditions rather than relying on a vulnerability label alone.
4. **Recommend a fix.** Give concrete remediation steps and a way to verify the result. Call out operational side effects when they matter.
5. **Classify only when justified.** Use CWE for supported software weaknesses, MITRE ATT&CK for adversary behavior that actually fits a technique, and CVSS when enough context is available to assess a specific vulnerability. Do not force a mapping or invent a score to make a report look complete.

The reference guides include worked examples to illustrate the expected reasoning and level of detail. Their indicators, severity descriptions, and snippets are examples—not validated detections or substitutes for testing in the target environment.

## Use the skill

The repository contains a `SKILL.md` entry point and supporting material in `references/`.

- **Skill-compatible assistants:** Install or add the complete project directory according to the skill mechanism supported by your assistant. Keep `SKILL.md` and the `references/` directory together so the routing instructions can resolve the linked guides.
- **Other agent frameworks:** Adapt the routing and reference material to your framework. `SKILL.md` includes a framework-neutral function schema that can be used as a starting point; it is not a ready-made integration or an executable security scanner.
- **Manual use:** Open the relevant reference and follow its checklist, evidence standards, and remediation guidance.

No particular model, agent framework, scanner, sandbox, or threat-intelligence service is bundled with this repository. Any external tool must be configured and used separately, within an authorized scope.

## Repository layout

```text
Security-Analyst/
├── SKILL.md
├── README.md
├── LICENSE
├── banner.svg
├── references/
│   ├── reconnaissance.md
│   ├── vulnerability-analysis.md
│   ├── ai-generated-code.md
│   ├── threat-analysis.md
│   ├── social-engineering.md
│   └── remediation.md
└── tests/
    └── test_docs.py
```

## Scope and responsible use

Use this material for defensive analysis, systems you own, or assessments you are explicitly authorized to conduct. It does not grant permission to scan or test third-party systems. Suspicious files should be examined in an isolated lab, and sensitive samples or credentials should not be sent to public services without approval. The skill is designed to explain risks and support safe validation; it is not intended to generate deployable malware or working exploit chains against real targets.

AI-assisted analysis can miss issues or misinterpret evidence. Validate important findings with the relevant source material, tools, and qualified reviewers before making high-impact decisions.

## Validation

The documentation checks use Python's standard library and require no third-party packages:

```bash
python -m unittest discover -s tests -v
```

These checks validate repository consistency and example formatting. They do not prove that a security conclusion, YARA rule, STIX indicator, or remediation is correct for a real environment.

## License

This project is distributed under the MIT License. See [`LICENSE`](LICENSE).
