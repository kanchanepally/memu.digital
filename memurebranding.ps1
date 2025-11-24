# Memu Rebranding Script
# Usage: Run from the root of the repository
# Action: Replaces 'Memu' and 'Memu' with 'memu' in all filenames and file contents.

$excludeDir = @(".git", ".idea", "node_modules", "venv", "__pycache__")
$binaryExtensions = @(".png", ".jpg", ".jpeg", ".ico", ".gz", ".zip", ".tar", ".pyc", ".db", ".sqlite")

Function Is-Binary ($path) {
    $ext = [System.IO.Path]::GetExtension($path)
    return $binaryExtensions -contains $ext
}

Write-Host "Starting Rebrand: Memu/Memu -> Memu..." -ForegroundColor Cyan

# 1. Content Replacement
Write-Host "Phase 1: Replacing text content..." -ForegroundColor Yellow
$files = Get-ChildItem -Recurse -File | Where-Object { 
    $dir = $_.DirectoryName
    $skip = $false
    foreach ($ex in $excludeDir) { if ($dir -like "*$ex*") { $skip = $true } }
    return -not $skip
}

foreach ($file in $files) {
    if (Is-Binary $file.FullName) { continue }
    
    try {
        $content = Get-Content -Path $file.FullName -Raw -ErrorAction Stop
        
        if ($content -match "Memu" -or $content -match "Memu") {
            $newContent = $content -replace "Memu\.local", "memu.local" `
                                   -replace "Memu\.local", "memu.local" `
                                   -replace "ourMemu\.app", "memu.digital" `
                                   -replace "Memu Hub", "Memu Hub" `
                                   -replace "Memu", "Memu" `
                                   -replace "Memu", "memu" `
                                   -replace "Memu", "Memu" `
                                   -replace "Memu", "memu"
            
            if ($content -ne $newContent) {
                Set-Content -Path $file.FullName -Value $newContent -NoNewline -Encoding UTF8
                Write-Host "Updated: $($file.Name)" -ForegroundColor Green
            }
        }
    }
    catch {
        Write-Host "Skipped (Read Error): $($file.Name)" -ForegroundColor DarkGray
    }
}

# 2. File & Directory Renaming
Write-Host "Phase 2: Renaming files and folders..." -ForegroundColor Yellow

# Get items again to ensure paths are fresh, sort by length descending to rename deepest children first
$items = Get-ChildItem -Recurse | Where-Object { $_.Name -match "Memu" -or $_.Name -match "Memu" } | Sort-Object -Property FullName -Descending

foreach ($item in $items) {
    $newName = $item.Name -replace "Memu", "memu" `
                          -replace "Memu", "Memu" `
                          -replace "Memu", "memu" `
                          -replace "Memu", "Memu"
    try {
        Rename-Item -Path $item.FullName -NewName $newName -ErrorAction Stop
        Write-Host "Renamed: $($item.Name) -> $newName" -ForegroundColor Magenta
    }
    catch {
        Write-Host "Failed to rename: $($item.Name) ($_.Exception.Message)" -ForegroundColor Red
    }
}

# 3. Verification
Write-Host "Phase 3: Verification..." -ForegroundColor Yellow
$remaining = Get-ChildItem -Recurse | Where-Object { $_.Name -match "Memu" -or $_.Name -match "Memu" }
if ($remaining) {
    Write-Host "Warning: Some files/folders still contain 'Memu' or 'Memu':" -ForegroundColor Red
    $remaining | ForEach-Object { Write-Host "  - $($_.FullName)" }
} else {
    Write-Host "Verification Passed: No 'Memu' or 'Memu' in filenames." -ForegroundColor Green
}

Write-Host "Rebranding Complete. Welcome to Memu." -ForegroundColor Cyan