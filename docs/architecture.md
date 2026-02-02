# Memu OS Architecture

## System Overview

Memu OS is a **vertically integrated Private Cloud Appliance** designed to provide a "Digital Sanctuary" for families. It combines the convenience of modern cloud services with the sovereignty of local hosting.

**Key Philosophies:**
- **Tenant-Isolated:** One family, one physical device.
- **Edge-Based Safety:** Safety scanning occurs locally on the NPU, not in the cloud.
- **Network Agnostic:** Works behind any router via encrypted tunnels (Tailscale).

## The Stack

### Hardware Layer
- **Compute:** Raspberry Pi 5 (8GB RAM recommended) or x86 NUC.
- **Storage:** NVMe SSD (PCIe Gen 2) - Holds OS and User Data.
- **AI Accelerator:** Raspberry Pi AI Kit (Hailo-8L NPU) - Offloads computer vision tasks.
- **Boot:** SD Card (Bootloader only) or NVMe.

### Routing Layer (The "Front Door")
- **Ingress:** **Tailscale** (Mesh VPN). Provides secure, encrypted remote access without opening public ports.
- **DNS:** **MagicDNS**. Allows accessing services via friendly names (e.g., `http://memu-hub`) instead of IPs.
- **Internal Proxy:** **Nginx**.
    -   Listens on Port 80.
    -   Routes traffic to internal containers based on URL paths (`/admin`, `/_matrix`, `/`).
    -   Handles `/.well-known` discovery for Matrix federation.

### Application Layer (Docker Compose)

The system runs as a cohesive suite of Docker containers connected via numbers `memu_net` bridge network:

#### 1. Setup & Management (The "OS")
-   **Service:** `bootstrap` (Containerized Python/Flask).
-   **Function:**
    -   Host of the **Setup Wizard** and **Admin Dashboard**.
    -   Manages `memu.db` (SQLite) for user/family metadata.
    -   Connects to Docker Socket (`/var/run/docker.sock`) to manage the stack.
    -   Provides authentication (`/login`) for administrative tasks.

#### 2. Core Infrastructure
-   **Database:** `memu_postgres` (PostgreSQL 15 + `pgvecto.rs`). Unified database for Chat, Photos, and AI embeddings.
-   **Cache:** `memu_redis` (Redis 6.2). Shared cache.
-   **Network:** `memu_tailscale` (Tailscale). Runs in `host` network mode to provide connectivity to the entire stack.

#### 3. Memu Chat (Matrix)
-   **Backend:** `synapse` (Matrix Homeserver).
-   **Frontend:** `element` (Element Web, highly customized config).
-   **Routing:** `/` -> Element, `/_matrix` -> Synapse.

#### 4. Memu Memories (Immich)
-   **Server:** `immich_server` (Monolithic container). Handles API, web, and microservices (v1.124+).
-   **ML Engine:** `immich_ml` (Hardware accelerated via Hailo NPU where available).
-   **Storage:** Photos stored in `./photos` (mapped to host).

#### 5. Memu Intelligence (AI)
-   **LLM Server:** `ollama` (Running Llama 3.2 3B).
-   **Service:** `intelligence` (Python bot).
    -   Listens to Matrix chat events.
    -   Orchestrates memory and RAG (Retrieval Augmented Generation).

## Data Flow

### User Access (Remote or Local)
1.  **User Device** (Phone/Laptop on Tailscale) requests `http://memu-hub` (MagicDNS).
2.  **Tailscale Tunnel** accepts traffic and forwards to Host Port 80.
3.  **Nginx (Proxy)** receives request:
    -   Path `/admin` -> Proxies to `bootstrap:8888`.
    -   Path `/` -> Proxies to `element:80`.
    -   Path `/photos` (or Port 2283) -> Proxies to `immich_server:2283`.
4.  **Service** processes request and queries `postgres` or `redis`.

### Backup Protocol
-   **Database:** Periodic dumps of `memu_postgres`.
-   **Files:** `./photos` directory.
-   **Config:** `.env` and `docker-compose.yml`.