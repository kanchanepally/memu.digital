# Install Script for Windows (PowerShell)
# Sets up directories and environment

Write-Host "=== Memu OS Setup ==="

# Check for .env
if (!(Test-Path -Path ".env")) {
    Write-Host "Creating .env from example..."
    Copy-Item ".env.example" ".env"
    Write-Host "Please edit .env with your specific configuration." -ForegroundColor Yellow
} else {
    Write-Host ".env already exists."
}

# Create directories
$Dirs = @("synapse", "pgdata", "redisdata", "ollama_data", "photos")
foreach ($Dir in $Dirs) {
    if (!(Test-Path -Path $Dir)) {
        New-Item -ItemType Directory -Path $Dir | Out-Null
        Write-Host "Created directory: $Dir"
    }
}

Write-Host "Setup complete. Run 'docker compose up -d' to start."
