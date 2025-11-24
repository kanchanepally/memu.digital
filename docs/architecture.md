Memu OS Architecture

System Overview

Memu OS is a microservices architecture wrapped in a single appliance experience. It is designed to be Tenant-Isolated (one family per device) and Network Agnostic (works behind any router).

The Stack

Hardware Layer:

Raspberry Pi 5 (4GB or 8GB RAM)

NVMe SSD (PCIe Gen 2) - Data Storage & OS

SD Card - Bootloader only

Routing Layer (The "Front Door"):

Cloudflare Tunnel (cloudflared): Ingress from the internet. No open ports on router.

Nginx Proxy: Internal traffic director. Terminates SSL, handles /.well-known discovery, routes to containers.

Application Layer (Docker):

Synapse: The Matrix Homeserver (Chat Backend).

PostgreSQL: The source of truth (Database).

Immich: The Photo Server (Coming Phase 2).

Memu Bootstrap: (Python/Flask) Temporary service for initial setup.

Client Layer (The Interface):

Memu Mobile: React Native (Expo) app. Uses Matrix SDK + Custom APIs.

Memu Web: (Legacy/Desktop) SMemuned Element Web instance.

Network Flow

1. Setup Mode (Day 0)

User: Connects to WiFi.

Discovery: mDNS broadcasts memu.local.

Traffic: Phone -> http://memu.local -> Nginx -> Bootstrap App (Port 5000).

Action: User inputs "Smiths". System writes .env, generates Nginx config, and restarts.

2. Production Mode (Day 1+)

External Traffic:
smiths.memu.digital -> Cloudflare Edge -> Tunnel -> Localhost:80 -> Nginx.

/ -> Memu Web (Optional Desktop Access).

/_matrix -> Synapse (API for Mobile App).

Mobile App Connectivity:
The App attempts to resolve smiths.memu.digital.

Remote: Connects via Cloudflare Tunnel.

Local (Future): Will connect via Split DNS for max speed.

Data Sovereignty Strategy

Storage

Location: /var/lib/docker/volumes/memu_*

Medium: NVMe SSD (ext4).

Backup Protocol (3-2-1)

Live: PostgreSQL WAL (Write Ahead Log).

Nightly: pg_dump to local compressed archive.

Offsite: Encrypted .tar.gz.enc pushed to User's Cloud Storage (Rclone) or Local USB.