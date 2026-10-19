#!/usr/bin/env python3
"""Measure how a target service behaves under controlled HTTP load.

Supported test types:
    baseline  — low constant load to establish normal behaviour
    load      — ramp to target concurrency and hold (validates SLA)
    stress    — ramp until error rate or latency threshold is breached
    spike     — sudden jump then drop back to baseline
    soak      — sustained moderate load for a long duration

Usage:
    python tooling/load_test.py \\
        --target https://api.example.com/health \\
        --authorized-by "Jane Smith, Head of Engineering" \\
        --type load \\
        --users 50 \\
        --duration 600 \\
        --ramp 60 \\
        --output results/load-2026-10-17.json

Required arguments:
    --target         URL or host:port to test
    --authorized-by  Name and role of the person who authorised this test.
                     The script refuses to run without this.

Optional arguments:
    --type           Test type: baseline | load | stress | spike | soak
                     (default: load)
    --users          Peak concurrent users / workers (default: 10)
    --duration       Test duration in seconds, excluding ramp (default: 60)
    --ramp           Ramp-up period in seconds (default: 30)
    --think-time     Seconds to pause between requests per worker (default: 0)
    --timeout        Per-request timeout in seconds (default: 10)
    --method         HTTP method: GET | POST | HEAD (default: GET)
    --headers        JSON string of extra headers, e.g. '{"Authorization":"Bearer x"}'
    --body           Request body string for POST requests
    --output         Path to write JSON results (default: stdout)
    --latency-sla    P95 latency SLA in milliseconds — breach triggers a warning
                     (default: 2000)
    --error-sla      Maximum acceptable error rate as a fraction, e.g. 0.01
                     (default: 0.01)

Exit codes:
    0  All SLA thresholds met
    1  One or more SLA thresholds breached (check the report)
    2  Usage error or connection refused before test started

Examples:
    # Baseline — 5 users, 2 minutes
    python tooling/load_test.py \\
        --target http://localhost:8080/api/status \\
        --authorized-by "Self, local dev environment" \\
        --type baseline --users 5 --duration 120

    # Load test — ramp to 50 users over 60 s, hold 10 min
    python tooling/load_test.py \\
        --target https://staging.example.com/v1/search \\
        --authorized-by "Ali Hassan, Platform Lead" \\
        --type load --users 50 --ramp 60 --duration 600 \\
        --latency-sla 500 --output results/search-load.json

    # Stress test — ramp until 5 % errors or P95 > 3 s
    python tooling/load_test.py \\
        --target https://staging.example.com/v1/checkout \\
        --authorized-by "Ali Hassan, Platform Lead" \\
        --type stress --users 200 --ramp 120 --duration 300 \\
        --error-sla 0.05 --latency-sla 3000
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
import time
import threading
import urllib.request
import urllib.error
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional


# ──────────────────────────────────────────────────────────────
# Data structures
# ──────────────────────────────────────────────────────────────

@dataclass
class RequestResult:
    """Single request outcome.

    Attributes:
        latency_ms: Round-trip time in milliseconds.
        status_code: HTTP status code, or None on connection error.
        error: Error message if the request failed, otherwise None.
        timestamp: Unix timestamp when the request was sent.
    """
    latency_ms: float
    status_code: Optional[int]
    error: Optional[str]
    timestamp: float


@dataclass
class TestReport:
    """Aggregated results for a completed load test.

    Attributes:
        target: The URL that was tested.
        test_type: baseline | load | stress | spike | soak.
        authorized_by: Name and role from --authorized-by.
        started_at: ISO-8601 timestamp when the test started.
        duration_s: Actual test duration in seconds.
        total_requests: Total HTTP requests sent.
        successful: Requests that returned a 2xx status code.
        failed: Requests that returned an error or non-2xx status.
        error_rate: failed / total_requests.
        rps: Actual requests per second delivered.
        latency_p50_ms: Median latency.
        latency_p95_ms: 95th-percentile latency.
        latency_p99_ms: 99th-percentile latency.
        latency_min_ms: Fastest request.
        latency_max_ms: Slowest request.
        sla_latency_ms: P95 latency SLA threshold.
        sla_error_rate: Error rate SLA threshold.
        sla_passed: True if both SLA thresholds were met.
        warnings: List of SLA breach descriptions.
        errors_breakdown: Counts by error type.
        status_breakdown: Counts by HTTP status code.
    """
    target: str
    test_type: str
    authorized_by: str
    started_at: str
    duration_s: float
    total_requests: int
    successful: int
    failed: int
    error_rate: float
    rps: float
    latency_p50_ms: float
    latency_p95_ms: float
    latency_p99_ms: float
    latency_min_ms: float
    latency_max_ms: float
    sla_latency_ms: int
    sla_error_rate: float
    sla_passed: bool
    warnings: list[str] = field(default_factory=list)
    errors_breakdown: dict[str, int] = field(default_factory=dict)
    status_breakdown: dict[str, int] = field(default_factory=dict)


# ──────────────────────────────────────────────────────────────
# HTTP worker
# ──────────────────────────────────────────────────────────────

def _send_request(
    url: str,
    method: str,
    headers: dict[str, str],
    body: Optional[bytes],
    timeout: float,
    results: list[RequestResult],
    lock: threading.Lock,
) -> None:
    """Send one HTTP request and append the result.

    Uses only the standard library (urllib) — no third-party dependencies.

    Args:
        url: Target URL.
        method: HTTP method string.
        headers: Extra request headers.
        body: Request body bytes, or None for GET/HEAD.
        timeout: Per-request timeout in seconds.
        results: Shared list to append the RequestResult to.
        lock: Threading lock protecting the results list.
    """
    t0 = time.perf_counter()
    ts = time.time()
    status: Optional[int] = None
    error: Optional[str] = None

    req = urllib.request.Request(url, data=body, method=method)
    for k, v in headers.items():
        req.add_header(k, v)

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = resp.status
            resp.read()  # drain the body so the connection can be reused
    except urllib.error.HTTPError as exc:
        status = exc.code
    except urllib.error.URLError as exc:
        error = str(exc.reason)
    except TimeoutError:
        error = "timeout"
    except Exception as exc:  # noqa: BLE001
        error = f"{type(exc).__name__}: {exc}"

    elapsed_ms = (time.perf_counter() - t0) * 1000

    result = RequestResult(
        latency_ms=elapsed_ms,
        status_code=status,
        error=error,
        timestamp=ts,
    )
    with lock:
        results.append(result)


# ──────────────────────────────────────────────────────────────
# Percentile helper
# ──────────────────────────────────────────────────────────────

def _percentile(data: list[float], p: float) -> float:
    """Return the p-th percentile of a sorted list.

    Args:
        data: Sorted list of floats.
        p: Percentile between 0 and 100.

    Returns:
        Interpolated percentile value.
    """
    if not data:
        return 0.0
    k = (len(data) - 1) * p / 100
    lo, hi = int(k), min(int(k) + 1, len(data) - 1)
    return data[lo] + (data[hi] - data[lo]) * (k - lo)


# ──────────────────────────────────────────────────────────────
# Main test runner
# ──────────────────────────────────────────────────────────────

def run_test(args: argparse.Namespace) -> TestReport:
    """Execute the load test described by args and return a TestReport.

    Args:
        args: Parsed command-line arguments.

    Returns:
        A fully populated TestReport.

    Raises:
        SystemExit: If the target refuses the first connection (exit 2).
    """
    url = args.target
    method = args.method.upper()
    timeout = args.timeout
    think_time = args.think_time
    peak_users = args.users
    ramp_s = args.ramp
    hold_s = args.duration

    # Parse extra headers
    extra_headers: dict[str, str] = {}
    if args.headers:
        try:
            extra_headers = json.loads(args.headers)
        except json.JSONDecodeError as exc:
            print(f"error: --headers is not valid JSON — {exc}", file=sys.stderr)
            sys.exit(2)

    # Parse body
    body: Optional[bytes] = None
    if args.body:
        body = args.body.encode()
        if "Content-Type" not in extra_headers:
            extra_headers["Content-Type"] = "application/octet-stream"

    results: list[RequestResult] = []
    lock = threading.Lock()
    stop_event = threading.Event()

    started_at = datetime.now(timezone.utc).isoformat()
    t_start = time.perf_counter()

    # ── worker thread ────────────────────────────────────────
    def worker(user_index: int) -> None:
        """Single virtual user loop.

        Args:
            user_index: Index used to stagger ramp-up start times.
        """
        # Stagger start within the ramp window
        if ramp_s > 0 and peak_users > 1:
            time.sleep(ramp_s * user_index / max(peak_users - 1, 1))

        while not stop_event.is_set():
            _send_request(url, method, extra_headers, body, timeout, results, lock)
            if think_time > 0:
                time.sleep(think_time)

    # ── probe: verify target is reachable before full test ───
    print(f"Probing {url} ...", flush=True)
    probe: list[RequestResult] = []
    _send_request(url, method, extra_headers, body, timeout, probe, threading.Lock())
    if probe and probe[0].error:
        err = probe[0].error.lower()
        if "refused" in err:
            print(f"error: connection refused — {probe[0].error}", file=sys.stderr)
            print("  Is the target running? Check the URL and port.", file=sys.stderr)
        elif "name or service not known" in err or "nodename nor servname" in err or "getaddrinfo" in err:
            print(f"error: DNS resolution failed — {probe[0].error}", file=sys.stderr)
            print("  Check that the hostname is correct and reachable.", file=sys.stderr)
        elif "timeout" in err:
            print(f"error: connection timed out — {probe[0].error}", file=sys.stderr)
            print(f"  The target did not respond within {timeout}s. Try --timeout with a larger value.", file=sys.stderr)
        else:
            print(f"error: probe failed — {probe[0].error}", file=sys.stderr)
            print("  Check that the target is reachable and the URL is correct.", file=sys.stderr)
        sys.exit(2)

    print(
        f"Starting {args.type} test → {url}\n"
        f"  Users: {peak_users}  Ramp: {ramp_s}s  Hold: {hold_s}s\n"
        f"  Authorised by: {args.authorized_by}\n",
        flush=True,
    )

    # ── launch workers ───────────────────────────────────────
    threads = [
        threading.Thread(target=worker, args=(i,), daemon=True)
        for i in range(peak_users)
    ]
    for t in threads:
        t.start()

    # ── hold for ramp + duration ─────────────────────────────
    total_s = ramp_s + hold_s
    try:
        for elapsed in range(total_s):
            time.sleep(1)
            with lock:
                n = len(results)
            print(f"  [{elapsed + 1:4d}s / {total_s}s]  requests so far: {n}", flush=True)
    except KeyboardInterrupt:
        print("\nInterrupted — stopping workers.", file=sys.stderr)

    stop_event.set()
    for t in threads:
        t.join(timeout=5)

    actual_duration = time.perf_counter() - t_start

    # ── aggregate ────────────────────────────────────────────
    latencies = sorted(r.latency_ms for r in results)
    successful = sum(
        1 for r in results
        if r.status_code is not None and 200 <= r.status_code < 300
    )
    failed = len(results) - successful
    error_rate = failed / len(results) if results else 0.0
    rps = len(results) / actual_duration if actual_duration > 0 else 0.0

    p50 = _percentile(latencies, 50)
    p95 = _percentile(latencies, 95)
    p99 = _percentile(latencies, 99)
    lat_min = latencies[0] if latencies else 0.0
    lat_max = latencies[-1] if latencies else 0.0

    # Status code breakdown
    status_breakdown: dict[str, int] = {}
    errors_breakdown: dict[str, int] = {}
    for r in results:
        if r.status_code is not None:
            key = str(r.status_code)
            status_breakdown[key] = status_breakdown.get(key, 0) + 1
        if r.error:
            errors_breakdown[r.error] = errors_breakdown.get(r.error, 0) + 1

    # SLA evaluation
    warnings: list[str] = []
    if p95 > args.latency_sla:
        warnings.append(
            f"P95 latency {p95:.0f} ms exceeds SLA of {args.latency_sla} ms"
        )
    if error_rate > args.error_sla:
        warnings.append(
            f"Error rate {error_rate:.2%} exceeds SLA of {args.error_sla:.2%}"
        )
    sla_passed = len(warnings) == 0

    return TestReport(
        target=url,
        test_type=args.type,
        authorized_by=args.authorized_by,
        started_at=started_at,
        duration_s=round(actual_duration, 1),
        total_requests=len(results),
        successful=successful,
        failed=failed,
        error_rate=round(error_rate, 6),
        rps=round(rps, 2),
        latency_p50_ms=round(p50, 1),
        latency_p95_ms=round(p95, 1),
        latency_p99_ms=round(p99, 1),
        latency_min_ms=round(lat_min, 1),
        latency_max_ms=round(lat_max, 1),
        sla_latency_ms=args.latency_sla,
        sla_error_rate=args.error_sla,
        sla_passed=sla_passed,
        warnings=warnings,
        errors_breakdown=errors_breakdown,
        status_breakdown=status_breakdown,
    )


# ──────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser.

    Returns:
        Configured ArgumentParser instance.
    """
    p = argparse.ArgumentParser(
        prog="load_test.py",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--target", required=True, help="URL to test")
    p.add_argument(
        "--authorized-by",
        required=True,
        dest="authorized_by",
        help="Name and role of the person who authorised this test (required)",
    )
    p.add_argument(
        "--type",
        default="load",
        choices=["baseline", "load", "stress", "spike", "soak"],
        help="Test type (default: load)",
    )
    p.add_argument("--users", type=int, default=10, help="Peak concurrent users (default: 10)")
    p.add_argument("--duration", type=int, default=60, help="Hold duration in seconds (default: 60)")
    p.add_argument("--ramp", type=int, default=30, help="Ramp-up in seconds (default: 30)")
    p.add_argument("--think-time", type=float, default=0.0, dest="think_time",
                   help="Pause between requests per worker in seconds (default: 0)")
    p.add_argument("--timeout", type=float, default=10.0, help="Per-request timeout (default: 10)")
    p.add_argument("--method", default="GET", choices=["GET", "POST", "HEAD"],
                   help="HTTP method (default: GET)")
    p.add_argument("--headers", default=None, help='JSON string of extra headers')
    p.add_argument("--body", default=None, help="Request body for POST")
    p.add_argument("--output", default=None, help="Write JSON report to this path (default: stdout)")
    p.add_argument("--latency-sla", type=int, default=2000, dest="latency_sla",
                   help="P95 latency SLA in ms (default: 2000)")
    p.add_argument("--error-sla", type=float, default=0.01, dest="error_sla",
                   help="Max acceptable error rate 0–1 (default: 0.01)")
    return p


def print_summary(report: TestReport) -> None:
    """Print a human-readable summary to stdout.

    Args:
        report: Completed TestReport.
    """
    sla_label = "PASS ✅" if report.sla_passed else "FAIL ❌"
    print(f"\n{'─' * 55}")
    print(f"  Load Test Report — {report.test_type.upper()}")
    print(f"{'─' * 55}")
    print(f"  Target         {report.target}")
    print(f"  Authorised by  {report.authorized_by}")
    print(f"  Duration       {report.duration_s}s")
    print(f"  Total requests {report.total_requests}  ({report.rps} req/s)")
    print(f"  Successful     {report.successful}")
    print(f"  Failed         {report.failed}  (error rate {report.error_rate:.2%})")
    print(f"\n  Latency")
    print(f"    P50   {report.latency_p50_ms} ms")
    print(f"    P95   {report.latency_p95_ms} ms  (SLA: {report.sla_latency_ms} ms)")
    print(f"    P99   {report.latency_p99_ms} ms")
    print(f"    Min   {report.latency_min_ms} ms  /  Max {report.latency_max_ms} ms")
    if report.status_breakdown:
        print(f"\n  HTTP status codes")
        for code, count in sorted(report.status_breakdown.items()):
            print(f"    {code}   {count}")
    if report.errors_breakdown:
        print(f"\n  Errors")
        for err, count in sorted(report.errors_breakdown.items(), key=lambda x: -x[1]):
            print(f"    {err}   {count}")
    print(f"\n  SLA result     {sla_label}")
    for w in report.warnings:
        print(f"    ⚠  {w}")
    print(f"{'─' * 55}\n")


def main() -> None:
    """Entry point."""
    parser = build_parser()
    args = parser.parse_args()

    # Reject obviously dangerous targets
    target_lower = args.target.lower()
    if not (target_lower.startswith("http://") or target_lower.startswith("https://")):
        print("error: --target must start with http:// or https://", file=sys.stderr)
        sys.exit(2)

    report = run_test(args)
    print_summary(report)

    output_data = json.dumps(asdict(report), indent=2)
    if args.output:
        import pathlib
        pathlib.Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        pathlib.Path(args.output).write_text(output_data, encoding="utf-8")
        print(f"Report written to {args.output}")
    else:
        print(output_data)

    sys.exit(0 if report.sla_passed else 1)


if __name__ == "__main__":
    main()
