#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Memu System Repair & Migration Tool ===${NC}"
echo "This script will align your system to the correct configuration."
echo "WARNING: This will RESET the database to ensure correct branding."
echo "Your photos (stored in filesystem) and AI models will be preserved."
echo "Chat history and user accounts will be reset."
echo ""

# 1. Check Environment
# Safely extract variables without sourcing the whole file (avoids special char issues)
CLOUDFLARED_TOKEN=$(grep "^CLOUDFLARED_TOKEN=" .env | cut -d'=' -f2- | tr -d '"' | tr -d "'")
MEMU_DOMAIN=$(grep "^MEMU_DOMAIN=" .env | cut -d'=' -f2- | tr -d '"' | tr -d "'")
# Set default if missing
if [ -z "$UPLOAD_LOCATION" ]; then
    echo "UPLOAD_LOCATION not found, defaulting to ./immich_data"
    UPLOAD_LOCATION="./immich_data"
    # Append to .env so Docker sees it
    echo "UPLOAD_LOCATION=./immich_data" >> .env
fi

# Export variables so docker compose can see them (since we aren't sourcing .env)
export CLOUDFLARED_TOKEN
export MEMU_DOMAIN
export UPLOAD_LOCATION

if [ -z "$CLOUDFLARED_TOKEN" ]; then
    echo -e "${RED}Error: CLOUDFLARED_TOKEN is missing in .env${NC}"
    exit 1
fi

DOMAIN=${MEMU_DOMAIN:-rachandhari.memu.digital}
echo "Target Domain: $DOMAIN"

# 2. Stop Everything
echo -e "${GREEN}Stopping existing services...${NC}"
docker compose down --remove-orphans

# 3. Generate Configs
echo -e "${GREEN}Generating configuration files...${NC}"

# Nginx
cat > nginx/conf.d/default.conf <<EOF
server {
    listen 80;
    server_name localhost;

    location / {
        proxy_pass http://memu_element:80;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /_matrix {
        proxy_pass http://memu_synapse:8008;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        client_max_body_size 50M;
    }

    location /_synapse/client {
        proxy_pass http://memu_synapse:8008;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        client_max_body_size 50M;
    }
}
EOF

# Element
cat > element-config.json <<EOF
{
    "default_server_config": {
        "m.homeserver": {
            "base_url": "https://$DOMAIN",
            "server_name": "$DOMAIN"
        },
        "m.identity_server": {
            "base_url": "https://vector.im"
        }
    },
    "brand": "Memu",
    "show_labs_settings": true
}
EOF

# Synapse (Update existing file in place)
# We use sudo because it might be owned by root
echo "Updating Synapse config..."
sudo sed -i "s/server_name: .*/server_name: \"$DOMAIN\"/" synapse/homeserver.yaml
sudo sed -i 's/user: .*/user: memu_user/' synapse/homeserver.yaml
sudo sed -i 's/password: .*/password: memupass123/' synapse/homeserver.yaml
sudo sed -i 's/database: .*/database: synapse/' synapse/homeserver.yaml
sudo sed -i 's/host: .*/host: memu_postgres/' synapse/homeserver.yaml
# Enable registration
sudo sed -i 's/^#enable_registration:.*/enable_registration: true/' synapse/homeserver.yaml
sudo sed -i 's/^enable_registration_without_verification:.*/enable_registration_without_verification: true/' synapse/homeserver.yaml

# 4. Reset Database
echo -e "${GREEN}Resetting Database for clean slate...${NC}"
docker compose up -d memu_postgres
echo "Waiting for database to be ready..."
sleep 10

# Drop and Recreate DBs
docker exec memu_postgres psql -U memu_user -d immich -c "DROP DATABASE IF EXISTS synapse;"
docker exec memu_postgres psql -U memu_user -d immich -c "CREATE DATABASE synapse OWNER memu_user LC_COLLATE='C' LC_CTYPE='C' TEMPLATE=template0;"
# Ensure Immich DB exists (it should, but just in case)
docker exec memu_postgres psql -U memu_user -d immich -c "CREATE DATABASE immich OWNER memu_user;" || true

# 5. Start Full Stack
echo -e "${GREEN}Starting full Memu stack...${NC}"
docker compose up -d

echo "Waiting for services to stabilize (20s)..."
sleep 20

# 6. User Registration
echo -e "${GREEN}=== User Registration ===${NC}"
echo "We need to create your Admin account."
read -p "Enter Admin Username (e.g. hareesh): " ADMIN_USER
read -s -p "Enter Admin Password: " ADMIN_PASS
echo ""

echo "Registering Admin..."
docker exec memu_synapse register_new_matrix_user -u "$ADMIN_USER" -p "$ADMIN_PASS" -a -c /data/homeserver.yaml http://localhost:8008

echo "Registering Bot..."
docker exec memu_synapse register_new_matrix_user -u "memu_bot" -p "botpass123" --no-admin -c /data/homeserver.yaml http://localhost:8008

# 7. Get Bot Token
echo "Generating Bot Token..."
BOT_TOKEN=$(curl -s -X POST http://localhost:8008/_matrix/client/r0/login \
  -H "Content-Type: application/json" \
  -d '{"type":"m.login.password","user":"memu_bot","password":"botpass123"}' | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$BOT_TOKEN" ]; then
    echo -e "${RED}Failed to get bot token. Check logs.${NC}"
else
    echo "Bot Token: $BOT_TOKEN"
    # Update docker-compose.yml with new token
    sed -i "s/MATRIX_BOT_TOKEN=.*/MATRIX_BOT_TOKEN=$BOT_TOKEN/" docker-compose.yml
    
    # Restart bot to pick it up
    docker compose restart memu_intelligence
fi

echo -e "${GREEN}=== Setup Complete! ===${NC}"
echo "1. Chat: https://$DOMAIN"
echo "2. Photos: http://<PI_IP>:2283 (Immich)"
echo "3. Admin User: @$ADMIN_USER:$DOMAIN"
echo "4. Bot User: @memu_bot:$DOMAIN"
