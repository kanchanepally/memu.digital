# Memu: The Digital Sanctuary

## Trust, Safety, and Architecture Manifesto v2.0

**Authors:** Founder & CTO  
**Date:** November 2025  
**Classification:** Public Strategy Document

---

## 1. The Core Philosophy: From "Privacy" to "Sanctuary"

For the last decade, the technology industry has offered families a false choice: **Surveillance** or **Silence**.

*   **Option A (Big Tech):** You get convenience, magical search, and safety tools, but you pay with your data, your children's privacy, and monthly rent. You are a tenant in a digital landlord's house.
*   **Option B (Crypto/Privacy Tech):** You get total secrecy and anonymity, but you lose convenience, safety features, and the ability to find your own photos. You are a hermit in a bunker.

**Memu rejects this binary.** We are building a third way: **The Digital Sanctuary**.

We believe a family's digital life should be treated like their physical home:

*   **Ownership:** You own the walls (the hardware) and the furniture (the data). No one can evict you.
*   **Privacy:** What happens at the dinner table stays there. We don't put microphones in the walls.
*   **Safety:** You lock your front door. You don't let strangers in. You have rules for your kids.

> Memu is not an "Encrypted Bunker" for hiding from the police.  
> Memu is a "Private Sanctuary" for living freely without corporate surveillance.

## 2. Product Definition: The Anti-Cloud Appliance

Memu is a **Private Cloud Appliance** (Hardware + OS + App) that physically sits in the user's home.

*   **The Hub:** A Raspberry Pi 5 with NVMe storage. It holds the "Golden Copy" of all family data.
*   **The Network:** Devices connect directly to the Hub via encrypted tunnels.
*   **The Relationship:** Memu Inc. sells the toaster; we do not bake the bread. We provide the infrastructure for connection, but we do not possess the keys to decrypt the content.

## 3. The Safety Architecture: "Guardians at the Gate"

We acknowledge that total encryption creates risks (CSAM, abuse, crime). Unlike Signal or Telegram, which claim "we can't see anything, so it's not our problem," Memu takes active responsibility through **Edge-Based Safety**.

Since we control the hardware, we enforce safety at the **device level**, not the cloud level.

### A. Child Safety (The "Apple Model" Done Right)

We do not scan data in the cloud. Instead, the Memu Hub runs a local "Safety Driver"—a lightweight AI model optimized for the Raspberry Pi.

#### Local Hash Matching (CSAM Prevention)
*   **Mechanism:** When any file is written to the Memu Hub (via chat or photo backup), the Hub calculates its perceptual hash.
*   **The Check:** This hash is compared against a locally stored, compressed, and blinded blocklist of known harmful content (e.g., from NCMEC/IWF).
*   **The Action:** If a match is found, the file system rejects the write operation. The illegal file literally cannot be saved to the disk.
*   **Privacy:** The image never leaves the home. Memu Inc. never sees it.

#### Communication Safety (Bullying & Nudity)
*   **Mechanism:** On-device Computer Vision detects nudity or aggressive language in chats for child accounts.
*   **The Nudge:** The image is blurred before it is displayed. A prompt appears: *"This looks sensitive. Are you sure? Do you want to ask Dad/Mom?"*
*   **Empowerment:** This teaches digital resilience rather than just blocking. It keeps the parent in the loop without Memu Inc. acting as the global policeman.

### B. Domestic Abuse & Coercive Control Prevention

We recognize the risk of an abuser using a private server to control a victim or hide evidence.

*   **Immutable Audit Logs:** The Memu Hub maintains a strictly append-only log of administrative actions (e.g., "User X password changed," "Internet access disabled for Device Y").
    *   **Feature:** These logs cannot be deleted via the UI. If a device is seized by law enforcement, the pattern of digital control is visible, even if the chat content is encrypted.
*   **The "Panic Button" (Physical Reset):** A victim can trigger a "Safety Reset" (e.g., physical button combination on the box) that disconnects the Hub from the internet and locks the data, preserving evidence while stopping remote access by an abuser.
*   **Help Resources:** The app includes a "Safety Center" with resources on domestic violence and digital control, accessible via a discreet UI that doesn't log to the browser history.

### C. Criminal Deterrence (The "Paper Trail")

Memu is designed to be hostile to organized crime.

*   **Physical Liability:** Criminals prefer ephemeral cloud accounts. Memu requires a physical device in a physical location. **Possession of the Hub = Possession of the Evidence.** This is a massive deterrent for drug dealers or cartels.
*   **Identity Verification:** We require a valid payment method (Credit Card) for the Memu Relay service. We do not accept anonymous crypto payments. We verify the "Head of Household."
*   **Traffic Heuristics:** While we cannot read messages, our Relay analyzes traffic patterns.
    *   *Family Pattern:* Photos, sporadic chat, video calls.
    *   *Bot/Spam Pattern:* 10,000 text messages/hour, zero photos.
    *   *Action:* We aggressively ban accounts that violate "Fair Use" traffic patterns, effectively booting bad actors off our relay.

## 4. Technical Architecture & Data Guidelines

### The "Zero-Knowledge" Promise

*   **Encryption:** All data in transit is encrypted (TLS 1.3). All chat data is End-to-End Encrypted (Matrix/Olm).
*   **Storage:** Data at rest on the Hub is encrypted via LUKS (Linux Unified Key Setup), with keys managed by the user's password.
*   **Memu Inc. Access:** We have **ZERO** access to user content. We cannot reset passwords. We cannot recover deleted photos. We are the plumber, not the landlord.

### The "Tech-Legal" Stack

*   **Manufacturer Status:** We position ourselves legally as a hardware manufacturer. If a user commits a crime with a Samsung phone, Samsung is not liable. We apply the same logic to the Memu Hub.
*   **Terms of Service:** Our ToS explicitly prohibits illegal use. Because the software requires a license check to function fully (Relay/Updates), we reserve the right to "brick" the remote access of any user identified by law enforcement with a valid court order, isolating them to their local LAN.

## 5. Blue Sky: The Future of "Local AI"

We are not just replicating 2015-era safety. We are building 2030-era intelligence.

### The "Guardian Angel" Agent
We will train a Small Language Model (SLM) that runs entirely on the Raspberry Pi's NPU. This agent acts as a proactive family mediator.

*   **Context:** It reads the local, decrypted stream of data (because it lives inside the house).
*   **Capabilities:**
    *   **Scam Detection:** *"Dad, that message looks like a phishing attempt. Don't click the link."*
    *   **Tone Policing (Optional):** *"This message sounds very angry. Are you sure you want to send it to your daughter?"*
    *   **Mental Health Spotting:** *"It looks like [Child] hasn't left the house in 3 days and is sleeping late. Should we suggest a family walk?"*
*   **The Key:** This insight stays on the device. Memu Inc. never knows. It gives families the power of AI safety without the privacy invasion of Corporate AI.

---

**Summary**

Memu protects families from Big Tech's greed and from digital harm. We do this by moving the responsibility and the power from the **Cloud** (where it is dangerous and invasive) to the **Home** (where it is safe and controlled).