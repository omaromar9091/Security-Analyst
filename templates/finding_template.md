# Finding template

Use this template to capture a security finding in a consistent, machine-friendly way. Prefer JSON output when integrating with other tools.

Required fields:
- id
- title
- analysis_domain
- evidence
- impact
- confidence (low|medium|high)
- remediation

Example (JSON):

```json
{
  "id": "F-2026-0001",
  "title": "Internet-exposed MySQL instance",
  "analysis_domain": "reconnaissance",
  "evidence": "Nmap shows port 3306 open on host 203.0.113.12",
  "impact": "Database accessible from the internet could allow data exposure",
  "confidence": "high",
  "cwe": [],
  "mitre_attck": [],
  "cvss": "",
  "remediation": "Restrict access to internal network or VPN; enforce least-privilege rules on DB accounts",
  "verification_steps": [
    "Confirm port is closed from internet using an external scanning service",
    "Confirm application connectivity from inside the network"
  ]
}
```
