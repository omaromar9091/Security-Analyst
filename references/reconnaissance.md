# Reconnaissance & OSINT

Use this file before vulnerability or threat analysis, when the task starts with raw scan output — Nmap, Shodan, Sublist3r, or similar — or open-source information gathering, and the goal is mapping an attack surface before deciding what to look at more closely.

This assumes the activity is authorized and within a defined scope, such as an approved penetration test, a bug bounty program, or an organization reviewing its own exposure. Check scope and rules of engagement before follow-up testing. This guide focuses on interpreting and prioritizing results, not on scanning third-party systems without permission.

## Reading Scan Output

### Port and Service Scans

Open ports and banners point to running services, often down to the exact version, which narrows down which known vulnerabilities to check first. An outdated or end-of-life version is a priority lead, not just a data point to note in passing.

Unexpected open ports — a database port reachable from outside the internal network, a management interface facing the internet — are usually a bigger finding on their own than whatever specific vulnerability might exist in the service behind them. The exposure itself is the issue.

OS fingerprinting narrows the field of likely vulnerabilities and which techniques even apply, but it's a hint, not a certainty. Hardened or deliberately obscured systems throw it off regularly.

### Internet-Facing Asset Discovery

Shodan-style results turn up devices and services never meant to be reachable from the internet — exposed industrial control systems, unauthenticated admin panels, misconfigured cloud storage, forgotten test servers. The first thing worth flagging is usually "this shouldn't be reachable at all," before even getting into what's running on it.

Banner and metadata fields — server headers, default credentials still sitting there, certificate details — often reveal the organization behind an asset without any further lookup, which matters for scoping and for tracing a given exposure back to a real business unit.

### Subdomain Enumeration

A large subdomain list is usually a mix of production, staging, and abandoned infrastructure. Staging and forgotten subdomains carry weaker controls more often than not — default credentials, outdated software, debug endpoints left switched on — and deserve a look before the well-maintained production domains do.

Naming patterns like dev-, test-, old-, or internal- are a fast way to triage which ones to check first. Cross-referencing against certificate transparency logs and DNS records catches assets that a single enumeration pass missed.

## Organizational and Human-Layer OSINT

Job postings, LinkedIn profiles, and public documentation often leak internal tool names, team structure, and tech stack — all of it useful for building a more convincing social engineering pretext later (see `references/social-engineering.md`).

Public reporting and reputable breach-notification services may indicate that organizational credentials were exposed. Do not download or redistribute raw credential dumps, and never test exposed credentials against live services. Treat a reported exposure as a lead: notify the authorized security owner, use approved breach-monitoring channels, and arrange password resets, session revocation, and MFA review through the normal incident process.

Metadata buried in public documents — author names, software versions, internal file paths — can say more about internal infrastructure than the document's actual content does.

## Turning Recon Into a Prioritized Target List

1. Group what was found by exposure type: unauthenticated access, outdated software, unexpected reachability, leaked credentials, human-layer intelligence.
2. Rank by a rough cost-versus-impact estimate, not by how interesting something looks. An unauthenticated admin panel on a low-value internal tool can matter less than a slightly outdated library on a system that touches customer data.
3. Separate confirmed exposures from leads that need verification. An internet-exposed database may be a finding on its own; a third-party report of leaked credentials needs careful validation and incident handling, not credential testing.
4. Hand the prioritized list to `references/vulnerability-analysis.md` or `references/threat-analysis.md` depending on whether the next step is code and configuration, or something already running.

## When Explaining This to a User

Summarize what the data actually exposes and why it matters, in priority order, rather than listing every open port and subdomain with equal weight. Keep anything that's a finding by itself separate from leads that still need confirming.

## Worked Example

**Input**: An Nmap scan of a client's external range shows port 3306 (MySQL) open on a host. A Sublist3r run turns up staging-api.client.com, which isn't in the production DNS zone.

**Analysis**: A database port open to the internet is a significant finding on its own, independent of whatever vulnerabilities might exist in the database behind it — this kind of service was never meant to be internet-facing to begin with. The staging subdomain is a secondary lead: staging environments routinely run weaker than production, and it's not yet clear whether this one's still in active use or just forgotten.

**Output**: Priority finding: MySQL reachable directly from the internet. Flag and remediate this — restrict to internal network or VPN access — regardless of whether a specific database vulnerability ever turns up. Secondary lead: check staging-api.client.com for weaker controls than production, default credentials, verbose errors, missing authentication, before deciding whether it needs a deeper code-level look.
