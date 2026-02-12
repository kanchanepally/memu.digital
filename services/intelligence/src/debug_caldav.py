
import logging
import os
import caldav
from urllib.parse import urlparse

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("debug_caldav")

# Config (simulate from config.py/env)
CALDAV_URL = os.environ.get("CALDAV_URL", "http://calendar/calendar/dav.php/")
USERNAME = os.environ.get("CALDAV_USERNAME", "memu")
PASSWORD = os.environ.get("CALDAV_PASSWORD", "password_placeholder")

print(f"--- Debugging CalDAV Connection ---")
print(f"URL: {CALDAV_URL}")
print(f"User: {USERNAME}")
print(f"Pass: {'*' * len(PASSWORD)}")

def test_connection():
    client = caldav.DAVClient(
        url=CALDAV_URL,
        username=USERNAME,
        password=PASSWORD
    )
    
    print("\n1. Testing Auto-Discovery (client.principal())...")
    try:
        principal = client.principal()
        print(f"SUCCESS: Found principal: {principal}")
        return principal
    except Exception as e:
        print(f"FAILURE: Auto-discovery failed: {e}")

    print("\n2. Testing Manual Principal URL Construction...")
    # Try the construction logic I added to calendar_tool.py
    base = CALDAV_URL.rstrip('/')
    # Baikal format: /principals/users/USERNAME/
    # But wait, CALDAV_URL is http://calendar/calendar/dav.php/
    # So base is http://calendar/calendar/dav.php
    
    # Let's try to parse the URL to be smart
    parsed = urlparse(CALDAV_URL)
    # Reconstruct base without user/calendar specifics if possible, but Baikal is weird.
    # Usually http://host/dav.php/principals/users/user/
    
    # Try strict Baikal path
    principal_url = f"{base}/principals/users/{USERNAME}/"
    print(f"Trying URL: {principal_url}")
    
    try:
        principal = client.principal(principal_url)
        print(f"Test 1 (Constructed): {principal}")
        cals = principal.calendars()
        print(f"SUCCESS: Found {len(cals)} calendars")
        for c in cals:
            print(f" - {c.name} (URL: {c.url})")
        return principal
    except Exception as e:
        print(f"FAILURE: Manual path failed: {e}")

    return None

if __name__ == "__main__":
    if PASSWORD == "password_placeholder":
        print("ERROR: Environment variables not set. Run inside container or set env vars.")
    else:
        test_connection()
