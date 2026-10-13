# Threat and Binary Analysis

Use this guide to assess a suspicious file or process, interpret unusual system activity, or organize evidence after a suspected compromise. Treat conclusions as provisional until they are supported by multiple observations where possible.

## Static Analysis

Start with non-executing checks whenever practical.

- **Hashes and reputation:** Calculate a SHA-256 hash and compare it with approved internal or reputable intelligence sources. A reputation lookup is one signal, not a verdict; a new or modified sample may have no detections. Do not upload confidential, regulated, or otherwise sensitive files to a public scanning service without authorization.
- **Strings and resources:** Review readable strings, embedded resources, file paths, domains, and error messages. Treat these as leads: strings can be decoys, stale artifacts, or unrelated library content.
- **File structure:** Inspect headers, sections, signing information, and entropy. Packing or high entropy can be consistent with compression or encryption, but is not proof of malware.
- **Imports and capabilities:** Review imported functions and metadata for capabilities such as network communication, process manipulation, or persistence. A capability does not prove that the file uses it maliciously.

## Dynamic Analysis

Run a suspicious sample only in a disposable, isolated analysis environment controlled by an authorized analyst. Prefer a snapshot that can be reverted. Do not use a normal workstation, production credentials, sensitive shared folders, or unrestricted network access. If network behavior must be observed, use a controlled simulation or tightly monitored lab network with explicit approval.

Record what the sample actually does:

- Files and directories created, modified, or removed.
- Registry changes, services, scheduled tasks, and other persistence mechanisms.
- Process creation, child processes, privilege changes, and security-tool interference.
- DNS requests and network connections, including timestamps and destinations.
- Attempts to detect a debugger, virtual machine, or analysis environment.

A sandbox run that shows no suspicious activity does not prove a sample is safe; behavior may depend on time, configuration, user activity, or unavailable infrastructure.

## Writing Detection Content

Detection content should be based on indicators observed during analysis. Mark examples as illustrative, test them against both known-positive and known-negative samples, and document expected false positives. Do not deploy a rule solely because it appears in this guide.

### YARA example

This rule is a template. Replace the example string with a stable, distinctive string actually observed in the sample. The `.invalid` domain is reserved for examples and is not a real indicator.

```yara
rule example_observed_string_only
{
    meta:
        description = "Illustrative template; replace with a validated sample-specific indicator"
        reference = "Documentation example only"

    strings:
        $observed = "sample-marker.example.invalid" ascii wide nocase

    condition:
        $observed
}
```

The string above is deliberately not a useful production signature. A generic file header such as `MZ` is not distinctive enough on its own. Before deployment, run the rule against a representative benign corpus, relevant known-positive samples, and the expected scanning locations. Review performance and false-positive rates.

### STIX 2.1 indicator example

The following is a structurally complete STIX 2.1 Indicator object for documentation purposes only. Its all-zero hash is a dummy value, not a real IOC. Replace the ID, timestamps, hash, and description with verified case data before use. Keep separate indicators for unrelated observables unless the relationship between them is supported by evidence.

```json
{
  "type": "indicator",
  "spec_version": "2.1",
  "id": "indicator--11111111-1111-4111-8111-111111111111",
  "created": "2026-10-09T00:00:00Z",
  "modified": "2026-10-09T00:00:00Z",
  "name": "Documentation example - replace before use",
  "description": "Illustrative object only; not a verified indicator.",
  "indicator_types": ["malicious-activity"],
  "pattern": "[file:hashes.'SHA-256' = '0000000000000000000000000000000000000000000000000000000000000000']",
  "pattern_type": "stix",
  "valid_from": "2026-10-09T00:00:00Z"
}
```

Use a STIX 2.1 validator and the receiving platform's schema checks before ingesting generated objects. Do not label an indicator as malicious unless the evidence supports that label. Follow the organization's data-sharing and marking rules when exporting threat intelligence.

## Evidence Handling After an Incident

1. Follow the incident-response plan and preserve evidence before making changes when doing so will not prolong active harm. Capture relevant logs, volatile data, and disk images where authorized and feasible.
2. Record a timeline with time zones and note the source of each timestamp.
3. Identify plausible entry points, but distinguish confirmed evidence from hypotheses.
4. Determine scope by checking related systems, accounts, identities, and indicators.
5. Preserve hashes, paths, domains, IP addresses, task names, and other relevant indicators with provenance and collection time.
6. Maintain chain-of-custody records where evidence may be used for legal, regulatory, or disciplinary purposes.

Containment may need to happen before complete collection when active damage is ongoing. Explain the trade-off and follow the organization's incident lead rather than delaying urgent containment for ideal evidence collection.

## Reporting

State the observed behavior, the evidence supporting the assessment, the confidence level, and what remains unknown. Recommend proportionate containment and validation steps. Do not treat an indicator match as conclusive attribution or proof that every host with the same indicator is compromised.

Map behavior to MITRE ATT&CK only when the observed behavior fits a technique. A suspicious file or a hash match alone is not enough to claim a specific adversary technique. Use CVSS only when assessing a specific vulnerability and when the required context is available; it is not a general malware severity score.

## Worked Examples

**Input:** Endpoint telemetry shows an unfamiliar executable under a user's profile creating a logon-triggered scheduled task, followed by outbound connections to the same external address at roughly 60-second intervals.

**Analysis:** The scheduled task is evidence of persistence, and the repeated outbound connections may indicate beaconing. Neither observation alone proves command-and-control; confirm the process-to-connection relationship, destination reputation, and surrounding activity. Preserve the executable and relevant telemetry before cleanup if incident procedures permit.

**Output:** Assessment: suspicious activity with possible scheduled-task persistence and periodic outbound communication. Confidence: moderate pending process and destination validation. Immediate actions: isolate the host if active compromise is reasonably suspected, preserve relevant evidence, identify the executable's SHA-256 hash, and check for related activity elsewhere. ATT&CK: T1053.005 (Scheduled Task) is a candidate mapping if the task's persistence role is confirmed; map the network behavior only after confirming its purpose. Do not infer an ATT&CK technique from timing alone.

---

**Input:** Antivirus reports no detections for an unknown executable. Static inspection finds a high-entropy PE section and very few readable strings.

**Analysis:** Those properties can be consistent with packing or encryption, but can also occur in legitimate software. A clean antivirus result and high entropy are both inconclusive on their own.

**Output:** Assessment: unresolved; additional analysis is warranted. Next step: inspect signing and provenance, compare metadata with a trusted release, and—if authorized—run the file in an isolated lab with controlled networking. Do not describe the file as malware unless additional evidence supports that conclusion.

---

**Input:** A shared drive was encrypted overnight. Audit logs show a service account used outside its normal backup activity during the same period.

**Analysis:** The account's unusual activity is relevant, but logs alone may not establish whether its credentials were stolen, whether malware used the account, or whether the account was the initial entry point.

**Output:** Assessment: suspected ransomware incident with anomalous service-account use. Contain affected systems, disable or rotate the account through the incident process, preserve relevant logs, and check for other persistence and compromised identities before recovery. Restore only from backups confirmed to predate the compromise, and validate the environment before returning it to service.
