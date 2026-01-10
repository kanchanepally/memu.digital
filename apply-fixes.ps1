# Memu Codebase Fix Script (PowerShell)
# Run this from your memu-os directory

Write-Host "╔═══════════════════════════════════════╗" -ForegroundColor Blue
Write-Host "║    Memu Codebase Fix Script           ║" -ForegroundColor Blue
Write-Host "╚═══════════════════════════════════════╝" -ForegroundColor Blue
Write-Host ""

# Check we're in the right directory
if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "ERROR: Run this from your memu-os project root directory" -ForegroundColor Red
    exit 1
}

Write-Host "[1/6] Removing sensitive/generated files..." -ForegroundColor Yellow
$filesToRemove = @(
    "synapse/memu.local.signing.key",
    "synapse_data/memu.local.signing.key",
    "synapse/homeserver.yaml",
    "synapse/homeserver-production.yaml",
    "element-config.json"
)
foreach ($file in $filesToRemove) {
    if (Test-Path $file) {
        Remove-Item $file -Force
        Write-Host "  Removed: $file"
    }
}
if (Test-Path "synapse_data" -PathType Container) {
    Remove-Item "synapse_data" -Recurse -Force -ErrorAction SilentlyContinue
}
Write-Host "✓ Sensitive files removed" -ForegroundColor Green

Write-Host ""
Write-Host "[2/6] Renaming dockerfile to Dockerfile..." -ForegroundColor Yellow
if (Test-Path "services/intelligence/dockerfile") {
    Rename-Item "services/intelligence/dockerfile" "Dockerfile"
    Write-Host "✓ Renamed to Dockerfile" -ForegroundColor Green
} else {
    Write-Host "✓ Already named Dockerfile (or doesn't exist)" -ForegroundColor Green
}

Write-Host ""
Write-Host "[3/6] Updating docker-compose.yml dockerfile reference..." -ForegroundColor Yellow
$composeContent = Get-Content "docker-compose.yml" -Raw
if ($composeContent -match "dockerfile: dockerfile") {
    $composeContent = $composeContent -replace "dockerfile: dockerfile", "dockerfile: Dockerfile"
    Set-Content "docker-compose.yml" $composeContent -NoNewline
    Write-Host "✓ Updated docker-compose.yml" -ForegroundColor Green
} else {
    Write-Host "✓ Already correct in docker-compose.yml" -ForegroundColor Green
}

Write-Host ""
Write-Host "[4/6] Fixing docker-compose.pi-patch.yml..." -ForegroundColor Yellow
if (Test-Path "docker-compose.pi-patch.yml") {
    $patchContent = Get-Content "docker-compose.pi-patch.yml" -Raw
    $patchContent = $patchContent -replace "container_name: Memu_", "container_name: memu_"
    $patchContent = $patchContent -replace "postgres:", "database:"
    $patchContent = $patchContent -replace "dockerfile: dockerfile", "dockerfile: Dockerfile"
    Set-Content "docker-compose.pi-patch.yml" $patchContent -NoNewline
    Write-Host "✓ Fixed docker-compose.pi-patch.yml" -ForegroundColor Green
} else {
    Write-Host "⚠ docker-compose.pi-patch.yml not found (OK if not using Pi)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[5/6] Updating .env.example..." -ForegroundColor Yellow
if (Test-Path ".env.example") {
    $envContent = Get-Content ".env.example" -Raw
    $envContent = $envContent -replace "(?m)^DB_USER=memu$", "DB_USER=memu_user"
    Set-Content ".env.example" $envContent -NoNewline
    Write-Host "✓ Updated .env.example" -ForegroundColor Green
} else {
    Write-Host "⚠ .env.example not found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[6/6] Updating .gitignore..." -ForegroundColor Yellow
$gitignoreEntries = @(
    "synapse/homeserver.yaml",
    "synapse/homeserver-production.yaml",
    "synapse/*.signing.key",
    "synapse_data/",
    "element-config.json",
    ".env",
    "nginx/conf.d/",
    "photos/",
    "backups/"
)

$gitignoreContent = ""
if (Test-Path ".gitignore") {
    $gitignoreContent = Get-Content ".gitignore" -Raw
}

foreach ($entry in $gitignoreEntries) {
    if ($gitignoreContent -notmatch [regex]::Escape($entry)) {
        Add-Content ".gitignore" $entry
        Write-Host "  Added: $entry"
    }
}
Write-Host "✓ Updated .gitignore" -ForegroundColor Green

Write-Host ""
Write-Host "═══════════════════════════════════════" -ForegroundColor Green
Write-Host "  Fixes Applied!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Replace scripts/install.sh with the fixed version"
Write-Host "2. Review changes: git diff"
Write-Host "3. Commit: git add -A; git commit -m 'Apply audit fixes'"
Write-Host "4. Push: git push"
Write-Host "5. Test fresh install on DO droplet"
Write-Host ""
