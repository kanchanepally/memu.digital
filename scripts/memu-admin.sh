#!/bin/bash
# =============================================================================
# Memu Admin Tool
# Usage: sudo ./scripts/memu-admin.sh
# =============================================================================

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Memu Administration${NC}"
echo "1. Create New Chat User"
echo "2. Update System"
echo "3. Exit"
read -p "Select: " OPTION

case $OPTION in
    1)
        read -p "Username: " NEW_USER
        read -s -p "Password: " NEW_PASS
        echo ""
        docker exec -it synapse register_new_matrix_user -u "$NEW_USER" -p "$NEW_PASS" -c /data/homeserver.yaml --admin --no-user-interactive http://localhost:8008
        echo -e "${GREEN}User created.${NC}"
        ;;
    2)
        echo "Updating..."
        git pull && docker compose pull && docker compose up -d
        ;;
    *) exit 0 ;;
esac
