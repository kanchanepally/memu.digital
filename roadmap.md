Memu OS: 90-Day Execution Plan

Current Phase: Productization & Mobile MVP
Status: Foundation Secure (Memu OS v0.1)

PHASE 1: The "Ironclad" Foundation (Weeks 1-4)

Goal: Stable hardware, zero data loss, one-click setup.

[x] Week 1: Prototype: Prove the Stack (Docker, Synapse, Postgres).

[x] Week 2: The Pivot: Rebrand to Memu, implement Nginx, launch memu.digital.

[ ] Week 3: The Hardware Standard:

Migrate to NVMe SSD (Reliability).

Finalize "Golden Image" for SD Cards.

Validate http://memu.local bootstrap wizard on real hardware.

[ ] Week 4: The Safety Net:

Verify backup.sh (Encrypted nightly dumps).

Test "Disaster Recovery" (Flash new drive -> Restore data).

PHASE 2: The "Memu Mobile" Build (Weeks 5-8)

Goal: Build the Super-App. No more generic clients.

[ ] Week 5: Mobile Core (React Native):

Scaffold the "Super-App" structure (Expo).

Implement "Connect to Home" (Auth flow against Synapse).

[ ] Week 6: Chat MVP:

Integrate Matrix SDK.

Build "Chat List" and "Message View" (Native UI).

Milestone: Send a message from the Memu App to the Pi.

[ ] Week 7: Memories MVP:

Deploy Immich container to the stack.

Build "Photo Feed" tab in the Mobile App.

Implement basic photo upload.

[ ] Week 8: Alpha Testing:

Give a pre-flashed Memu Hub to 1 non-technical friend.

Observe their setup process silently.

PHASE 3: Intelligence & Launch (Weeks 9-12)

Goal: Add the "Wow" factor.

[ ] Week 9: Local AI (Ollama):

Enable Llama 3 container.

Build "Assistant" tab in Mobile App.

[ ] Week 10: Marketing Push:

Film the promo video using the Alpha unit.

Update memu.digital with real app screenshots.

[ ] Week 11: Beta Batch:

Flash 10 SSDs.

Ship to early access list.

[ ] Week 12: Public Launch:

Open orders for "Memu Hub Kit".

"Kill List" (What we are NOT doing yet)

Element Branding: We are not skinning Element anymore. We are building native.

Federation: We are not trying to talk to other Matrix servers yet. Isolation is a feature.

Video Calls: Too heavy for V1. Text and Photos only.