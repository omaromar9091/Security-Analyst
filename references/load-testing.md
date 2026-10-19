# Load Testing & Performance Analysis

## Purpose

This domain covers measuring how a system — a web application, API, microservice, database, or any networked service — behaves under controlled traffic load. The goal is to find performance ceilings, failure points, and degradation patterns before they appear in production.

This is a measurement discipline, not an attack technique. Every test in this domain runs against a target the tester owns or has written authorization to test.

## When to use this file

- Validating that a new service can handle expected peak traffic before launch
- Finding the point at which response times degrade or errors begin
- Comparing performance before and after a code change or infrastructure upgrade
- Sizing infrastructure: how many instances, how much memory, what database connection pool
- Satisfying an SLA requirement that mandates a minimum throughput or maximum latency

## Authorization requirement

**No test runs without a written scope statement.** At minimum, document:

- Target URL or host/port
- Who owns the target and who authorized the test
- Maximum request rate the test is allowed to generate
- Date and time window for the test
- Contact person on the target system's team

Running a load test against a system you do not own, or without written authorization from someone who does, is illegal in most jurisdictions regardless of intent. The tooling in this repository enforces this by requiring `--authorized-by` on the command line.

---

## Test types and when to use them

### Baseline test

Send a low, constant load for a short period. Establishes the system's normal behavior — response times, error rate, resource usage — before any stress is applied. Always run this first.

Typical shape: 5–10 concurrent users, 2–3 minutes.

### Load test

Gradually increase traffic to the expected peak level and hold it there. Measures whether the system meets its SLA under realistic conditions.

Typical shape: ramp from 0 to target concurrency over 5 minutes, hold for 10–15 minutes.

### Stress test

Push traffic beyond the expected peak to find the breaking point. The question is not whether the system fails — it will — but how it fails: gracefully (returns errors, stays responsive) or catastrophically (crashes, corrupts data, stops responding entirely).

Typical shape: ramp up until error rate exceeds 5% or latency exceeds the SLA ceiling.

### Spike test

Apply a sudden large increase in traffic, hold briefly, then drop back. Simulates a flash sale, a viral event, or a sudden burst of legitimate users. Tests whether the system can absorb a shock and recover.

Typical shape: jump from baseline to 5–10× normal in seconds, hold for 1–2 minutes, return to baseline.

### Soak test (endurance test)

Run at moderate load for a long period — hours or overnight. Finds problems that only appear over time: memory leaks, connection pool exhaustion, log file growth, certificate expiry edge cases, accumulated database locks.

Typical shape: 60–80% of peak load, 4–24 hours.

---

## Metrics to collect

Collect all of these; a finding based on only one metric is incomplete.

**Latency (response time)**
- P50, P95, P99 — the median is not enough; tail latency is what users experience at scale
- Time to First Byte (TTFB) separately from total response time when serving large payloads
- A P99 above the SLA threshold is a finding even if P50 looks fine

**Throughput**
- Requests per second (RPS) actually delivered
- Compare against the intended rate — a gap means the client itself or the network is the bottleneck, not the server

**Error rate**
- HTTP 5xx rate: server errors
- HTTP 4xx rate: watch for unexpected spikes (rate limiting, auth failures under load)
- Connection errors, timeouts, and DNS failures — log these separately from HTTP errors

**Resource utilization (server side)**
- CPU: sustained above 80% is a risk; at 100% the system is likely dropping requests
- Memory: watch for steady growth across the test duration (memory leak)
- Open file descriptors and network connections: exhaustion causes silent failures
- Database: connection pool usage, query latency, lock wait time

**Saturation point**
- The concurrency level or RPS at which latency starts increasing non-linearly
- Usually visible as an inflection point on a latency-vs-concurrency graph

---

## What good results look like

A healthy system under load shows:

- Latency that rises gradually and predictably as concurrency increases
- Error rate below 0.1% at expected peak load
- CPU and memory that plateau rather than grow continuously
- Clean recovery to baseline metrics after load drops
- No cascading failures: one slow component should not take down unrelated services

A system that needs attention shows:

- Latency that spikes sharply at a concurrency level well below expected peak
- Error rate above 1% at expected peak, or any 5xx errors at baseline
- Memory that grows throughout the test and does not return to baseline after load drops
- Timeouts or connection resets that do not appear in the server's own error logs (network-layer failures)
- Long recovery time after load drops — the system stays degraded

---

## Interpreting bottlenecks

**High CPU, low latency increase**: the system is compute-bound. Optimise hot code paths or add CPU capacity.

**Low CPU, high latency increase**: likely I/O bound — database, external API calls, or disk. Profile slow queries and slow external dependencies.

