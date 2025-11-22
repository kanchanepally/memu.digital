#!/bin/bash
# Kin OS - Nightly Backup Script

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/home/hareesh/backups"
mkdir -p $BACKUP_DIR

# Load Secrets
source /home/hareesh/kin-os/.env

# 1. Stop Synapse (ensure consistency)
docker stop kin_synapse

# 2. Dump Database
echo "Dumping database..."
docker exec kin_db pg_dump -U kin_user kin_core > "$BACKUP_DIR/kin_backup_$TIMESTAMP.sql"

# 3. Restart Synapse
docker start kin_synapse

# 4. Encrypt & Compress
# We use the DB_PASSWORD as the encryption key for simplicity in V1
echo "Encrypting backup..."
tar -czf - "$BACKUP_DIR/kin_backup_$TIMESTAMP.sql" | openssl enc -e -aes-256-cbc -salt -k "$DB_PASSWORD" -out "$BACKUP_DIR/kin_backup_$TIMESTAMP.sql.tar.gz.enc"

# 5. Cleanup Raw File
rm "$BACKUP_DIR/kin_backup_$TIMESTAMP.sql"

# 6. Retention (Delete backups older than 7 days)
find $BACKUP_DIR -name "*.enc" -mtime +7 -delete

echo "Backup Complete: $BACKUP_DIR/kin_backup_$TIMESTAMP.sql.tar.gz.enc"