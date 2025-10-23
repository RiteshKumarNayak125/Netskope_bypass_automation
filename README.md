# 🔒 Netskope / Jira Timed Security Bypass Automation (SOAR Playbook Mock)

**Purpose-only README** — a concise, GitHub-ready description that explains the project, its goals, simulated components, how to run the demo in Docker, and next steps for production. This version intentionally omits any source code and instead describes the role of each file and the expected commands to run.

---

## 🎯 Project Summary

A contained, Dockerized mock SOAR playbook demonstrating a risk-based, time-bound Netskope policy bypass triggered by an approved Jira Service Management ticket. The automation:

* Enriches the request with a user risk score (mocked).
* Denies the request if risk is above a configurable threshold.
* Adds the user to a bypass group when allowed (mocked enforcement).
* Automatically revokes the bypass after the requested duration.

Everything in this demo is simulated using local mock files and a short-lived container runtime.

---

## 📦 Prerequisites

* Docker Desktop (Windows / macOS / Linux)
* PowerShell, Bash, or a compatible shell
* Basic knowledge of Python and JSON (helpful but not required to run the demo)

---

## 🌐 Simulated Components (Mapping)

* **Workflow Engine** — simulated by `mock_jira_webhook.json` (represents an approved Jira webhook payload).
* **Risk Context** — simulated by `mock_user_history.json` (contains users and risk scores; stands in for Netskope CRE).
* **Enforcement Point** — simulated by `mock_netskope_db.txt` (simple text file representing group membership/steering config).
* **Automation Engine** — `automation_script.py` (single-file orchestration that reads the webhook, performs enrichment/decision, modifies the mock DB, waits, then revokes).

> All of these are local files mounted into the container for the demo.

---

## 🧩 Files (purpose-only)

* `Dockerfile` — Builds the container image that runs the orchestration demo.
* `automation_script.py` — Orchestrates the playbook flow: enrichment → containment check → apply bypass → timed revocation.
* `requirements.txt` — Lists Python dependencies needed inside the container.
* `mock_jira_webhook.json` — Example Jira webhook payload used to trigger the playbook in demo runs.
* `mock_user_history.json` — Contains sample users and their risk scores for enrichment and policy decisions.
* `mock_netskope_db.txt` — Simple file used by the script to simulate adding/removing users from a bypass group.
* `README.md` — This document.

---

## ⚙️ Setup & Execution (high level)

1. **Create the mock files** in your local project folder. Ensure `mock_netskope_db.txt` exists and is empty before the demo run.

2. **Build the Docker image** (run from project root):

```
docker build -t netskope-automation:latest .
```

3. **Run the container** (replace `YOUR_ABSOLUTE_PATH` with your folder path):

```
docker run -it \
  -v "YOUR_ABSOLUTE_PATH/mock_jira_webhook.json:/app/mock_jira_webhook.json" \
  -v "YOUR_ABSOLUTE_PATH/mock_netskope_db.txt:/app/mock_netskope_db.txt" \
  -v "YOUR_ABSOLUTE_PATH/mock_user_history.json:/app/mock_user_history.json" \
  netskope-automation:latest
```

> The container will execute the orchestration script, print status messages, and exit when the timed revocation completes (or exit early if the containment check denies the request).

---

## 🧪 Demo Scenarios

* **Success case (Alice)**: If `mock_jira_webhook.json` targets `alice.smith@mockcorp.com` and `mock_user_history.json` lists Alice with a risk lower than the threshold (e.g., 35), the script will append her email to `mock_netskope_db.txt`, wait the configured duration (simulated short pause), then remove her entry to simulate revocation.

* **Denial case (Bob)**: If the webhook targets `bob.jones@mockcorp.com` and Bob's risk score in `mock_user_history.json` exceeds the threshold (e.g., 85), the script will print `[POLICY BLOCKED]` and exit immediately — no timed change will be applied.

---

## ⏭️ Production Hardening (next steps)

To convert this demo into a production-ready SOAR playbook, consider:

1. Refactoring `automation_script.py` into a persistent web service (Flask or FastAPI) that accepts authenticated POST requests from Jira webhooks.
2. Replacing mock file operations with **authenticated API calls** to Netskope (for steering/config updates) and Jira (for ticket verification), using secure API tokens.
3. Storing credentials securely (Vault, Azure Key Vault, AWS Secrets Manager).
4. Implementing a reliable revocation mechanism (background job queue, scheduler, or cloud functions) — avoid `sleep()` in production.
5. Adding full audit logging, error handling, RBAC checks, and alerting for failed revocations or denied high-risk requests.

---

## ✅ Notes & Tips

* This demo intentionally simplifies many real-world concerns (auth, rate limits, error handling, auditability). Treat it as a *conceptual* prototype illustrating the workflow and decision points.
* When you take this live, make the risk threshold, bypass group identifiers, and revocation timing configurable.

---

