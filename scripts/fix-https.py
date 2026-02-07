#!/usr/bin/env python3
"""Regenerate nginx config with both HTTP and HTTPS server blocks."""
import subprocess

DOMAIN = "manam.memu.digital"
TS = "memu-hub.tail5c57ce.ts.net"
CONF = "nginx/conf.d/default.conf"

LOCATIONS = """
    # Static Assets (Memu branding)
    location /memu-assets/ {
        alias /usr/share/nginx/assets/;
        expires 7d;
        add_header Cache-Control "public, immutable";
    }

    # Admin & Setup Routes (Bootstrap Service)
    location ~ ^/(admin|setup|logout|welcome|api/|status) {
        set $upstream_bootstrap http://bootstrap:8888;
        proxy_pass $upstream_bootstrap;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $host;
    }

    # Matrix API
    location ~ ^/(_matrix|_synapse/client) {
        set $upstream_synapse http://synapse:8008;
        proxy_pass $upstream_synapse;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $host;
        client_max_body_size 50M;
    }

    # Calendar (Baikal CalDAV)
    location /calendar/ {
        set $upstream_calendar http://calendar:80;
        rewrite ^/calendar(/.*)$ $1 break;
        proxy_pass $upstream_calendar;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $host;
        client_max_body_size 50M;
    }

    # CalDAV/CardDAV discovery
    location /.well-known/caldav {
        return 301 $scheme://$host/calendar/dav.php;
    }

    location /.well-known/carddav {
        return 301 $scheme://$host/calendar/dav.php;
    }

    # Chat UI (Cinny) - catch-all
    location / {
        set $upstream_element http://element:80;
        proxy_pass $upstream_element;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header Host $host;
    }

    # Matrix server discovery
    location /.well-known/matrix/server {
        return 200 '{"m.server": "TSHOST:443"}';
        add_header Content-Type application/json;
    }

    # Matrix client discovery (dynamic scheme for HTTP/HTTPS)
    location /.well-known/matrix/client {
        return 200 '{"m.homeserver": {"base_url": "$scheme://$host"}}';
        add_header Content-Type application/json;
        add_header Access-Control-Allow-Origin *;
    }
""".replace("TSHOST", TS)

config = f"""server {{
    listen 80;
    server_name localhost;
    resolver 127.0.0.11 valid=30s;
{LOCATIONS}}}

server {{
    listen 443 ssl;
    server_name {TS};
    resolver 127.0.0.11 valid=30s;

    ssl_certificate /etc/nginx/certs/{TS}.crt;
    ssl_certificate_key /etc/nginx/certs/{TS}.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
{LOCATIONS}}}
"""

with open(CONF, "w") as f:
    f.write(config)

print("Nginx config written with HTTP + HTTPS blocks")

# Test config before reload
r = subprocess.run(
    ["docker", "exec", "memu_proxy", "nginx", "-t"],
    capture_output=True, text=True
)
print(r.stderr.strip())

if r.returncode == 0:
    subprocess.run(["docker", "exec", "memu_proxy", "nginx", "-s", "reload"])
    print(f"Nginx reloaded. HTTPS at https://{TS}/")
else:
    print("ERROR: nginx config test failed, not reloading")
