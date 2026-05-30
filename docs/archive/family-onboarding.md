# Family Member Onboarding - Feature Specification

**Status:** Planned
**Priority:** High
**Estimated Sessions:** 6-8
**Last Updated:** 2025-01-26

---

## 1. Overview

### 1.1 Problem Statement

After initial Memu setup, there's no easy way to add family members. Currently:

- No UI to create new Matrix accounts
- No way to generate Tailscale invites
- No "setup card" for new family members
- `memu-admin.sh` script exists but is incomplete
- Family members need technical help to join

This creates friction for the core use case: getting the whole family on the platform.

### 1.2 Solution

An admin panel accessible at `http://memu.local/admin/family` that allows:

1. **Add family member** - Create Matrix account, generate setup instructions
2. **Generate setup card** - QR code + instructions (printable or shareable)
3. **View family members** - See who's set up
4. **Manage access** - Disable/remove members if needed

Combined with a "Family Setup Card" - a simple page/PDF with everything a new member needs.

---

## 2. User Stories

### 2.1 Core Stories

| ID | As a... | I want to... | So that... |
|----|---------|--------------|------------|
| US1 | Family admin | add a new family member from a web page | I don't need terminal access |
| US2 | Family admin | generate a setup card for my spouse | they can set up their phone without my help |
| US3 | New family member | scan a QR code to join | setup is effortless |
| US4 | Family admin | see who's set up | I know everyone is connected |
| US5 | Family admin | disable a member's access | I can handle divorce/family changes |
| US6 | New member | get clear step-by-step instructions | I'm not confused about what apps to install |

### 2.2 User Interactions

**Adding a Family Member (US1):**
```
Admin navigates to: http://memu.local/admin/family

┌─────────────────────────────────────────────────────────────┐
│  Family Members                               [Add Member]  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 👤 Dad (you)           Admin    ✓ Active           │   │
│  │    @dad:family.memu.local                          │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 👤 Mom                 Member   ✓ Active           │   │
│  │    @mom:family.memu.local       [Setup Card]       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 👤 Kids                Member   ○ Not set up       │   │
│  │    @kids:family.memu.local      [Setup Card]       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Add Member Dialog:**
```
┌─────────────────────────────────────────────────────────────┐
│  Add Family Member                                    [X]   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Display Name: [Mom                    ]                   │
│                                                             │
│  Username:     [mom                    ]                   │
│                @mom:family.memu.local                      │
│                                                             │
│  Temporary Password: [Auto-generate ▼]                     │
│                      abc123xyz                             │
│                                                             │
│  [ ] Send Tailscale invite email                          │
│      Email: [mom@gmail.com           ]                    │
│                                                             │
│                              [Cancel]  [Create & Generate] │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Setup Card (US2, US3, US6):**
```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│              Welcome to Our Family Hub!                     │
│                                                             │
│  ┌─────────┐                                               │
│  │ QR CODE │  Scan this with your phone camera             │
│  │         │  to download Tailscale                        │
│  └─────────┘                                               │
│                                                             │
│  Step 1: Install Tailscale                                 │
│  ────────────────────────                                  │
│  Scan the QR code above, or search "Tailscale"            │
│  in your app store. Sign in with Google/Apple.            │
│                                                             │
│  Step 2: Install Element (Chat)                            │
│  ────────────────────────────                              │
│  Search "Element" in your app store.                       │
│                                                             │
│  When it asks for a server, enter:                         │
│  ┌─────────────────────────────────┐                       │
│  │ https://family.memu.local      │                       │
│  └─────────────────────────────────┘                       │
│                                                             │
│  Your login:                                               │
│  Username: mom                                              │
│  Password: abc123xyz (you'll change this)                  │
│                                                             │
│  Step 3: Install Immich (Photos)                           │
│  ────────────────────────────────                          │
│  Search "Immich" in your app store.                        │
│                                                             │
│  Server: https://family.memu.local:2283                    │
│  (Create account with same email)                          │
│                                                             │
│  Questions? Ask Dad!                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Architecture

### 3.1 Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      FAMILY ONBOARDING SYSTEM                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────┐                                                   │
│  │   Web Browser    │                                                   │
│  │ /admin/family    │                                                   │
│  └────────┬─────────┘                                                   │
│           │                                                             │
│           ▼                                                             │
│  ┌──────────────────┐        ┌───────────────────────────────┐         │
│  │  Admin Panel     │        │   Family Manager              │         │
│  │  (Flask routes)  │───────▶│   (Python module)             │         │
│  │                  │        │                               │         │
│  │  - List members  │        │   - Create Matrix user        │         │
│  │  - Add member    │        │   - Generate temp password    │         │
│  │  - Setup card    │        │   - Generate setup card       │         │
│  │  - Disable       │        │   - Check user status         │         │
│  └──────────────────┘        └───────────────┬───────────────┘         │
│                                              │                          │
│                                              ▼                          │
│  ┌───────────────────────────────────────────────────────────┐         │
│  │                    Matrix Synapse                         │         │
│  │                                                           │         │
│  │   Admin API:                                              │         │
│  │   - POST /_synapse/admin/v2/users/{user_id}              │         │
│  │   - GET /_synapse/admin/v2/users                         │         │
│  │   - PUT /_synapse/admin/v1/deactivate/{user_id}          │         │
│  │                                                           │         │
│  └───────────────────────────────────────────────────────────┘         │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────┐         │
│  │                    Setup Card Generator                   │         │
│  │                                                           │         │
│  │   - HTML template with instructions                       │         │
│  │   - QR code generation (qrcode library)                  │         │
│  │   - PDF export option (weasyprint)                       │         │
│  │   - Shareable link option                                │         │
│  │                                                           │         │
│  └───────────────────────────────────────────────────────────┘         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.2 API Routes

| Route | Method | Purpose |
|-------|--------|---------|
| `/admin/family` | GET | Family management page |
| `/admin/family/members` | GET | JSON list of family members |
| `/admin/family/add` | POST | Create new family member |
| `/admin/family/card/<username>` | GET | Setup card HTML |
| `/admin/family/card/<username>/pdf` | GET | Setup card PDF |
| `/admin/family/disable/<username>` | POST | Disable member |
| `/admin/family/enable/<username>` | POST | Re-enable member |

### 3.3 File Structure

```
memu-os/
├── bootstrap/
│   ├── app.py                    # MODIFY: Add family routes
│   ├── family_manager.py         # NEW: Family management logic
│   └── templates/
│       ├── family.html           # NEW: Family management page
│       └── setup_card.html       # NEW: Setup card template
│
├── services/
│   └── intelligence/
│       └── src/
│           └── bot.py            # MODIFY: Add /family-status command
│
└── scripts/
    └── memu-admin.sh             # MODIFY: Improve CLI tool