**Memory growing throughout test**: memory leak. Find it with heap profiling; do not mask it by adding RAM.

**Error rate spikes then recovers**: circuit breaker or retry storm. Review retry logic; add exponential backoff.

**Error rate grows steadily**: resource exhaustion. Check connection pool limits, file descriptor limits, thread pool size.

**Latency fine, throughput lower than expected**: the test client or network is the bottleneck, not the server. Run the client closer to the target, or use a distributed load generator.

---

## Infrastructure types and considerations

### HTTP/HTTPS web applications and APIs

Standard target. Measure at the application layer. Verify that TLS termination is not the bottleneck (common on underpowered load balancers). Test authenticated and unauthenticated endpoints separately.

### Cloud-hosted services (AWS, Azure, GCP, etc.)

Auto-scaling changes the analysis: the system may handle load by adding instances rather than by failing. Test whether auto-scaling activates within the required time window, and what happens during the scale-out period. Watch for cost implications — a load test can run up a significant cloud bill if not time-limited.

### Microservices / service meshes

Test each service individually first, then test the full call graph. Cascade failures are common: one slow upstream service causes timeouts in every downstream caller. Introduce artificial latency into dependencies (fault injection) to test resilience.

### Databases

Test the connection pool limit explicitly. Most applications fail not because the database is slow but because available connections are exhausted. Measure query latency under concurrent load, not just under single-connection benchmarks.

### Local / on-premise applications

Network is not a variable — focus on CPU, memory, and disk I/O. Test with the test client on a separate machine even on a LAN to avoid resource contention with the target.

### WebSocket and long-lived connections

Concurrency model differs from HTTP request/response. Measure connection establishment time, message latency, and maximum simultaneous open connections rather than requests per second.

---

## Output format

Each load test produces a finding in the standard schema. Fill in:

- `analysis_domain`: `"load_testing"`
- `evidence`: quantitative results — P50/P95/P99 latency, peak RPS, error rate, resource utilization at peak
- `impact`: what breaks or degrades in production if this finding is not addressed
- `confidence`: `"high"` when results are reproducible across multiple runs; `"medium"` for a single run; `"low"` if the test environment differed significantly from production
- `remediation`: specific, actionable steps — not "improve performance" but "increase database connection pool from 10 to 50, add read replica for reporting queries"

---

## Worked examples

### Example 1 — Web API latency spike under moderate load

**Input**

```
Target: https://api.example.com/v1/search  (owned and authorized by: Jane Smith, Head of Engineering)
Test type: load test
Concurrency ramp: 1 → 50 users over 5 min, hold 10 min
Results:
  P50 latency: 120 ms (baseline: 95 ms)
  P95 latency: 4,200 ms (baseline: 180 ms)
  P99 latency: 12,000 ms (baseline: 310 ms)
  Error rate: 0.8% (all HTTP 504 Gateway Timeout)
  Peak RPS delivered: 340
  Server CPU: 45% average
  Server memory: stable at 2.1 GB
  Database connection pool: 10/10 in use (pool exhausted at ~30 concurrent users)
```

**Analysis**

CPU and memory are not the constraint. The database connection pool exhausted at approximately 30 concurrent users — well below the 50-user test target. Once the pool was full, new requests queued and eventually timed out (504s). The P95 and P99 latency spike is consistent with queuing delay rather than slow query execution. This is a configuration finding, not a code defect.

**Output**

```json
{
  "id": "LT-2026-0001",
  "title": "Database connection pool exhaustion at 30 concurrent users",
  "analysis_domain": "load_testing",
  "evidence": "P95 latency rose from 180 ms to 4,200 ms as concurrent users exceeded 30. Pool size is 10; all 10 connections were in use at the inflection point. HTTP 504 error rate 0.8% at 50 concurrent users. CPU 45%, memory stable — server resources not constrained.",
  "impact": "Any traffic spike above ~25 concurrent active searches will cause visible latency degradation and a proportion of timeouts. Current peak production traffic (Black Friday estimate: 80 concurrent) would cause widespread user-facing errors.",
  "confidence": "high",
  "cwe": [],
  "mitre_attck": [],
  "cvss": "",
  "remediation": "Increase database connection pool size to 50 (matches expected peak concurrency with headroom). Add a read replica and route search queries there to separate read load from write load. Set a connection acquire timeout of 2 seconds and return a 503 with Retry-After rather than queuing indefinitely.",
  "verification_steps": [
    "Re-run the 50-user load test after pool size increase",
    "Confirm P95 latency stays below 500 ms at 50 concurrent users",
    "Confirm error rate drops below 0.1%",
    "Verify pool utilization metric is visible in monitoring dashboard"
  ]
}
```

---

### Example 2 — Memory leak found in soak test

**Input**

