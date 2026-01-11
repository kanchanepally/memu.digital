#!/bin/bash
# =============================================================================
# Memu OS - System Installer v2.1
# =============================================================================
# This script prepares the system for Memu installation:
# - Checks prerequisites (Docker, RAM, disk space)
# - Creates swap memory if needed (critical for AI)
# - Installs dependencies
# - Cleans up any previous installation (with user consent)
# - Sets up systemd services for the Setup Wizard
#
# Usage: sudo ./scripts/install.sh
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Minimum requirements
MIN_RAM_MB=3500          # 4GB minus some overhead
MIN_DISK_GB=20           # Minimum free disk space
RECOMMENDED_RAM_MB=7500  # 8GB for full features
SWAP_SIZE_GB=4           # Swap file size for low-RAM systems

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║   ███╗   ███╗███████╗███╗   ███╗██╗   ██╗                    ║"
echo "║   ████╗ ████║██╔════╝████╗ ████║██║   ██║                    ║"
echo "║   ██╔████╔██║█████╗  ██╔████╔██║██║   ██║                    ║"
echo "║   ██║╚██╔╝██║██╔══╝  ██║╚██╔╝██║██║   ██║                    ║"
echo "║   ██║ ╚═╝ ██║███████╗██║ ╚═╝ ██║╚██████╔╝                    ║"
echo "║   ╚═╝     ╚═╝╚══════╝╚═╝     ╚═╝ ╚═════╝                     ║"
echo "║                                                               ║"
echo "║   Your Family's Digital Sanctuary                             ║"
echo "║   Installer v2.1                                              ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# =============================================================================
# SWAP MEMORY SETUP (Critical for AI on low-RAM systems)
# =============================================================================

