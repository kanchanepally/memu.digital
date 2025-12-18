# Debugging Report: Memu OS Open Source Release Prep
**Date:** December 17-18, 2025
**Objective:** Finalize "One-Click" Installation for Digital Ocean (2GB Droplet)
**Status:** ✅ Solved & Stable

---

## 🚀 Executive Summary
We successfully transformed a fragile installation process into a robust, "terminal-free" experience. This involved identifying and fixing **9 distinct critical failures**, ranging from simple missing dependencies to complex systemd race conditions and silent authentication failures.

The system now runs stable on resource-constrained environments (1GB RAM) with proper error handling and self-correcting configuration.

---

## 🐛 Bug Hunt & Fix Log

### 1. The "Module Not Found" Crash
*   **Symptom:** The Setup Wizard crashed immediately because it couldn't find `flask` or `pip`.
*   **Root Cause:** `install.sh` assumed these were present on the host (Digital Ocean Ubuntu).
*   **Fix:** Updated `scripts/install.sh` to explicitly install `python3-pip` and `flask`.

### 2. The "Database Vector" Crash
*   **Symptom:** Immich returned 404/500 errors.
*   **Root Cause:** The `postgres:15-alpine` image did not support the `pgvecto.rs` extension required by Immich AI.
*   **Fix:** Swapped Docker image to `tensorchord/pgvecto-rs:pg15-v0.2.0`.

### 3. The "Permission Denied" Key Error
*   **Symptom:** Synapse container failed to start (`PermissionError: [Errno 13]`).
*   **Root Cause:** Docker volume directory was owned by `root`, preventing the container user from writing signing keys.
*   **Fix:** Added `mkdir -p` and `chmod 777 ./synapse` to `install.sh` to pre-provision writable storage.

### 4. The "Hidden Saboteur" (Nginx Corruption)
*   **Symptom:** Site worked during setup, then crashed with `memu_chat_ui` errors immediately after clicking "Launch".
*   **Root Cause:** A legacy script `scripts/launch_production.sh` was lying dormant in the repo. The Wizard called it, and it **overwrote** the freshly generated Nginx config with an old, broken version.
*   **Fix:** **Deleted** the legacy script and moved the launch logic safely into `app.py`.

### 5. The "Service Suicide" (Blank Page Error)
*   **Symptom:** Clicking "Launch" resulted in a blank/error page in the browser instead of "Success".
*   **Root Cause:** The Wizard stopped its own systemd service *too quickly*, killing the network connection before it could send the success HTTP response to the user.
*   **Fix:** Implemented a **Detached Handoff** mechanism.

### 6. The "Port 80 War" (Race Condition)
*   **Symptom:** "Address already in use" or "Connection Refused".
*   **Root Cause:** The Wizard (Port 80) and Production Nginx (Port 80) fought for the port. The Wizard needed to die for Nginx to live, but if it died too fast, the logic stopped.
*   **Fix:** Used `systemd-run` to spawn a **Transient Independent Unit** that waits 3 seconds, stops the Wizard, and starts Production safely.

### 7. The "Host Not Found" Boot Crash
*   **Symptom:** Nginx crashed on boot with `host not found in upstream "synapse"`.
*   **Root Cause:** Nginx started milliseconds faster than the Synapse container. It tried to resolve the DNS, failed, and exited.
*   **Fix:** Implemented **Lazy DNS Resolution** in Nginx config:
    *   Added `resolver 127.0.0.11;` (Docker's internal DNS).
    *   Used variables (`$upstream_synapse`) to force runtime resolution instead of boot-time resolution.

### 8. The "Resource Starvation" Timeout
*   **Symptom:** Setup Wizard failed with "Chat server failed to start".
*   **Root Cause:** On 1GB RAM, Synapse key generation takes >60 seconds. The Wizard timed out.
*   **Fix:** Increased `wait_for_synapse` timeout to **180 seconds** in `app.py`.

### 9. The "Ghost Admin" (Silent Auth Failure)
*   **Symptom:** Wizard said "Success", but the `admin` user didn't exist (Login failed).
*   **Root Cause:**
    *   **A:** The generated config missed `registration_shared_secret`, causing Synapse to reject the admin creation request.
    *   **B:** The Python script failed silently because it ignored the error code from the command.
*   **Fix:**
    *   Added the secret generation to `app.py`.
    *   Updated `create_matrix_user` to **capture and report errors** loudly, ensuring no more silent failures.

---

## 🏆 Final Outcome
The codebase is now resilient. It handles low-resource environments, cleans up after itself, prevents race conditions, and correctly reports errors.
