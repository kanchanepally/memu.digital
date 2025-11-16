# **Technical & Solution Design: The Hearth Hub**

Version: 1.0 (Household MVP)  
Date: 15 September 2025  
Author: The CTO  
Project Code Name: Kith

### **1\. Architectural Principles**

1. **Physical Sovereignty:** All user data resides on user-owned hardware.  
2. **Zero-Knowledge:** The company has no technical ability to access user content.  
3. **Appliance-like Simplicity:** The system is designed for reliability and requires zero user maintenance.  
4. **Open Standards:** Core communication is built on the Matrix protocol to ensure security and prevent lock-in.

### **2\. Hardware Specification**

The hardware plan is phased to accelerate development while ensuring a production-ready final product.

* **Phase A \- Prototype Hardware (Your Current Kit):**  
  * **Device:** Raspberry Pi 5  
  * **Storage:** 32GB Micro SD Card  
  * **Case:** Official Raspberry Pi 5 Case  
  * **Purpose:** To build and test the complete software stack in a real-world environment without delay. Sufficient for development and light household use for several months.  
* **Phase B \- Production Hardware (The Final Product):**  
  * **Device:** Raspberry Pi 5 (8GB Model)  
  * **Storage:** 1TB NVMe SSD  
  * **Case:** Custom-designed (or premium third-party like Argon ONE V3) fanless, metal enclosure.  
  * **Purpose:** This is the final, commercial-grade product. It offers the reliability, speed, and capacity required for long-term use as a family's primary digital archive.

### **3\. Software Stack (The Hearth OS)**

The Hearth Hub runs a custom "Hearth OS," which is a hardened Raspberry Pi OS Lite (64-bit) with a LUKS-encrypted filesystem. All services run as isolated containers via Docker Compose for security and manageability.

* **Container 1: Synapse (Matrix Server)**  
  * **Role:** The core communication server.  
  * **Configuration:** Deploys the latest official Synapse image.  
* **Container 2: PostgreSQL**  
  * **Role:** The database for Synapse and our other services.  
  * **Configuration:** A dedicated container running the official Postgres image, providing robust and reliable data storage far superior to the default SQLite.  
* **Container 3: Ollama**  
  * **Role:** The AI model service.  
  * **Configuration:** Runs the Ollama server, serving a small, efficient, quantized LLM. The initial target model is **Phi-3-mini-4k-instruct**, wrapped with a safety filter like Llama Guard.  
* **Container 4: Intelligence Service**  
  * **Role:** The "household brain." This is our proprietary software.  
  * **Configuration:** A custom **Python** application that reads from the PostgreSQL database, makes local API calls to the Ollama container for analysis, and writes structured data back to the database.  
* **Host Service: cloudflared**  
  * **Role:** The connectivity bridge.  
  * **Configuration:** Runs directly on the host OS as a system service. It creates a persistent, secure tunnel to the Cloudflare network, managed automatically by our central API.

### **4\. Multi-User Sovereignty Architecture**

To mitigate the risk of intra-household abuse, the system is designed with a strict separation of roles, enforced by encryption.

{  
  "hub\_admin": "Manages device settings, updates, backups",  
  "user\_accounts": \[  
    {  
      "user\_id": "user\_a",  
      "encryption\_key": "user\_a\_master\_key (inaccessible to admin)",  
      "data\_sovereignty": "Complete control over own conversations and data exports"  
    },  
    {  
      "user\_id": "user\_b",  
      "encryption\_key": "user\_b\_master\_key (inaccessible to admin)",  
      "data\_sovereignty": "Complete control over own conversations and data exports"  
    }  
  \]  
}

### **5\. Data Flow & Security**

* **Messaging:** The Hearth app on a user's phone establishes an E2EE connection via the Cloudflare Tunnel to the Synapse server on their Hub.  
* **AI Processing (Hearth Intelligence):** The Intelligence Service has read-only access to the message tables in the PostgreSQL database. It processes this data locally and makes API calls to http://ollama:11434. No data ever leaves the Hub for AI analysis.  
* **Backup (Hearth Bridge):** A nightly cron job on the Hub performs a pg\_dump of the database. The resulting file is encrypted locally using an encryption key stored only on the Hub. The encrypted blob is then uploaded to the user's connected cloud storage account via their API.