<div align="center">

# **Memu**

### **Your Family. Your Network. Your Data.**

**The convenience of iCloud, with the sovereignty of a hard drive.**

[Getting Started](#getting-started) • [The Manifesto](#the-manifesto-from-privacy-to-sanctuary) • [The Memu Suite](#the-memu-suite) • [Architecture](#architecture)

</div>

## **The Manifesto: From Privacy to Sanctuary**

We do not sell "Privacy Tech" (which implies hiding). We sell **Digital Real Estate** (which implies ownership).

**Memu** (Telugu: *We*) is a **Digital Sanctuary**: A physical vault in your home where your data lives, protected from Big Tech surveillance and commercial exploitation. It is the server for *us*, not just *me*.

We reject the false choice between Safety and Privacy. We enforce safety at the **Edge** (The Device), not the Cloud.

* **Local Intelligence:** All AI processing happens on your device.  
* **Zero Telemetry:** We do not track user activity.  
* **Ownership:** You own the hardware. You own the data.

### **Why I Built This**

"I am a parent who got tired of my family's private moments being mined to sell us things. I wanted the convenience of the cloud, but with the safety of a photo album on a shelf. Memu is that shelf." — *Founder, Memu Digital*

### **Inspired by Giants**

Memu stands on the shoulders of the **Solid Project** and Sir Tim Berners-Lee's vision for a decentralized web.

* **Solid** defines the protocol for data sovereignty (Pods).  
* **Memu** builds the *appliance* that makes that sovereignty accessible to non-technical families today.

## **What is Memu?**

Memu is a vertically integrated **Private Cloud Appliance**. It transforms commodity hardware (like a Raspberry Pi 5\) into a beautiful, silent, and sovereign home server.

It is designed not for system administrators, but for families. It provides three core services, pre-configured and integrated instantly:

### **1\. Memu Chat (Communication)**

A private living room for your digital conversations.

* **User Story:** "I want to text my family privately, with no data mining."  
* **Engine:** Matrix Synapse (End-to-End Encrypted).  
* **Interface:** Uses the native **Element X** app on your phone.

### **2\. Memu Photos (The Vault)**

Stop paying monthly rent for your own life history.

* **User Story:** "I want my camera roll backed up automatically to my own drive."  
* **Engine:** Immich (High-performance Go/Node).  
* **Interface:** Uses the native **Immich** app for full mobile backup.

### **3\. Memu Intelligence (The Brain)**

A local AI utility that helps, but never spies.

* **User Story:** "I want a smart assistant that knows my family context but is private."  
* **Engine:** Ollama (Llama 3.2 3B) \+ Python Logic Bridge.  
* **Interface:** Chat with **@memu\_bot** to summarize days, set reminders, or manage lists.

## **The Memu Suite**

Instead of building a monolithic custom app, Memu deploys a "Super Stack" of industry-standard open protocols. This ensures your data is never locked into a proprietary format.

| Capability | Backend Engine | Frontend App (User) | Branding Strategy |
| :---- | :---- | :---- | :---- |
| **Photos** | **Immich** | **Immich Mobile App** | "Memu Photos" |
| **Chat** | **Matrix (Synapse)** | **Element X / Web** | "Memu Chat" |
| **Intelligence** | **Ollama \+ Python** | **Memu Bot (@memu\_bot)** | "Memu Assistant" |

## **Getting Started**

### **Hardware Requirements**

#### **Option A: The Memu Hub (Official Spec)**

Optimized for silence, power efficiency, and the "appliance" feel.

* **Server:** Raspberry Pi 5 (8GB RAM).  
* **Storage:** NVMe SSD (1TB recommended) via PCIe HAT.  
* **Power:** Official 27W USB-C Power Supply.  
* **AI:** *Ready for Raspberry Pi AI Kit (Hailo-8L).*

#### **Option B: The Pro Spec (x86 / Mini PC)**

For power users needing hardware video transcoding.
For the technical stewards (the "Chief Technology Officers" of the household), Memu is built on a transparent, audit-friendly stack.

* **Orchestration:** Docker Compose (memu-suite).  
* **Database:** Unified **PostgreSQL 15** (handling Synapse, Immich, and Intelligence data).  
* **Cache:** Redis 6.2.  
* **Ingress:** Nginx \+ Cloudflare Tunnel (Zero Trust).

### **Data Hierarchy**

We respect the distinction between *system* and *user*.

* /memu/system: The immutable OS code. Updated automatically via GitOps.  
* /memu/data: **The Holy Grail.** Your photos, database volumes, and config.  
  * *Backup Strategy:* You only ever need to backup /memu/data.

## **Roadmap**

We are currently in **Phase 3 (Refinement)**.

* ✅ **Foundation:** Hardware support, Docker stack, Matrix, Immich.  
* ✅ **Intelligence:** Local LLM integration, Python bot framework.  
* 🚧 **Refinement:** Backup automation, System Dashboard.  
* 🔮 **Expansion:** Home Assistant integration, Voice control, Federation.

## **License & Sovereignty**

**Memu is Open Source (AGPLv3).**

We believe that code used to store private family lives must be open to audit. You are free to inspect, modify, and host this software yourself.

* **Trademark:** "Memu" and the Memu logo are trademarks of Memu Digital.  
* **Telemetry:** Memu contains **zero** tracking. We do not know who you are, and we don't want to.

<div align="center"\>  
Built with ❤️ for families everywhere.  
</div\>
