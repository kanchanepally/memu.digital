# Memu Fix Script for Windows
# Run this from: C:\Users\Lenovo\Code\Memu\Memu-os

Write-Host "Fixing Memu Setup..." -ForegroundColor Cyan

# Step 1: Copy schema
Write-Host "`nStep 1: Copying database schema..." -ForegroundColor Yellow
Copy-Item database/schema.sql init-db.sql
Write-Host "Schema copied successfully" -ForegroundColor Green

# Step 2: Stop containers
Write-Host "`nStep 2: Stopping containers..." -ForegroundColor Yellow
docker compose down
Write-Host "Containers stopped" -ForegroundColor Green

# Step 3: Generate Synapse config
Write-Host "`nStep 3: Generating Synapse configuration..." -ForegroundColor Yellow
docker run -it --rm `
  -v ${PWD}/synapse_data:/data `
  -e SYNAPSE_SERVER_NAME=memu.local `
  -e SYNAPSE_REPORT_STATS=no `
  matrixdotorg/synapse:latest generate

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to generate Synapse config" -ForegroundColor Red
    exit 1
}
Write-Host "Synapse config generated" -ForegroundColor Green

# Step 4: Add PostgreSQL config to homeserver.yaml
Write-Host "`nStep 4: Configuring PostgreSQL..." -ForegroundColor Yellow
$dbConfig = @"

# PostgreSQL Database Configuration
database:
  name: psycopg2
  args:
    user: Memu
    password: dummy_password
    database: Memu
    host: postgres
    port: 5432
    cp_min: 5
    cp_max: 10
"@

Add-Content -Path synapse_data/homeserver.yaml -Value $dbConfig
Write-Host "PostgreSQL configured" -ForegroundColor Green

# Step 5: Enable registration
Write-Host "`nStep 5: Enabling registration..." -ForegroundColor Yellow
$homeserverContent = Get-Content synapse_data/homeserver.yaml -Raw
$homeserverContent = $homeserverContent -replace 'enable_registration: false', 'enable_registration: true'
Set-Content -Path synapse_data/homeserver.yaml -Value $homeserverContent

# Also add this at the end if not present
if ($homeserverContent -notmatch 'enable_registration_without_verification') {
    Add-Content -Path synapse_data/homeserver.yaml -Value "`nenable_registration_without_verification: true"
}
Write-Host "Registration enabled" -ForegroundColor Green

# Step 6: Restart with clean database
Write-Host "`nStep 6: Starting services with fresh database..." -ForegroundColor Yellow
docker compose down -v
Start-Sleep -Seconds 2
docker compose up -d
Write-Host "Services starting..." -ForegroundColor Green

# Step 7: Wait for services
Write-Host "`nStep 7: Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Step 8: Check status
Write-Host "`nService Status:" -ForegroundColor Cyan
docker compose ps

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Memu Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "   1. Open browser: http://localhost:8080" -ForegroundColor White
Write-Host "   2. Click 'Create Account'" -ForegroundColor White
Write-Host "   3. Username: john (or your name)" -ForegroundColor White
Write-Host "   4. Password: something secure" -ForegroundColor White
Write-Host "   5. Start chatting!" -ForegroundColor White

Write-Host "`nTo check logs:" -ForegroundColor Yellow
Write-Host "   docker compose logs synapse" -ForegroundColor White

Write-Host "`nTo test Synapse:" -ForegroundColor Yellow
Write-Host "   curl http://localhost:8008/_matrix/client/versions" -ForegroundColor White
Write-Host ""