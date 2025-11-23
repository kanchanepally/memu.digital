Memu OS 🏠

The operating system for your family.
Private chat, photos, and AI, hosted physically in your home.

What is Memu?

Memu OS turns a Raspberry Pi 5 into a Memu Hub—a private server for your family. It replaces WhatsApp, Google Photos, and iCloud with a system you actually own.

Private: Data never leaves your home unencrypted.

Simple: Setup via http://memu.local. No terminal required.

Resilient: Works offline. Automatic encrypted backups.

The Tech Stack

Core: Matrix (Synapse)

Database: PostgreSQL

Routing: Nginx + Cloudflare Tunnels

Client: Memu Mobile (React Native)

Intelligence: Ollama (Llama 3)

Installation (For Developers)

Prerequisites: Raspberry Pi 5, NVMe SSD.

Flash the OS:
Install Raspberry Pi OS Lite (64-bit).

Clone & Install:

git clone [https://github.com/kanchanepally/memu-os.git](https://github.com/kanchanepally/memu-os.git)
cd memu-os
./scripts/install.sh


Setup:
Visit http://memu.local (or the Pi's IP) to configure your family domain.

Roadmap

See Roadmap for the 90-day plan.

License

AGPL-3.0. Your data is yours. The code is open.