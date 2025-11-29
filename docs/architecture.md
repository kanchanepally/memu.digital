# Memu OS Architecture

## System Overview

Memu OS is a **vertically integrated Private Cloud Appliance** designed to provide a "Digital Sanctuary" for families. It combines the convenience of modern cloud services with the sovereignty of local hosting.

**Key Philosophies:**
- **Tenant-Isolated:** One family, one physical device.
- **Edge-Based Safety:** Safety scanning occurs locally on the NPU, not in the cloud.
- **Network Agnostic:** Works behind any router via encrypted tunnels.

## The Stack

### Hardware Layer
- **Compute:** Raspberry Pi 5 (8GB RAM recommended).
- **Storage:** NVMe SSD (PCIe Gen 2) - Holds OS and User Data.
- **AI Accelerator:** Raspberry Pi AI Kit (Hailo-8L NPU) - Offloads computer vision tasks.
- **Boot:** SD Card (Bootloader only).

### Routing Layer (The "Front Door")
- **Ingress:** Cloudflare Tunnel (`cloudflared`). Zero-configuration remote access without open ports.
- **Internal Proxy:** Nginx. Terminates SSL (internally), handles `/.well-known` discovery, and routes traffic to containers.

### Application Layer (Docker Compose)

The system runs as a cohesive suite of Docker containers:

#### Core Infrastructure
- **Database:** `immich-postgres` (PostgreSQL 15 + `pgvecto.rs` extension). Unified database for Chat, Photos, and AI embeddings.
- **Cache:** `redis` (Redis 6.2). Shared cache for Immich and other services.

#### Modules
1.  **Memu Chat:**
    -   **Backend:** `synapse` (Matrix Homeserver).
    -   **Frontend:** `element` (Element Web, skinned for Memu).
2.  **Memu Memories:**
    -   **Server:** `immich-server`.
    -   **Workers:** `immich-microservices`.
    -   **ML Engine:** `immich-machine-learning` (Hardware accelerated via Hailo NPU).
3.  **Memu Intelligence:**
    -   **LLM Server:** `ollama` (Running Llama 3.2 3B).
    -   **Safety:** Local Nudity/CSAM scanning at the edge.
## Data Sovereignty Strategy

### Storage
-   **Location:** `/var/lib/docker/volumes/` (Mapped to NVMe).
-   **Format:** Standard Linux filesystems (ext4). Photos stored as standard files, not blobs.

### Backup Protocol (3-2-1)
-   **Live:** PostgreSQL WAL (Write Ahead Log).
-   **Nightly:** `pg_dump` to local compressed archive.
-   **Offsite:** Encrypted backup to User's Cloud Storage (Rclone) or Physical USB (Future).