setup_swap() {
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  Checking Swap Memory${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    # Check if swap exists
    SWAP_TOTAL=$(free -m | awk '/^Swap:/ {print $2}')
    
    if [ "$SWAP_TOTAL" -lt 1000 ]; then
        log_warning "Insufficient swap detected (${SWAP_TOTAL}MB)."
        log_info "Creating ${SWAP_SIZE_GB}GB swap file for AI stability..."
        echo ""
        
        # Remove old swapfile if it exists but isn't active
        if [ -f /swapfile ]; then
            swapoff /swapfile 2>/dev/null || true
            rm -f /swapfile
        fi
        
        # Create new swap file
        fallocate -l ${SWAP_SIZE_GB}G /swapfile
        chmod 600 /swapfile
        mkswap /swapfile
        swapon /swapfile
        
        # Make it permanent (if not already in fstab)
        if ! grep -q "/swapfile" /etc/fstab; then
            echo '/swapfile none swap sw 0 0' >> /etc/fstab
        fi
        
        log_success "Created ${SWAP_SIZE_GB}GB swap file"
        
        # Verify
        NEW_SWAP=$(free -m | awk '/^Swap:/ {print $2}')
        log_info "Swap now: ${NEW_SWAP}MB"
    else
        log_success "Swap memory OK (${SWAP_TOTAL}MB)"
    fi
    echo ""
}

# =============================================================================
# STEP 0: DETECT USER AND PATHS
# =============================================================================

echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  Step 0: Detecting Environment${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Get the actual user who invoked sudo (not root)
REAL_USER="${SUDO_USER:-$(whoami)}"
REAL_HOME=$(eval echo ~$REAL_USER)
PROJECT_ROOT=$(pwd)

log_info "Detected User: ${GREEN}$REAL_USER${NC}"
log_info "Home Directory: ${GREEN}$REAL_HOME${NC}"
log_info "Project Root: ${GREEN}$PROJECT_ROOT${NC}"
echo ""

# Verify we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    log_error "docker-compose.yml not found in current directory."
    log_error "Please run this script from the memu.digital project root."
    log_error "Example: cd ~/memu.digital && sudo ./scripts/install.sh"
    exit 1
fi

log_success "Project structure verified"
echo ""

# =============================================================================
# STEP 1: CHECK PREREQUISITES
# =============================================================================

echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  Step 1: Checking Prerequisites${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Check if running as root/sudo
if [ "$EUID" -ne 0 ]; then
    log_error "This script must be run with sudo."
    log_error "Usage: sudo ./scripts/install.sh"
    exit 1
fi
log_success "Running with root privileges"

# Check Docker
if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed."
    echo ""
    echo "  Install Docker first with:"
    echo -e "  ${CYAN}curl -sSL https://get.docker.com | sh${NC}"
    echo -e "  ${CYAN}sudo usermod -aG docker $REAL_USER${NC}"
    echo ""
    exit 1
fi
DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
log_success "Docker installed (version $DOCKER_VERSION)"

# Check Docker Compose
if ! docker compose version &> /dev/null; then
    log_error "Docker Compose (v2) is not available."
    echo "  Please ensure you have Docker Compose v2 installed."
    exit 1
fi
COMPOSE_VERSION=$(docker compose version --short)
log_success "Docker Compose installed (version $COMPOSE_VERSION)"

# Check RAM
TOTAL_RAM_KB=$(grep MemTotal /proc/meminfo | awk '{print $2}')
TOTAL_RAM_MB=$((TOTAL_RAM_KB / 1024))
TOTAL_RAM_GB=$(awk "BEGIN {printf \"%.1f\", $TOTAL_RAM_MB / 1024}")

echo ""
log_info "System RAM: ${GREEN}${TOTAL_RAM_GB}GB${NC} (${TOTAL_RAM_MB}MB)"

if [ $TOTAL_RAM_MB -lt $MIN_RAM_MB ]; then
    log_error "Insufficient RAM. Minimum 4GB required."
    log_error "Detected: ${TOTAL_RAM_GB}GB"
    echo ""
    echo "  Memu requires at least 4GB RAM to run all services."
    echo "  With less RAM, services will crash or hang."
    echo ""
    exit 1
elif [ $TOTAL_RAM_MB -lt $RECOMMENDED_RAM_MB ]; then
    log_warning "RAM is below recommended 8GB."
    echo ""
    echo -e "  ${YELLOW}Your system has ${TOTAL_RAM_GB}GB RAM.${NC}"
    echo "  Memu will run, but with limitations:"
    echo "  - AI model will use smaller/slower model (llama3.2:1b)"
    echo "  - Photo ML features may be slower"
    echo "  - Recommend upgrading to 8GB for best experience"
    echo ""
    AI_MODE="limited"
else
    log_success "RAM is sufficient for full features"
    AI_MODE="full"
fi

# Setup swap memory (critical for AI stability)
setup_swap

# Check Disk Space
DISK_FREE_KB=$(df -k "$PROJECT_ROOT" | tail -1 | awk '{print $4}')
DISK_FREE_GB=$((DISK_FREE_KB / 1024 / 1024))

log_info "Free disk space: ${GREEN}${DISK_FREE_GB}GB${NC}"

if [ $DISK_FREE_GB -lt $MIN_DISK_GB ]; then
    log_error "Insufficient disk space. Minimum ${MIN_DISK_GB}GB required."
    exit 1
fi
log_success "Disk space is sufficient"

echo ""

# =============================================================================
# STEP 2: CHECK FOR EXISTING INSTALLATION
# =============================================================================

echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  Step 2: Checking for Existing Installation${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""

EXISTING_VOLUMES=$(docker volume ls -q | grep -E "memu|pgdata|ollama|redis" 2>/dev/null || true)
EXISTING_CONTAINERS=$(docker ps -a --format '{{.Names}}' | grep -E "memu_" 2>/dev/null || true)

if [ -n "$EXISTING_VOLUMES" ] || [ -n "$EXISTING_CONTAINERS" ]; then
    log_warning "Found existing Memu installation!"
    echo ""
    
    if [ -n "$EXISTING_CONTAINERS" ]; then
        echo "  Existing containers:"
        echo "$EXISTING_CONTAINERS" | sed 's/^/    - /'
    fi
    
    if [ -n "$EXISTING_VOLUMES" ]; then
        echo ""
        echo "  Existing data volumes:"
        echo "$EXISTING_VOLUMES" | sed 's/^/    - /'
    fi
    
    echo ""
    echo -e "  ${YELLOW}What would you like to do?${NC}"
    echo ""
    echo "  1) Fresh install (DELETE all existing data)"
    echo "  2) Keep data (attempt upgrade/repair)"
    echo "  3) Cancel installation"
    echo ""
    read -p "  Enter choice [1-3]: " INSTALL_CHOICE
    
    case $INSTALL_CHOICE in
        1)
            log_info "Removing existing installation..."
            echo ""
            
            # Stop containers
            if [ -n "$EXISTING_CONTAINERS" ]; then
                log_info "Stopping containers..."
                docker stop $(docker ps -aq --filter "name=memu_") 2>/dev/null || true
                docker rm $(docker ps -aq --filter "name=memu_") 2>/dev/null || true
                log_success "Containers removed"
            fi
            
            # Remove volumes
            if [ -n "$EXISTING_VOLUMES" ]; then
                log_info "Removing data volumes..."
                for vol in $EXISTING_VOLUMES; do
                    docker volume rm "$vol" -f 2>/dev/null || true
                done
                log_success "Volumes removed"
            fi
            
            # Prune any remaining
            docker system prune -f > /dev/null 2>&1 || true
            
            # Clean up generated config files
            log_info "Cleaning up config files..."
            rm -f ./synapse/homeserver.yaml
            rm -f ./synapse/*.signing.key
            rm -f ./synapse/*.log.config 2>/dev/null || true
            rm -f ./element-config.json
            rm -f ./.env
            rm -rf ./nginx/conf.d/*
            rm -f ./.ai_config
            log_success "Config files cleaned"
            echo ""
            ;;
        2)
            log_info "Keeping existing data. Will attempt upgrade/repair."
            echo ""
            ;;
        3)
            log_info "Installation cancelled."
            exit 0
            ;;
        *)
            log_error "Invalid choice. Installation cancelled."
            exit 1
            ;;
    esac
else
    log_success "No existing installation found. Fresh install."
fi

echo ""

# =============================================================================
# STEP 3: INSTALL DEPENDENCIES
# =============================================================================

echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  Step 3: Installing Dependencies${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""

log_info "Updating package lists..."
apt-get update -qq

log_info "Installing Python and dependencies..."
apt-get install -y python3-pip python3-requests curl > /dev/null 2>&1

# Install Flask for the setup wizard
pip3 install flask --quiet --break-system-packages 2>/dev/null || pip3 install flask --quiet

log_success "Python dependencies installed"
echo ""

# =============================================================================
# STEP 4: PREPARE DIRECTORIES AND PERMISSIONS
# =============================================================================

echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  Step 4: Preparing Directories${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Create necessary directories
log_info "Creating directories..."
mkdir -p ./synapse
mkdir -p ./nginx/conf.d
mkdir -p ./photos
mkdir -p ./backups

# Set ownership to the real user (not root)
chown -R $REAL_USER:$REAL_USER ./synapse
chown -R $REAL_USER:$REAL_USER ./nginx
chown -R $REAL_USER:$REAL_USER ./photos
chown -R $REAL_USER:$REAL_USER ./backups

# Synapse needs write permissions for signing keys
chmod 755 ./synapse

log_success "Directories created and permissions set"
echo ""

# =============================================================================
# STEP 5: CONFIGURE SYSTEMD SERVICES
# =============================================================================

echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  Step 5: Configuring System Services${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""

log_info "Creating systemd service files..."

# Create Setup Wizard service
# NOTE: Runs as root to bind to port 80
# bootstrap/app.py MUST have: app.run(host='0.0.0.0', port=80)
cat > /etc/systemd/system/memu-setup.service << EOF
[Unit]
Description=Memu OS Setup Wizard
After=network.target docker.service
Wants=docker.service

[Service]
Type=simple
User=root
WorkingDirectory=${PROJECT_ROOT}/bootstrap
ExecStart=/usr/bin/python3 app.py
Restart=on-failure
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

log_success "Created memu-setup.service"

# Create Production service
cat > /etc/systemd/system/memu-production.service << EOF
[Unit]
Description=Memu OS Production Stack
Requires=docker.service
After=docker.service network-online.target
Wants=network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
User=${REAL_USER}
WorkingDirectory=${PROJECT_ROOT}
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
TimeoutStartSec=300

[Install]
WantedBy=multi-user.target
EOF

log_success "Created memu-production.service"

# Reload systemd
systemctl daemon-reload

# Enable the setup service (but don't start it yet)
systemctl enable memu-setup.service > /dev/null 2>&1

log_success "Systemd services configured"
echo ""

# =============================================================================
# STEP 6: CONFIGURE AI MODE BASED ON RAM
# =============================================================================

echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  Step 6: Configuring AI Mode${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""

if [ "$AI_MODE" = "limited" ]; then
    log_warning "Configuring for limited RAM (${TOTAL_RAM_GB}GB)"
    echo ""
    echo "  AI will use smaller model (llama3.2:1b instead of llama3.2)"
    echo "  This model is compatible with the bot code and uses less RAM."
    echo "  To upgrade AI capabilities, add more RAM to your system."
    echo ""
    
    # Create an AI config marker file
    # Using llama3.2:1b for compatibility with bot code (not phi3:mini)
    echo "AI_MODEL=llama3.2:1b" > ./.ai_config
    echo "AI_MODE=limited" >> ./.ai_config
else
    log_success "Configuring for full AI features (${TOTAL_RAM_GB}GB RAM)"
    echo ""
    
    echo "AI_MODEL=llama3.2" > ./.ai_config
    echo "AI_MODE=full" >> ./.ai_config
fi

chown $REAL_USER:$REAL_USER ./.ai_config

echo ""

# =============================================================================
# STEP 7: VERIFY BOOTSTRAP APP CONFIGURATION
# =============================================================================

echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  Step 7: Verifying Setup Wizard${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Check that bootstrap/app.py exists
if [ ! -f "./bootstrap/app.py" ]; then
    log_error "bootstrap/app.py not found!"
    log_error "The Setup Wizard cannot run without this file."
    exit 1
fi

# Check that app.py binds to 0.0.0.0 (not just localhost)
if grep -q "host='0.0.0.0'" ./bootstrap/app.py || grep -q 'host="0.0.0.0"' ./bootstrap/app.py; then
    log_success "Setup Wizard configured to accept external connections"
else
    log_warning "Setup Wizard may only listen on localhost!"
    echo ""
    echo "  Please verify bootstrap/app.py contains:"
    echo -e "  ${CYAN}app.run(host='0.0.0.0', port=80)${NC}"
    echo ""
    echo "  If it only has app.run() or app.run(port=80), you won't be"
    echo "  able to access the wizard from your browser."
    echo ""
fi

# Check port 80 binding
if grep -q "port=80" ./bootstrap/app.py; then
    log_success "Setup Wizard configured for port 80"
else
    log_warning "Setup Wizard may not be on port 80"
    echo "  Verify bootstrap/app.py has: app.run(host='0.0.0.0', port=80)"
fi

echo ""

# =============================================================================
# INSTALLATION COMPLETE
# =============================================================================

echo -e "${GREEN}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║   ✓ Installation Preparation Complete!                       ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Get the server's IP address
SERVER_IP=$(hostname -I | awk '{print $1}')

echo -e "${CYAN}Next Steps:${NC}"
echo ""
echo "  1. Start the Setup Wizard:"
echo -e "     ${GREEN}sudo systemctl start memu-setup.service${NC}"
echo ""
echo "  2. Open your browser and visit:"
echo -e "     ${GREEN}http://${SERVER_IP}${NC}"
echo ""
echo "     Or if on local network:"
echo -e "     ${GREEN}http://$(hostname).local${NC}"
echo ""
echo "  3. Complete the setup wizard to configure your Memu server."
echo ""
echo -e "${CYAN}System Information:${NC}"
echo "  - RAM: ${TOTAL_RAM_GB}GB (AI Mode: ${AI_MODE})"
echo "  - Swap: $(free -m | awk '/^Swap:/ {print $2}')MB"
echo "  - Disk: ${DISK_FREE_GB}GB free"
echo "  - User: ${REAL_USER}"
echo "  - Project: ${PROJECT_ROOT}"
echo ""
echo -e "${CYAN}Troubleshooting:${NC}"
echo "  - Check wizard status: ${YELLOW}sudo systemctl status memu-setup.service${NC}"
echo "  - View wizard logs:    ${YELLOW}sudo journalctl -u memu-setup.service -f${NC}"
echo "  - Restart wizard:      ${YELLOW}sudo systemctl restart memu-setup.service${NC}"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Memu - Your Family's Digital Sanctuary${NC}"
echo -e "${BLUE}  https://github.com/kanchanepally/memu.digital${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""