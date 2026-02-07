#!/usr/bin/env python3
"""Add HTTPS server block to nginx config and reload."""
import subprocess, sys

CONF = "nginx/conf.d/default.conf"
TS = "memu-hub.tail5c57ce.ts.net"

with open(CONF) as f:
    c = f.read()

if "listen 443" in c:
    print("HTTPS block already exists, skipping")
    sys.exit(0)

# Extract everything between first { and last } (resolver + location blocks)
inner = c[c.index("{") + 1 : c.rindex("}")]

https_block = f"""
server {{
    listen 443 ssl;
    server_name {TS};
    ssl_certificate /etc/nginx/certs/{TS}.crt;
    ssl_certificate_key /etc/nginx/certs/{TS}.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
{inner}}}
"""

with open(CONF, "a") as f:
    f.write(https_block)

print("HTTPS block added to nginx config")
subprocess.run(["docker", "exec", "memu_proxy", "nginx", "-s", "reload"])
print(f"Done. HTTPS enabled at https://{TS}/")