```
Target: http://10.0.1.25:8080 (internal staging server, authorized by: DevOps team lead)
Test type: soak test
Load: 20 concurrent users (60% of expected peak), 6 hours
Results:
  P50 latency: stable at 85 ms throughout
  Error rate: 0% throughout
  CPU: stable at 22%
  Memory at test start: 512 MB
  Memory at 2 hours: 780 MB
  Memory at 4 hours: 1,050 MB
  Memory at 6 hours: 1,380 MB
  Server did not crash; test ended before OOM
```

**Analysis**

Latency and error rate were healthy throughout, which would pass a short load test. Memory grew linearly at approximately 145 MB per hour with no plateau. At this rate the server would exhaust its 2 GB limit in approximately 10 hours under sustained moderate load. The growth pattern is consistent with an accumulating reference — a cache with no eviction policy, an unclosed resource, or a growing collection that is never flushed.

**Output**

```json
{
  "id": "LT-2026-0002",
  "title": "Linear memory growth under sustained load — probable memory leak",
  "analysis_domain": "load_testing",
  "evidence": "Memory grew from 512 MB to 1,380 MB over 6 hours at 20 concurrent users (145 MB/hour average). Growth was linear with no plateau. Latency and error rate were stable, ruling out request queuing as the cause. Server would exhaust 2 GB heap in approximately 10 hours under this load.",
  "impact": "Under sustained production load the service will exhaust available memory and crash or trigger OOM-killing. Recovery requires a restart, causing downtime. The issue is invisible in short tests and will only manifest hours into a busy period.",
  "confidence": "high",
  "cwe": ["CWE-401"],
  "mitre_attck": [],
  "cvss": "",
  "remediation": "Profile heap allocation with a memory profiler (e.g., memory-profiler for Python, VisualVM for JVM, pprof for Go) during a 30-minute reproducer run. Look for collections or caches that grow without bound. Add eviction policies (TTL or max-size) to any in-memory caches. Re-run soak test for 6 hours after fix and confirm memory plateau.",
  "verification_steps": [
    "Run heap profiler during 30-minute load session and identify top allocating objects",
    "Fix identified accumulation point",
    "Re-run 6-hour soak test at 20 concurrent users",
    "Confirm memory stabilises within the first 30 minutes and does not grow beyond 600 MB"
  ]
}
```

---

### Example 3 — Cloud auto-scaling too slow for spike traffic

**Input**

```
Target: https://shop.example.com (AWS ECS, authorized by: platform team)
Test type: spike test
Baseline: 10 concurrent users
Spike: jump to 200 concurrent users at t=2min, hold 3 min, return to 10
Auto-scaling configured: scale out when CPU > 60% for 3 minutes
Results:
  t=0–2min (baseline): P95 140 ms, error rate 0%
  t=2–4min (spike onset): P95 climbed to 8,900 ms, error rate 12% (HTTP 503)
  t=5min: new instances came online, P95 dropped to 320 ms, error rate 0%
  t=7min (post-spike): returned to baseline
```

**Analysis**

Auto-scaling worked but the 3-minute CPU threshold meant the system was degraded for approximately 3 minutes before new capacity arrived. For an e-commerce checkout flow, a 12% error rate over 3 minutes during a spike event represents significant lost revenue. The scaling policy needs a faster trigger.

**Output**

```json
{
  "id": "LT-2026-0003",
  "title": "Auto-scaling response too slow for spike traffic — 3-minute degradation window",
  "analysis_domain": "load_testing",
  "evidence": "Spike from 10 to 200 concurrent users caused P95 latency to reach 8,900 ms and error rate to hit 12% for approximately 3 minutes before new ECS tasks became healthy. Auto-scaling trigger threshold is CPU > 60% for 3 consecutive minutes.",
  "impact": "A real spike event (flash sale, viral link) causes a 3-minute window of service degradation visible to users. At estimated peak checkout rate this represents lost revenue per minute of downtime.",
  "confidence": "high",
  "cwe": [],
  "mitre_attck": [],
  "cvss": "",
  "remediation": "Reduce auto-scaling CPU evaluation period from 3 minutes to 1 minute. Add a request-count-per-target metric as a secondary scaling trigger (scales out when ALB RequestCountPerTarget exceeds threshold for 1 minute). Pre-warm capacity before known spike events. Consider keeping minimum task count at 3 instead of 1 to absorb the initial burst.",
  "verification_steps": [
    "Update ECS auto-scaling policy: CPU threshold period 1 minute",
    "Add RequestCountPerTarget scaling policy",
    "Re-run identical spike test",
    "Confirm degradation window drops below 60 seconds",
    "Confirm error rate stays below 1% during spike"
  ]
}
```
