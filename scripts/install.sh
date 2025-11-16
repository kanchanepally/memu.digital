#!/bin/bash
# Complete Hearth OS Installation & Setup Script
# Run this on your Raspberry Pi 5

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}╔═══════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Hearth OS - Complete Setup         ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════╝${NC}"
echo ""

# Step 1: Create all configuration files
echo -e "${GREEN}Step 1: Creating configuration files...${NC}"

# Create .env
cat > .env << 'ENVEOF'
SCHOOL_NAME=Smith Family
HEARTH_DOMAIN=hearth.local
DB_NAME=hearth
DB_USER=hearth
DB_PASSWORD=PLACEHOLDER_DB_PASS
SYNAPSE_ADMIN_TOKEN=PLACEHOLDER_SYNAPSE_TOKEN
ENABLE_REGISTRATION=true
AI_ENABLED=false
BACKUP_ENABLED=false
SESSION_SECRET=PLACEHOLDER_SESSION
LOG_LEVEL=INFO
TZ=Europe/London
ENVEOF

# Generate secure passwords
DB_PASS=$(openssl rand -base64 24 | tr -d "=+/" | cut -c1-25)
SYNAPSE_TOKEN=$(openssl rand -hex 32)
SESSION_SEC=$(openssl rand -hex 32)

sed -i "s/PLACEHOLDER_DB_PASS/$DB_PASS/" .env
sed -i "s/PLACEHOLDER_SYNAPSE_TOKEN/$SYNAPSE_TOKEN/" .env
sed -i "s/PLACEHOLDER_SESSION/$SESSION_SEC/" .env

echo "✓ Configuration file created"

# Create docker-compose.yml (simplified for initial setup)
cat > docker-compose.yml << 'COMPOSEEOF'
version: '3.8'

networks:
  hearth:
    driver: bridge

volumes:
  synapse_data:
  postgres_data:

services:
  postgres:
    image: postgres:15-alpine
    container_name: hearth_db
    restart: unless-stopped
    networks:
      - hearth
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-db.sql:/docker-entrypoint-initdb.d/01-init.sql:ro
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U hearth"]
      interval: 10s
      timeout: 5s
      retries: 5

  synapse:
    image: matrixdotorg/synapse:latest
    container_name: hearth_synapse
    restart: unless-stopped
    networks:
      - hearth
    volumes:
      - synapse_data:/data
    environment:
      SYNAPSE_SERVER_NAME: ${HEARTH_DOMAIN}
      SYNAPSE_REPORT_STATS: "no"
      SYNAPSE_ENABLE_REGISTRATION: "${ENABLE_REGISTRATION}"
    ports:
      - "8008:8008"
    depends_on:
      postgres:
        condition: service_healthy

  element:
    image: vectorim/element-web:latest
    container_name: hearth_element
    restart: unless-stopped
    networks:
      - hearth
    ports:
      - "8080:80"
    volumes:
      - ./element-config.json:/app/config.json:ro
COMPOSEEOF

echo "✓ Docker Compose file created"

# Create database init script
cat > init-db.sql << 'SQLEOF'
CREATE TABLE IF NOT EXISTS households (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    household_id UUID REFERENCES households(id),
    matrix_user_id VARCHAR(255) UNIQUE,
    display_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS shared_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    household_id UUID,
    category VARCHAR(50) DEFAULT 'general',
    task VARCHAR(500) NOT NULL,
    created_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    completed BOOLEAN DEFAULT false,
    completed_at TIMESTAMP,
    completed_by VARCHAR(255)
);

CREATE INDEX idx_tasks ON shared_tasks(household_id, category, completed);

INSERT INTO households (name) VALUES ('My Household');
SQLEOF

echo "✓ Database schema created"

# Create Element config
cat > element-config.json << 'ELEMENTEOF'
{
    "default_server_config": {
        "m.homeserver": {
            "base_url": "http://localhost:8008",
            "server_name": "hearth.local"
        }
    },
    "brand": "Hearth - Your Private Family Space",
    "disable_guests": true,
    "disable_3pid_login": true,
    "show_labs_settings": false,
    "default_theme": "light",
    "default_country_code": "GB",
    "permalink_prefix": "http://localhost:8080"
}
ELEMENTEOF

echo "✓ Element config created"
echo ""

# Step 2: Pull Docker images
echo -e "${GREEN}Step 2: Downloading Docker images (2-3 minutes)...${NC}"
docker compose pull
echo "✓ Images downloaded"
echo ""

# Step 3: Generate Synapse config
echo -e "${GREEN}Step 3: Generating Matrix server config...${NC}"
docker compose run --rm synapse generate
echo "✓ Synapse configured"
echo ""

# Step 4: Start services
echo -e "${GREEN}Step 4: Starting all services...${NC}"
docker compose up -d
echo "✓ Services started"
echo ""

# Step 5: Wait for services
echo -e "${GREEN}Step 5: Waiting for services to be ready (30 seconds)...${NC}"
sleep 30

# Check service health
echo ""
echo "Service Status:"
docker compose ps
echo ""

# Get IP address
IP_ADDRESS=$(hostname -I | awk '{print $1}')

echo -e "${BLUE}╔═══════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Installation Complete! 🎉           ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Access Hearth:${NC}"
echo ""
echo "  Web App: http://$IP_ADDRESS:8080"
echo "  Matrix Server: http://$IP_ADDRESS:8008"
echo ""
echo -e "${YELLOW}IMPORTANT - Create Your Account:${NC}"
echo ""
echo "On your laptop/phone, open: http://$IP_ADDRESS:8080"
echo ""
echo "Click 'Create Account' and register with:"
echo "  - Username: your-name"
echo "  - Password: [choose a secure password]"
echo ""
echo "Then do the same for your wife on her phone/laptop."
echo ""
echo -e "${GREEN}Next Steps:${NC}"
echo "1. Create accounts for you and your wife"
echo "2. Start a private chat between you two"
echo "3. Create a 'Family Room' for shared messages"
echo "4. Share photos by clicking the paperclip icon"
echo ""
echo -e "${YELLOW}Useful Commands:${NC}"
echo "  Stop:    docker compose stop"
echo "  Start:   docker compose start"
echo "  Logs:    docker compose logs -f"
echo "  Restart: docker compose restart"
echo ""
echo "Your Hearth Hub is now running!"
echo ""
COMPOSEEOF

chmod +x setup-hearth.sh