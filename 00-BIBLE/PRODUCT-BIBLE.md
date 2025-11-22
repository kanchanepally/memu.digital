Kin OS - Product Bible

The single source of truth for Kin OS development.
"Your kin, your network, your data."

1. Vision & Mission

The Problem: Families currently rent their digital lives from Big Tech. Their memories are mined for ads, their chats are metadata-harvested, and their history disappears when a cloud service shuts down.

The Solution: Kin OS.
We are not building just another messaging app. We are building a Private Digital Appliance (The Kin Hub) that gives a household complete ownership of their data, paired with a beautiful Super-App (Kin Mobile) that aggregates their digital life.

The Core Philosophy:

Identity vs. Infrastructure: We provide the address (smiths.ourkin.app), but the user owns the house (The Raspberry Pi).

Sovereignty: If our company goes bankrupt tomorrow, the user's Kin Hub must keep working forever.

Zero-Terminal: The user should never see a command line.

One App Rule: The user downloads one app ("Kin"), not three (Element, Immich, WebUI).

2. The Architecture: "Kin Hub"

The Kin Hub is a Raspberry Pi 5 (with NVMe SSD) running Kin OS.

The "Magic" Setup Flow

Plug in: User connects Power & Ethernet.

Discover: User visits http://kin.local on their phone.

Claim: User creates their family identity (e.g., rachandhari).

Live: The system configures the Cloudflare Tunnel, secures the SSL, and launches https://rachandhari.ourkin.app.

3. Core Features (The "Kin Super-App")

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