#!/bin/bash
# =============================================================================
# Memu Uninstaller
# =============================================================================

RED='\033[0;31m'
NC='\033[0m'

echo -e "${RED}WARNING: THIS WILL DELETE ALL DATA.${NC}"
read -p "Type 'DELETE' to confirm: " CONFIRM
if [ "$CONFIRM" != "DELETE" ]; then exit 1; fi

docker compose down -v
systemctl stop memu-setup.service 2>/dev/null
systemctl disable memu-setup.service 2>/dev/null
rm /etc/systemd/system/memu-setup.service 2>/dev/null
systemctl stop memu-production.service 2>/dev/null
systemctl disable memu-production.service 2>/dev/null
rm /etc/systemd/system/memu-production.service 2>/dev/null
systemctl daemon-reload
swapoff /swapfile 2>/dev/null
rm /swapfile 2>/dev/null
sed -i '/swapfile/d' /etc/fstab
rm -rf synapse photos backups nginx/conf.d .env .setup_complete
docker system prune -f

echo "Uninstall Complete."
