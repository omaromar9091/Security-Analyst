# Threat & Binary Analysis

Use this file for analyzing a suspicious file or process, system logs with unusual activity, or pulling together evidence after a breach.

## Stages of Analyzing a Suspicious File

### Static Analysis

Looking at the file without running it.

**Hash and signature**: computing MD5/SHA-256 and checking it against known databases like VirusTotal is a fast first step, but a new or lightly modified file will often slip past known signatures entirely.

**Strings and embedded resources**: pulling the readable text out of a file. IP addresses, domain names, file paths, error messages — these hint at what the file actually does before any deeper work starts.

**File structure**: checking headers (PE headers on Windows) for signs of packing or encryption, a common way malware authors hide the real payload from anything scanning the file at rest.

**Imported API calls**: what a file imports says a lot about what it can do. Network functions, registry-writing calls, process injection functions — all of these point toward expected behavior before the file ever runs.

### Dynamic Analysis

Running the file in an isolated sandbox and watching what happens.

File activity: what gets created, modified, or deleted, and where — system folders and startup folders matter most. Registry activity on Windows: autorun keys, security tools getting disabled, settings changing. Network activity: outbound connections, which addresses and domains it talks to, and whether the pattern looks periodic, one-shot, or like it's waiting for an instruction. Persistence: how it survives a reboot — scheduled tasks, services, startup keys. Evasion: whether it checks for analysis tools or a virtual environment before doing anything, or just delays execution to dodge automated scanning.

## Producing Machine-Usable Output

A written description of indicators is useful for a person reading it, but a detection signature or a structured record is what actually plugs into a SIEM or an endpoint tool. Once the analysis has turned up concrete indicators, produce both of these.

A YARA rule, built from whatever's distinctive about the file — specific strings, byte sequences, or a combination with size or a hash. Keep it tight enough that it won't flag unrelated files:

```
rule example_observed_string_only
{
    meta:
        description = "Detects sample based on a string observed during analysis"
        date = "2026-10-17"

    strings:
        $observed = "observed-c2-domain-or-string" ascii

    condition:
        $observed
}
```

Swap in whatever was actually observed during analysis. Never make up an indicator that wasn't actually seen in the sample.

And a structured IOC record, STIX/TAXII-style:

```json
{
  "type": "indicator",
  "spec_version": "2.1",
  "id": "indicator--a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "created": "2026-10-17T00:00:00Z",
  "modified": "2026-10-17T00:00:00Z",
  "pattern": "[file:hashes.'SHA-256' = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa']",
  "pattern_type": "stix",
  "valid_from": "2026-10-17T00:00:00Z",
  "indicator_types": ["malicious-activity"],
  "labels": ["c2", "persistence"],
  "description": "Replace hash and description with values observed in the actual sample. The id must be a valid UUIDv4 prefixed with indicator--."
}
```

Fill this in with the real hash, IP, domain, and observed behavior — it's meant to be ingested by a SIEM or threat intel platform, so accuracy beats completeness. Leave a field out rather than padding it with a placeholder.

## Gathering Evidence After an Incident

1. Preserve state before touching anything else: a memory dump and a disk image where that's possible, before anyone restarts or cleans an affected machine.
2. Build a timeline — when the suspicious activity first showed up, and what happened right before and right after.
3. Work out the likely initial entry point: an email, a link, a vulnerability in an exposed service, stolen credentials.
4. Scope the impact: which other machines or accounts touched the affected system or show the same indicators.
5. Pull together indicators of compromise — hashes, IPs, domains, file paths, registry keys — to check for other infections elsewhere.

## When Explaining This to a User

Classify what was observed — data theft, persistence, lateral movement, ransomware — and lay out the indicators that led to that call. Containment comes first in whatever you suggest: isolate the machine, rotate affected credentials, block the indicators on the network, before anything permanent.

## Worked Examples

**Input**: A workstation log shows an unfamiliar executable in `%AppData%` creating a scheduled task that runs at every login, followed by outbound connections to an IP address every 60 seconds.

**Analysis**: A scheduled task tied to login is a standard persistence move — it survives a reboot and needs nothing from the user to fire again. The fixed 60-second outbound connection fits a command-and-control beacon checking in, not normal application traffic, which tends to be bursty rather than metronomic. Together, these two point to malware with C2 already established on the host, not a one-off infection that's run its course.

**Output**: Classification: likely C2-beaconing malware with persistence through a scheduled task. ATT&CK: T1053 (Scheduled Task/Job) for persistence, T1071 (Application Layer Protocol) for the C2 channel. Immediate steps: isolate the host to cut the C2 connection, grab a memory image before touching anything else, and pull the executable's hash plus the destination IP to check against other machines. Leave the scheduled task and the file in place for now — they're evidence before they're cleanup.



---

**Input**: Antivirus flags a file as unknown, no signature match. Static analysis shows the PE header has an unusually high-entropy section and almost no readable strings for a file of that size.

**Analysis**: High entropy paired with barely any readable strings is a solid packing or encryption signal — the actual code and strings are compressed or encrypted and only unpack at runtime, which is exactly why a signature scanner came up empty. That alone doesn't prove the file is malicious, but it's enough reason to move to a sandbox rather than clear it on the strength of a clean AV scan.

**Output**: Classification: inconclusive from static analysis alone, but packed or encrypted in a way that's consistent with evasion. Next step: detonate it in an isolated sandbox and watch the runtime file, registry, and network behavior instead of trusting the static result. "No detections" on a packed binary isn't a clean bill of health; it's a reason to dig further.

---

**Input**: Post-incident review of a ransomware case. Files across a shared drive got encrypted overnight. The only account active during that window was a service account that normally just runs a nightly backup job.

**Analysis**: A service account acting outside its normal job — encrypting files instead of running a backup — points to compromised credentials being used directly, not malware independently escalating privileges on its own. The timing lines up with the backup job's usual schedule, which suggests the attacker either knew the schedule going in or rode the account's existing access window to avoid tripping any anomaly alert tied to odd login times.

**Output**: Classification: ransomware deployed through a compromised service account, not a privilege escalation exploit. Immediate steps: disable the account's credentials, figure out how they were obtained — exposed secrets, phishing against whoever manages the account, reused passwords — and check whether the same credentials open any other doors before rebuilding from backup.
