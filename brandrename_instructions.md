# **Memu Rebrand Execution Protocol**

Objective: Fully rebrand the codebase from "Kin" (or previously called "Hearth" as part of our Version 1) to **Memu**.  
Scope: Server OS (memu-os) and Mobile App (memu-mobile).

## **Phase 1: File System Structure**

1. **Rename Root Directories:**  
   * Rename folder kin-os → memu-os  
   * Rename folder kin-mobile → memu-mobile

## **Phase 2: Server & Infrastructure (memu-os)**

**Action:** Perform a global find-and-replace within the memu-os directory.

### **A. Global String Replacements (Case Sensitive)**

| Find | Replace | Context |
| :---- | :---- | :---- |
| ourkin.app | memu.digital | Public Domain |
| kin.local | memu.local | Internal Discovery Domain |
| KIN\_DOMAIN | MEMU\_DOMAIN | Env Variables |
| kin\_ | memu\_ | Docker Container/Volume Prefixes |
| kin- | memu- | Service/Script Prefixes |

### **B. File-Specific Updates**

1. **docker-compose.yml**  
   * Update all service names (e.g., kin\_synapse → memu\_synapse).  
   * Update volume names (e.g., kin\_postgres\_data → memu\_postgres\_data).  
   * Update network names (e.g., kin\_net → memu\_net).  
   * Ensure container names match the new memu\_ prefix.  
2. **.env.example**  
   * Rename variable KIN\_DOMAIN to MEMU\_DOMAIN.  
   * Set default value to family.memu.digital.  
3. **scripts/install.sh & scripts/launch\_production.sh**  
   * Update PROJECT\_ROOT variable to point to /home/hareesh/memu-os.  
   * Ensure Nginx generation block references http://memu\_element:80 and http://memu\_synapse:8008.  
   * Update systemd service references to memu-setup.service and memu-production.service.  
4. **bootstrap/app.py**  
   * Update PROJECT\_ROOT path.  
   * Update the .env generation logic to write MEMU\_DOMAIN.  
   * Update the subdomain construction logic to append .memu.digital.  
5. **systemd/\*.service**  
   * Rename files:  
     * kin-setup.service → memu-setup.service  
     * kin-production.service → memu-production.service  
   * Inside files: Update WorkingDirectory to /home/hareesh/memu-os.  
   * Update Description to "Memu OS ...".  
6. **nginx/conf.d/default.conf (if exists)**  
   * Ensure upstream proxies point to memu\_element and memu\_synapse.

## **Phase 3: Mobile Application (memu-mobile)**

**Action:** Update app identity and configuration.

1. **app.json**  
   * name: "Memu"  
   * slug: "memu"  
   * scheme: "memu"  
   * package: "com.memu.app"  
   * version: "1.0.0"  
2. **App.js & Components**  
   * **Text Replacement:** Change "KIN" to "MEMU" in headers/logos.  
   * **Tagline:** Change to "In a world of iClouds, be Memu."  
   * **Placeholder Text:** Change rachandhari.ourkin.app to rachandhari.memu.digital.

## **Phase 4: Final Verification**

1. **Search:** Run a grep/search for the string "kin" (case-insensitive) across the entire workspace.  
   * *Expected Result:* Zero matches (except perhaps in git history or this instruction file).  
2. **Test:** Ensure install.sh runs without error and generates a .env file with MEMU\_DOMAIN.