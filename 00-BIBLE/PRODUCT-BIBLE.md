Memu OS - Product Bible

The single source of truth for Memu OS development.
"Your family, your network, your data."

1. Vision & Mission

The Problem: Families currently rent their digital lives from Big Tech. Their memories are mined for ads, their chats are metadata-harvested, and their history disappears when a cloud service shuts down.

The Solution: Memu OS.
We are not building just another messaging app. We are building a Private Digital Appliance (The Memu Hub) that gives a household complete ownership of their data, paired with a beautiful Super-App (Memu Mobile) that aggregates their digital life.

The Core Philosophy:

Identity vs. Infrastructure: We provide the address (smiths.memu.digital), but the user owns the house (The Raspberry Pi).

Sovereignty: If our company goes bankrupt tomorrow, the user's Memu Hub must keep working forever.

Zero-Terminal: The user should never see a command line.

One App Rule: The user downloads one app ("Memu"), not three (Element, Immich, WebUI).

2. The Architecture: "Memu Hub"

The Memu Hub is a Raspberry Pi 5 (with NVMe SSD) running Memu OS.

The "Magic" Setup Flow

Plug in: User connects Power & Ethernet.

Discover: User visits http://memu.local on their phone.

Claim: User creates their family identity (e.g., smiths).

Live: The system configures the Cloudflare Tunnel, secures the SSL, and launches https://smiths.memu.digital.

3. Core Features (The "Memu Super-App")

A. Chat (The Communication Layer)

User Value: "WhatsApp, but you own the server."

Tech: Synapse (Backend) + Matrix SDK (Mobile App).

Experience: Native React Native UI. No "Matrix" branding visible to the user.

Requirement: End-to-End Encrypted by default.

B. Memories (The Storage Layer)

User Value: "Google Photos, but full quality and private."

Tech: Immich (Backend) + Custom React Native View.

Requirement: Background backup from mobile.

C. Assistant (The Intelligence Layer)

User Value: "A smart assistant that knows your family but tells no one else."

Tech: Ollama (Llama 3) running locally.

Requirement: Runs 100% offline on the NPU/CPU.

4. Engineering Constraints

Storage: NVMe SSD is mandatory. SD Cards are for boot only.

Backups: Automated nightly backups (Encrypted) to local USB or User's Cloud.

Routing: Nginx handles all internal traffic. Direct port exposure is forbidden.

OS: Based on Raspberry Pi OS Lite (Debian Bookworm).

5. Target Persona

"The Conscious Parent"
They are not hackers. They can set up a Sonos speaker, but they cannot configure a firewall. They are worried about their kids' digital footprint.

The "Mum Test":
If setting it up requires reading a GitHub README, we have failed.