PART 2: TECHNICAL ARCHITECTURE
System Overview
┌─────────────────────────────────────────────┐
│         Hearth Mobile App (iOS/Android)     │
│         - React Native                      │
│         - Custom UI (NOT Element)           │
│         - Matrix SDK underneath             │
└─────────────┬───────────────────────────────┘
              │
              │ Matrix Protocol (E2EE)
              │
┌─────────────▼───────────────────────────────┐
│         Raspberry Pi 5 (User's Home)        │
│  ┌─────────────────────────────────────┐   │
│  │  Synapse (Matrix Server)            │   │
│  │  PostgreSQL (Data Storage)          │   │
│  │  Hearth Services (Photos/Tasks/AI)  │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
Core Technology Stack
Backend (Raspberry Pi)

OS: Raspberry Pi OS Lite (64-bit, Bookworm)
Container Engine: Docker Compose
Matrix Server: Synapse (latest stable)
Database: PostgreSQL 15
Reverse Proxy: Caddy 2 (auto-HTTPS)
AI: Ollama with Phi-3-mini (Week 2+)
Language: Python 3.11 for services

Mobile App (Custom - NOT Element)

Framework: React Native (latest stable)
Matrix SDK: matrix-js-sdk
State Management: Zustand (simple, not Redux)
UI Library: React Native Paper (Material Design)
Navigation: React Navigation 6
Image Handling: react-native-image-picker + react-native-fast-image
Local Storage: @react-native-async-storage/async-storage
Network: Axios for REST, Matrix SDK for real-time

Design System

Inspiration: WhatsApp (familiar), Signal (clean), Telegram (fluid)
NOT Element: Avoid their UX mistakes entirely
Colors: Warm, inviting (not corporate blue)
Typography: SF Pro (iOS), Roboto (Android)
Animations: Smooth, 60fps, delightful micro-interactions

Key Architectural Principles
1. Zero Cloud Dependency
❌ NO: AWS, Google Cloud, Azure, Cloudflare Workers
✅ YES: User's Pi, user's network, user's control
⚠️ MAYBE: Cloudflare Tunnel (for remote access only, not data storage)
2. Offline-First Design
The app MUST work when:
- Pi is offline (queued messages)
- Phone is offline (cached data)
- Internet is down (local network still works)
3. Appliance-Like Simplicity
Setup flow (total time: 5 minutes):
1. Plug in Pi
2. Open Hearth app
3. Scan QR code from Pi
4. Done
No "homeserver" configuration. No server URLs. No technical jargon.
4. Privacy by Architecture
User data paths:
✅ Phone → Local WiFi → Pi (encrypted)
✅ Pi → User's chosen backup (encrypted)
❌ NEVER: Phone → Our servers → Pi
❌ NEVER: Any telemetry without explicit opt-in