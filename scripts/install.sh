#!/bin/bash
# Memu OS Installation Script
# "Your family, your network, your data"

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔═══════════════════════════════════════╗${NC}"
echo -e "${BLUE}║        Welcome to Memu OS             ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════╝${NC}"
echo ""

# 1. Gather User Input
read -p "Enter your Family Name (e.g. smiths): " FAMILY_SLUG
DOMAIN="${FAMILY_SLUG}.memu.digital"
echo -e "Setting up Memu for: ${GREEN}${DOMAIN}${NC}"

# 2. Generate .env
echo "Generating secrets..."
DB_PASS=$(openssl rand -base64 24 | tr -d "=+/" | cut -c1-25)
SYNAPSE_TOKEN=$(openssl rand -hex 32)

cat > .env << ENVEOF
MEMU_DOMAIN=${DOMAIN}
DB_NAME=memu_core
DB_USER=memu_user
DB_PASSWORD=${DB_PASS}
SYNAPSE_ADMIN_TOKEN=${SYNAPSE_TOKEN}
ENABLE_REGISTRATION=true
TZ=Europe/London
ENVEOF

# 3. Generate Nginx Config (The Magic Routing Layer)
echo "Configuring internal network..."
mkdir -p nginx/conf.d

cat > nginx/conf.d/default.conf << NGINXEOF
server {
    listen 80;
    server_name localhost;

    # Route root traffic to Element (The App)
    location / {
        proxy_pass http://memu_element:80;
        proxy_set_header Host \$host;
        proxy_set_header X-Forwarded-For \$remote_addr;
    }

    # Route Matrix API traffic to Synapse (The Server)
    location ~ ^/(_matrix|_synapse/client) {
        proxy_pass http://memu_synapse:8008;
        proxy_set_header X-Forwarded-For \$remote_addr;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header Host \$host;
        client_max_body_size 50M;
    }

    # Auto-Discovery (Crucial for Login)
    location /.well-known/matrix/server {
        return 200 '{"m.server": "${DOMAIN}:443"}';
        add_header Content-Type application/json;
    }

    location /.well-known/matrix/client {
        return 200 '{"m.homeserver": {"base_url": "https://${DOMAIN}"}}';
        add_header Content-Type application/json;
        add_header Access-Control-Allow-Origin *;
    }
}
NGINXEOF

# 4. Generate Element Config
cat > element-config.json << ELEMENTEOF
{
    "default_server_config": {
        "m.homeserver": {
            "base_url": "https://${DOMAIN}",
            "server_name": "${DOMAIN}"
        }
    },
    "brand": "Memu",
    "default_theme": "light"
}
ELEMENTEOF

echo ""
echo -e "${GREEN}Configuration complete!${NC}"
echo "To start Memu OS, run: docker compose up -d"