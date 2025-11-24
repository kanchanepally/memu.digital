#!/bin/bash
# Switches from Bootstrap Mode to Production Mode

FAMILY_SLUG=$1
# Get the directory where the script is located, then go up one level to root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 1. Generate Nginx Config
# We reuse the logic from the install script, but purely for the config generation
mkdir -p $PROJECT_ROOT/nginx/conf.d

cat > $PROJECT_ROOT/nginx/conf.d/default.conf << NGINXEOF
server {
    listen 80;
    server_name localhost;

    location / {
        proxy_pass http://memu_element:80;
        proxy_set_header Host \$host;
        proxy_set_header X-Forwarded-For \$remote_addr;
    }

    location ~ ^/(_matrix|_synapse/client) {
        proxy_pass http://memu_synapse:8008;
        proxy_set_header X-Forwarded-For \$remote_addr;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header Host \$host;
        client_max_body_size 50M;
    }

    location /.well-known/matrix/server {
        return 200 '{"m.server": "${FAMILY_SLUG}.memu.digital:443"}';
        add_header Content-Type application/json;
    }

    location /.well-known/matrix/client {
        return 200 '{"m.homeserver": {"base_url": "https://${FAMILY_SLUG}.memu.digital"}}';
        add_header Content-Type application/json;
        add_header Access-Control-Allow-Origin *;
    }
}
NGINXEOF

# 2. Generate Element Config
cat > $PROJECT_ROOT/element-config.json << ELEMENTEOF
{
    "default_server_config": {
        "m.homeserver": {
            "base_url": "https://${FAMILY_SLUG}.memu.digital",
            "server_name": "${FAMILY_SLUG}.memu.digital"
        }
    },
    "brand": "Memu",
    "default_theme": "light"
}
ELEMENTEOF

# 3. Stop the Setup Wizard
sudo systemctl stop memu-setup.service
sudo systemctl disable memu-setup.service

# 4. Start Production
cd $PROJECT_ROOT
docker compose up -d

# 5. Enable Production on Boot
sudo systemctl enable memu-production.service