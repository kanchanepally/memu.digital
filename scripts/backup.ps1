# Backup Script for Windows (PowerShell)
# Backs up Memu data volumes to a tarball

$BackupDir = "./backups"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupFile = "$BackupDir/memu_backup_$Timestamp.tar.gz"

Write-Host "=== Memu System Backup ==="
Write-Host "This will backup all your data (Chat, Photos, AI Models) to a single file."

if (!(Test-Path -Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir | Out-Null
}

# 1. Stop Services
Write-Host "Stopping services to ensure data consistency..."
docker compose down

# 2. Create Backup
Write-Host "Creating backup archive..."
# Using docker run to mount volumes and tar them (cross-platform way)
docker run --rm `
  -v memu-suite_pgdata:/data/pgdata `
  -v memu-suite_ollama_data:/data/ollama `
  -v ${PWD}:/backup `
  alpine tar czf /backup/$BackupFile -C /data .

# 3. Restart Services
Write-Host "Restarting services..."
docker compose up -d

Write-Host "=== Backup Complete ==="
Write-Host "File: $BackupFile"
