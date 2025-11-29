#!/bin/bash
set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                   Memu OS - One-Click Setup                  ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# 1. Prerequisites Check
echo -e "${BLUE}[1/6] Checking prerequisites...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker is ready${NC}"

# 2. Configuration
echo -e "\n${BLUE}[2/6] Configuration${NC}"
read -p "Enter your Domain Name (e.g. myfamily.memu.digital): " SERVER_NAME
if [ -z "$SERVER_NAME" ]; then
    echo -e "${RED}Domain name is required.${NC}"
    exit 1
fi

read -p "Enter Admin Username (default: admin): " ADMIN_USER
ADMIN_USER=${ADMIN_USER:-admin}

# Generate secure passwords
DB_PASSWORD=$(openssl rand -base64 24 | tr -d "=+/" | cut -c1-20)
ADMIN_PASSWORD=$(openssl rand -base64 24 | tr -d "=+/" | cut -c1-20)
BOT_PASSWORD=$(openssl rand -base64 24 | tr -d "=+/" | cut -c1-20)

echo -e "Generated secure passwords:"
echo -e "  Database: ${GREEN}Saved to .env${NC}"
echo -e "  Admin ($ADMIN_USER): ${GREEN}$ADMIN_PASSWORD${NC} (SAVE THIS!)"
echo -e "  Bot:      ${GREEN}Auto-managed${NC}"

# 3. Create .env
echo -e "\n${BLUE}[3/6] Creating environment file...${NC}"
cp .env.example .env

# Update .env with real values
# We use a temp file to avoid sed compatibility issues between macOS/Linux
sed "s|SERVER_NAME=.*|SERVER_NAME=${SERVER_NAME}|" .env > .env.tmp && mv .env.tmp .env
sed "s|DB_PASSWORD=.*|DB_PASSWORD=${DB_PASSWORD}|" .env > .env.tmp && mv .env.tmp .env
sed "s|MATRIX_BOT_USERNAME=.*|MATRIX_BOT_USERNAME=@memu_bot:${SERVER_NAME}|" .env > .env.tmp && mv .env.tmp .env
# We will fill in the TOKEN later

echo -e "${GREEN}✓ .env created${NC}"

# 4. Bootstrap Synapse
echo -e "\n${BLUE}[4/6] Bootstrapping Synapse (this takes a moment)...${NC}"
# Start only dependencies needed for registration
docker compose up -d database synapse

echo "Waiting for Synapse to start..."
until curl -s -f "http://localhost:8008/health" > /dev/null; do
    printf "."
    sleep 2
done
echo -e "\n${GREEN}✓ Synapse is up${NC}"

# 5. Register Users & Get Tokens
echo -e "\n${BLUE}[5/6] Registering Users & Generating Tokens...${NC}"

# Function to register user and get token
get_access_token() {
    local user=$1
    local pass=$2
    
    # 1. Create User (ignore error if exists)
    docker compose exec synapse register_new_matrix_user -u "$user" -p "$pass" --admin -c /data/homeserver.yaml --no-user-interactive 2>/dev/null || true
    
    # 2. Login to get Token
    local response=$(curl -s -X POST "http://localhost:8008/_matrix/client/r0/login" \
        -d "{\"type\":\"m.login.password\", \"user\":\"$user\", \"password\":\"$pass\"}")
    
    # Extract token using python (to avoid jq dependency)
    echo $response | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))"
}

# Register Admin
echo "Registering Admin ($ADMIN_USER)..."
ADMIN_TOKEN=$(get_access_token "$ADMIN_USER" "$ADMIN_PASSWORD")

if [ -z "$ADMIN_TOKEN" ]; then
    echo -e "${RED}Failed to register admin user.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Admin registered${NC}"

# Register Bot
echo "Registering Bot (memu_bot)..."
BOT_TOKEN=$(get_access_token "memu_bot" "$BOT_PASSWORD")

if [ -z "$BOT_TOKEN" ]; then
    echo -e "${RED}Failed to register bot user.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Bot registered${NC}"

# Save Bot Token to .env
sed "s|MATRIX_BOT_TOKEN=.*|MATRIX_BOT_TOKEN=${BOT_TOKEN}|" .env > .env.tmp && mv .env.tmp .env

# 6. Final Launch
echo -e "\n${BLUE}[6/6] Launching Memu OS...${NC}"
docker compose down # Stop the bootstrap containers
docker compose up -d # Start everything

echo -e "\n${BLUE}══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}             🚀 INSTALLATION COMPLETE 🚀             ${NC}"
echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"
echo -e ""
echo -e "Your system is live at: ${GREEN}https://${SERVER_NAME}${NC}"
echo -e ""
echo -e "Login Credentials:"
echo -e "  Username: ${GREEN}@${ADMIN_USER}:${SERVER_NAME}${NC}"
echo -e "  Password: ${GREEN}${ADMIN_PASSWORD}${NC}"
echo -e ""
echo -e "IMPORTANT: Save these credentials now!"
echo -e ""
