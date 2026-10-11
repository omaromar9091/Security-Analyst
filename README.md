# Security Analyst Skill

A cybersecurity analysis skill for any AI model or agent, covering six areas: reconnaissance and OSINT, code vulnerability analysis, AI-generated code review, threat and malware analysis, social engineering, and defense/remediation planning.

## Usage

Works with anything that supports the general idea of "skills" or tool/function calling.

For Claude, drop the whole `security-analyst/` folder into the skills directory for the project or account. For any other agent framework — LangChain, Semantic Kernel, MCP, or a direct integration — use the tool definition in `SKILL.md` under "Tool Definition" and feed the `references/` files in as context or system instructions.

## File Structure

```
security-analyst/
├── SKILL.md                          # Overview, approach, tool definition, routing, classification standards
└── references/
    ├── reconnaissance.md             # OSINT and attack-surface mapping (Nmap/Shodan/Sublist3r)
    ├── vulnerability-analysis.md     # Code vulnerabilities, exploit logic, crash/assembly triage
    ├── ai-generated-code.md          # Review patterns specific to AI-written/AI-assisted code
    ├── threat-analysis.md            # Suspicious file/behavior analysis, forensics, YARA/IOC output
    ├── social-engineering.md         # Social engineering and phishing assessment
    └── remediation.md                # Patching, defense, operational security, OPSEC data-handling review
```

## Scope

Built to support security decisions — reviewing code, classifying threats, spotting social engineering, planning remediation. Not a tool for generating ready-to-use exploits or malware; the limits on that are in `SKILL.md`.

## License

MIT License, see `LICENSE`.
