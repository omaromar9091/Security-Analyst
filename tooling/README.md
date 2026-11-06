# 🛠️ Security-Analyst Tooling Suite

This folder contains the core python scripts, helper utilities, and test runners used by the **Security-Analyst** framework to execute security assessments, hash IOCs, validate STIX exports, run YARA rules, and perform authorized HTTP load testing.

---

## 📋 Overview of Utilities

| Utility Script | Primary Purpose | Key Features |
| :--- | :--- | :--- |
| `compute_hash.py` | Hash Generation | Generates cryptographic hashes (SHA-256) for IOC tracking. |
| `validate_stix.py` | STIX 2.1 Validation | Validates Threat Intel JSON bundles against STIX specifications. |
| `run_yara_tests.sh` | YARA Rule Enforcement | Executes `.yar` rule files against sample binaries and payloads. |
| `load_test.py` | HTTP Load & Stress Testing | Measures service latency (P50/P95/P99), RPS, and error rates with SLA limits. |

---

## 🚀 Detailed Usage & Examples

### 1. File Hashing Utility (`compute_hash.py`)
Computes the SHA-256 hash of a file for logging Indicator of Compromise (IOC) evidence.

```bash
python tooling/compute_hash.py /path/to/target/sample.bin
```

---

### 2. STIX 2.1 Bundle Validator (`validate_stix.py`)
Parses and validates STIX 2.1 JSON indicator bundles to ensure compliance before sharing threat intelligence.

```bash
python tooling/validate_stix.py exports/indicators.json
```

---

### 3. YARA Rule Test Runner (`run_yara_tests.sh`)
Shell script that executes YARA rules located in the environment against test files in the `examples/` directory.

```bash
chmod +x tooling/run_yara_tests.sh
./tooling/run_yara_tests.sh
```

---

### 4. HTTP Load & Stress Tester (`load_test.py`)
A built-in performance and stress testing tool. Designed to measure system resiliency under different traffic profiles (baseline, load, stress, spike, soak).

> ⚠️ **Authorization Safety Control:** `load_test.py` **requires** the `--authorized-by` argument on every run. The script will refuse to execute without explicitly logging authorization details.

#### Baseline Test Example (5 Users, 60 seconds):
```bash
python tooling/load_test.py \
    --target http://localhost:8080/api/health \
    --authorized-by "Self, local dev environment" \
    --type baseline \
    --users 5 \
    --duration 60
```

#### Load Test Example with Latency SLA Enforcement (50 Users, 10 Minutes):
```bash
python tooling/load_test.py \
    --target https://staging.example.com/v1/search \
    --authorized-by "Ali Hassan, Platform Lead" \
    --type load \
    --users 50 \
    --ramp 60 \
    --duration 600 \
    --latency-sla 500 \
    --output results/search-load.json
```

---

## 🛡️ Usage within AI Agents (Claude / OpenCode / Cline)

When an AI Agent is tasked with binary triage or load testing, it can invoke these tools directly via terminal tools:

- **For IOC logging:** Call `compute_hash.py` on suspicious artifacts.
- **For Performance Assessment:** Invoke `load_test.py` with valid `--authorized-by` credentials provided by the prompt.