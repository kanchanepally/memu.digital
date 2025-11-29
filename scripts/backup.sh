#!/bin/bash
set -e

BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/memu_backup_$TIMESTAMP.tar.gz"

echo "=== Memu System Backup ==="
echo "This will backup all your data (Chat, Photos, AI Models) to a single file."

mkdir -p $BACKUP_DIR

# 1. Stop Services
echo "Stopping services to ensure data consistency..."
docker compose down

# 2. Create Backup
echo "Creating backup archive..."
# We use a temporary container to mount the volumes and tar them
docker run --rm \
  -v memu-suite_pgdata:/data/pgdata \
  -v memu-suite_ollama_data:/data/ollama \
  -v $(pwd):/backup \
  alpine tar czf /backup/$BACKUP_FILE -C /data .

# 3. Restart Services
echo "Restarting services..."
docker compose up -d

echo "=== Backup Complete ==="
echo "File: $BACKUP_FILE"
echo ""
echo "To Restore on new SSD:"
echo "1. Copy this file to the new machine."
echo "2. Run: docker run --rm -v memu-suite_pgdata:/data/pgdata -v memu-suite_ollama_data:/data/ollama -v $(pwd):/backup alpine tar xzf /backup/$(basename $BACKUP_FILE) -C /data"
