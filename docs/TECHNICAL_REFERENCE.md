# Memu OS Technical Reference & Codebase Review

**Version:** 1.0  
**Date:** February 2026  
**Audience:** Developers, Architects, and Solution Engineers

---

## 1. Executive Summary

Memu OS is a **vertically integrated private cloud appliance** designed for family data sovereignty. Unlike typical self-hosted stacks, it focuses on **UX-first design** (no terminal for end-users), **AI integration** (local context engine), and **secure remote access** without public port exposure.

The core philosophy is **"Tenant Isolation on Owned Hardware"**. The code provides a "turnkey" experience on standard hardware (Intel N100 or Raspberry Pi 5).

---

## 2. System Architecture

The solution operates as a Docker-based microservices architecture on top of a standard Linux OS (Ubuntu/Debian).

### 2.1 Hardware Layer
- **Target:** Intel N100 Mini PCs (primary) or Raspberry Pi 5.
- **Acceleration:** Uses Intel QuickSync (N100) or Hailo-8L NPU (Pi 5) for computer vision and AI workloads.

### 2.2 Critical Infrastructure
- **Systemd:** Manages the lifecycle of the entire stack.
  - `memu-production.service`: Ensures the Docker Compose stack is up.
  - `memu-setup.service`: Bootstrap wizard (disabled after setup).
  - `memu-backup.service` & `memu-backup.timer`: Daily backups.
- **Network (Tailscale):** The device runs a Tailscale node in `host` networking mode. ALL remote access happens via this private mesh VPN layer. No firewall ports are open to the public internet.

### 2.3 Container Stack (`docker-compose.yml`)

The stack is composed of 5 logical planes:

1.  **Routing Plane:**
    -   **Nginx (`memu_proxy`)**: The *only* container exposing port 80. Routes traffic based on hostname/path to internal containers.
    -   **Tailscale (`memu_tailscale`)**: Provides the secure tunnel.

2.  **Communication Plane (Matrix):**
    -   **Synapse (`memu_synapse`)**: The reference Matrix homeserver.
    -   **Element (`memu_element`)**: Web-based chat client (highly config-stripped).

3.  **Memory Plane (Immich):**
    -   **Immich Server (`memu_photos`)**: Photo storage, API, and web UI.
    -   **Immich ML (`memu_photos_ml`)**: Machine learning worker (face recognition).

4.  **Intelligence Plane:**
    -   **Ollama (`memu_brain`)**: Local LLM inference server (Llama 3, Ministral).
    -   **Intelligence Service (`memu_intelligence`)**: Custom Python bot (More details in Section 4).

5.  **State Plane:**
    -   **Postgres (`memu_postgres`)**: Shared database (pgvecto.rs extension installed for vector search).
    -   **Redis (`memu_redis`)**: Shared cache.

---

## 3. Key Workflows & UX Journey

### 3.1 Installation (`install.sh`)
**Goal:** Idempotent, silent server preparation.
1.  **System Check:** Verifies RAM, creates Swap.
2.  **State Prep:** Creates minimal directory structure (`synapse/`, `photos/`, `nginx/`).
3.  **Config Seeding:** Writes *placeholder* configs for Nginx and Element to ensure Docker starts without errors before configuration.
4.  **Service Install:** Writes and enables systemd units.
5.  **Handover:** Starts minimal `memu-setup` service and exits.

### 3.2 Post-Install Setup (Web Wizard)
**Code:** `bootstrap/app.py`
**Goal:** Configure complex services without user knowing what YAML is.
1.  **User Input:** Family Name, Admin Password, Tailscale Auth Key.
2.  **Configuration Generation:**
    -   Generates `synapse/homeserver.yaml` with correct secrets.
    -   Generates `nginx/conf.d/default.conf` with correct upstream routing.
    -   Writes `.env` file with secure random passwords.
3.  **Provisioning:**
    -   Spins up `database`.
    -   Initializes SQL schemas.
    -   Spins up `synapse`.
    -   **User Creation:** Uses Docker CLI to exec into Synapse and register the Admin user.
    -   **Bot Creation:** Registers `@memu_bot` and saves token.
4.  **Final Polish:** Configures Tailscale/MagicDNS and redirects user to the production dashboard.

### 3.3 The "Context Engine" (Intelligence Service)
**Code:** `services/intelligence/`
**Goal:** An AI that knows the family context.
-   **Integration:** Joins the family chat room as a bot.
-   **Memory:** Creates a custom schema in Postgres (`household_memory`, `shared_lists`, `reminders`).
-   **Recall Logic:**
    1.  User types `/recall where is the wifi password`.
    2.  Bot searches explicit memory (facts saved via `/remember`).
    3.  **Bot searches actual chat history** (via Synapse Search API).
    4.  Synthesizes a response using Ollama.

---

## 4. Developer Guide

### 4.1 "Do Not Break" Rules
1.  **Idempotency is King:** The `install.sh` script is often run multiple times (upgrades/fixes). *Never* overwrite a user's config file (like `homeserver.yaml` or `.env`) if it already exists. Use `if [ ! -f ... ]` checks.
2.  **Secrets Management:** All passwords live in `.env`. Python scripts should read from `os.environ`. Never hardcode credentials.
3.  **Mobile Compatibility:** The Nginx proxy rules are complex to support Mobile Apps (Element iOS, Immich Android).
    -   Matrix federation uses `/.well-known` paths.
    -   Immich often needs its own port (`2283`) mapped through for mobile apps if the web proxy fails. *Do not remove port mappings without testing mobile clients.*
    -   Tailscale handles TLS/HTTPS automatically. *Do not add manual Certbot/LetsEncrypt logic*, as it conflicts with MagicDNS.

### 4.2 Adding New Features
*   **New Service:** Add to `docker-compose.yml`, ensure it joins `memu_net`, and expose NO ports unless strictly necessary. Proxy it via `nginx/conf.d`.
*   **Migration:** If you change a generic config (like `nginx.conf`), you must write a script to update *existing* users' files, as the installer protects them.
*   **Database:** Use the shared Postgres instance if possible. Create a new DB (e.g., `CREATE DATABASE new_app;`) in `bootstrap/app.py` -> `create_databases()`.

### 4.3 Key Directories
| Path | Purpose |
|------|---------|
| `/bootstap` | The "Installer" web app code. |
| `/services/intelligence` | The Python AI bot code. |
| `/synapse` | Matrix config and data. |
| `/nginx` | Reverse proxy configuration. |
| `/scripts` | Maintenance utilities (`install.sh`, `backup.sh`). |

---

## 5. Security Model
-   **Zero Trust Ingress:** No open ports. Tailscale Auth Key is crucial.
-   **Isolation:** Apps talk on internal Docker bridge.
-   **Data Ownership:** All state is in `./photos`, `./synapse`, and Postgres volumes. Backing up the project root + docker volumes = full recovery.
