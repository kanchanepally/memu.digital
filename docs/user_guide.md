# Memu OS - User Guide

Welcome to your new **Digital Sanctuary**. This guide will help you set up your Memu device and reclaim your family's data sovereignty.

## 📦 1. Unboxing & Connections

Your Memu device is designed to be a "Headless Appliance" (no monitor or keyboard required).

1.  **Ethernet (Required for Setup):** Connect the Memu device to your home router using the provided Ethernet cable.
    *   *Note: WiFi can be configured later, but a wired connection is recommended for speed and stability.*
2.  **Power:** Connect the USB-C power supply.
3.  **Wait:** Allow 2-3 minutes for the system to boot up and initialize.

## 🛠️ 2. Prerequisites

Before you start the software setup, you need two things:

1.  **A Domain Name:** You need a web address for your family (e.g., `thesmiths.com` or `smith-family.net`). You can buy one from Namecheap, GoDaddy, or Cloudflare.
2.  **A Tailscale Account (Free):** We use Tailscale to securely tunnel your device to the internet without opening dangerous ports on your router.
    *   Create a free account at [tailscale.com](https://tailscale.com).
    *   Go to **Settings > Keys**.
    *   Generate an **Auth Key**.
    *   **Copy the Auth Key** (it looks like `tskey-auth-...`). You will need this in the next step.

## 🚀 3. The Setup Wizard

1.  Open a web browser on your phone or laptop (must be on the same WiFi as the Memu device).
2.  Visit: **http://memu.local**
3.  You will see the **Memu Setup Wizard**.
4.  Enter the following details:
    *   **Family Name:** (e.g., "Smiths"). This will create your local address.
    *   **Admin Password:** Create a strong password. This will be used for the "admin" account.
    *   **Tailscale Auth Key:** (Optional) Paste the key you generated earlier.
5.  Click **"Create My Family Server"**.

The system will now configure itself. This takes about **5-10 minutes**. Do not unplug the device.

## 📱 4. Connecting Your Apps

Once the installation is complete, your system is live at `https://<your-family>.memu.digital` (or your custom domain).

### **Chat (Element)**
1.  Download **Element X** (iOS/Android).
2.  Select **"Change Server"**.
3.  Enter your domain: `https://<your-family>.memu.digital`
4.  Login with:
    *   **Username:** `@admin:<your-family>.memu.digital`
    *   **Password:** (The one you created in the Wizard).

### **Photos (Immich)**
1.  Download **Immich** (iOS/Android).
2.  Enter Server URL: `https://<your-family>.memu.digital`
3.  Login with the same Admin credentials.
4.  Enable **Background Backup** to start saving your photos.

### **AI Assistant**
1.  Open the **Element** app.
2.  Start a new chat.
3.  Search for `@memu_bot:<your-family>.memu.digital`.
4.  Say "Hello!" to test your local AI.

## 📶 5. Switching to WiFi (Optional)

Memu works best on Ethernet. However, if you need to move the device to a location without a cable, you can configure WiFi.

**Note:** This step currently requires a keyboard and monitor attached to the Pi, or SSH access.

1.  **Access the Terminal:**
    *   Plug a keyboard and monitor into the Raspberry Pi.
    *   Login with username: `memu-user` (or your default user) and password.
2.  **Open Network Manager:**
    Run the following command:
    ```bash
    sudo nmtui
    ```
3.  **Connect:**
    *   Select **"Activate a connection"**.
    *   Choose your WiFi network from the list.
    *   Enter your WiFi password.
4.  **Finish:**
    *   Once connected (you see a `*` next to the network), select **<Back>** and then **<Quit>**.
    *   You can now unplug the Ethernet cable.

---

## ❓ Troubleshooting

*   **Can't reach http://memu.local?**
    *   Ensure your phone/laptop is on the same network as the Memu device.
    *   Try accessing it via the IP address (check your router's device list for "memu" or "raspberrypi").
*   **Cloudflare Tunnel not connecting?**
    *   Verify you copied the correct token.
    *   Ensure your domain DNS in Cloudflare points to the Tunnel (CNAME record).

---
*Welcome home.*
