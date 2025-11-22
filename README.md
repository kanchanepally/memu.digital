Kin OS 🏠

The operating system for your family.
Private chat, photos, and AI, hosted physically in your home.

What is Kin?

Kin OS turns a Raspberry Pi 5 into a Kin Hub—a private server for your family. It replaces WhatsApp, Google Photos, and iCloud with a system you actually own.

Private: Data never leaves your home unencrypted.

Simple: Setup via http://kin.local. No terminal required.

Resilient: Works offline. Automatic encrypted backups.

The Tech Stack

Core: Matrix (Synapse)

Database: PostgreSQL

Routing: Nginx + Cloudflare Tunnels

Client: Kin Mobile (React Native)

Intelligence: Ollama (Llama 3)

Installation (For Developers)

Prerequisites: Raspberry Pi 5, NVMe SSD.

Flash the OS:
Install Raspberry Pi OS Lite (64-bit).

Clone & Install:

git clone [https://github.com/kanchanepally/kin-os.git](https://github.com/kanchanepally/kin-os.git)
cd kin-os
./scripts/install.sh


Setup:
Visit http://kin.local (or the Pi's IP) to configure your family domain.

Roadmap

See Roadmap for the 90-day plan.

License

AGPL-3.0. Your data is yours. The code is open.