```

---

## 4. Success Criteria

### 4.1 Functional Requirements

| Requirement | Metric | Test Method |
|-------------|--------|-------------|
| Create user | Account created in Synapse | Login test |
| Setup card | Contains all required info | Manual review |
| QR code works | Scans correctly | Phone test |
| PDF export | Clean, printable | Print test |
| User list | Shows all accounts | Compare with Synapse |
| Disable works | User can't login | Login test |

### 4.2 Definition of Done

- [ ] Admin can create new family member from web UI
- [ ] Setup card generates with correct info
- [ ] QR codes scan and work
- [ ] PDF export looks good printed
- [ ] Can disable/enable users
- [ ] Non-technical family member can follow setup card
- [ ] Documentation updated

---

## 5. Implementation Plan

### 5.1 Sessions

| Session | Deliverable | Effort |
|---------|-------------|--------|
| 1 | Family manager module (Synapse API integration) | 2 hours |
| 2 | Family management page (list, add form) | 2 hours |
| 3 | Setup card template | 2 hours |
| 4 | QR code generation | 1 hour |
| 5 | PDF export | 1 hour |
| 6 | Disable/enable functionality | 1 hour |
| 7 | Bot /family-status command | 30 min |
| 8 | Documentation and QA | 1 hour |

### 5.2 Session Details

**Session 1: Family Manager Module**
- Create `family_manager.py`
- Synapse Admin API client
- Methods: create_user(), list_users(), deactivate_user(), reactivate_user()
- Generate secure temporary passwords

**Session 2: Family Management Page**
- Create `family.html` template
- List current family members with status
- "Add Member" form with validation
- Integration with family_manager.py

**Session 3: Setup Card Template**
- Create `setup_card.html`
- Step-by-step instructions
- Placeholders for server URL, username, password
- Mobile-friendly design
- Print-friendly CSS

**Session 4: QR Code Generation**
- Add `qrcode` library to requirements
- Generate QR for Tailscale download
- Generate QR for server URL
- Embed in setup card

**Session 5: PDF Export**
- Add `weasyprint` library (or simpler alternative)
- PDF generation endpoint
- Proper formatting for print

**Session 6: Disable/Enable**
- Deactivate endpoint using Synapse Admin API
- Reactivate endpoint
- UI buttons for disable/enable
- Confirmation dialog

**Session 7: Bot Command**
- Add `/family-status` command
- Show count of active members
- Show recent joins

**Session 8: Documentation**
- Update user guide with family management section
- Add screenshots
- Test with non-technical user

---

## 6. Technical Details

### 6.1 Synapse Admin API

**Create User:**
```python
async def create_user(username: str, password: str, display_name: str):
    user_id = f"@{username}:{SERVER_NAME}"

    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{SYNAPSE_URL}/_synapse/admin/v2/users/{user_id}",
            headers={"Authorization": f"Bearer {ADMIN_TOKEN}"},
            json={
                "password": password,
                "displayname": display_name,
                "admin": False,
                "deactivated": False
            }
        )
    return response.status_code == 200
```

**List Users:**
```python
async def list_users():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SYNAPSE_URL}/_synapse/admin/v2/users",
            headers={"Authorization": f"Bearer {ADMIN_TOKEN}"},
            params={"guests": "false"}
        )
    return response.json().get("users", [])
```

### 6.2 Setup Card Data

```python
@dataclass
class SetupCard:
    display_name: str
    username: str
    password: str
    server_url: str
    tailscale_invite_url: Optional[str]
    immich_url: str
    admin_contact: str

    def to_dict(self):
        return {
            "name": self.display_name,
            "username": self.username,
            "password": self.password,
            "chat_server": self.server_url,
            "photos_server": self.immich_url,
            "tailscale_url": self.tailscale_invite_url or "https://tailscale.com/download",
            "help_contact": self.admin_contact
        }
```

### 6.3 QR Code Generation

```python
import qrcode
import io
import base64

def generate_qr_base64(url: str) -> str:
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode()
```

---

## 7. Security Considerations

- Admin panel only accessible via Tailscale
- Temporary passwords should be random and strong
- Password change required on first login (future enhancement)
- Admin token stored securely
- Disable doesn't delete data (reversible)

---

## 8. Future Enhancements

- Email invitations with setup link
- Tailscale invite integration (API)
- Password change enforcement
- Family roles (admin, parent, child)
- Usage stats per member
- Profile photos
- Invite link (magic link instead of password)

---

## Appendix: Existing Code

**memu-admin.sh (incomplete):**
```bash
# Current script has stubs but doesn't work
# Needs to be connected to Synapse Admin API
```

**Bootstrap already has user creation:**
```python
# In app.py, bot user is created during setup
# Same pattern can be used for family members
```
