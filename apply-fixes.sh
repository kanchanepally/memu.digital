#!/bin/bash
# Memu Codebase Fix Script
# Run this from your memu-os directory to apply all audit fixes

set -e

echo "╔═══════════════════════════════════════╗"
echo "║    Memu Codebase Fix Script           ║"
echo "╚═══════════════════════════════════════╝"
echo ""

# Check we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "ERROR: Run this from your memu-os project root directory"
    exit 1
fi

echo "[1/6] Removing sensitive/generated files..."
rm -f synapse/memu.local.signing.key
rm -f synapse_data/memu.local.signing.key
rm -f synapse/homeserver.yaml
rm -f synapse/homeserver-production.yaml
rm -f element-config.json
rmdir synapse_data 2>/dev/null || true
echo "✓ Sensitive files removed"

echo ""
echo "[2/6] Renaming dockerfile to Dockerfile..."
if [ -f "services/intelligence/dockerfile" ]; then
    mv services/intelligence/dockerfile services/intelligence/Dockerfile
    echo "✓ Renamed to Dockerfile"
else
    echo "✓ Already named Dockerfile (or doesn't exist)"
fi

echo ""
echo "[3/6] Updating docker-compose.yml dockerfile reference..."
if grep -q "dockerfile: dockerfile" docker-compose.yml; then
    sed -i 's/dockerfile: dockerfile/dockerfile: Dockerfile/g' docker-compose.yml
    echo "✓ Updated docker-compose.yml"
else
    echo "✓ Already correct in docker-compose.yml"
fi

echo ""
echo "[4/6] Fixing docker-compose.pi-patch.yml..."
if [ -f "docker-compose.pi-patch.yml" ]; then
    # Fix container name (Memu_ -> memu_)
    sed -i 's/container_name: Memu_/container_name: memu_/g' docker-compose.pi-patch.yml
    # Fix depends_on (postgres -> database)
    sed -i 's/postgres:/database:/g' docker-compose.pi-patch.yml
    # Fix dockerfile reference
    sed -i 's/dockerfile: dockerfile/dockerfile: Dockerfile/g' docker-compose.pi-patch.yml
    echo "✓ Fixed docker-compose.pi-patch.yml"
else
    echo "⚠ docker-compose.pi-patch.yml not found (OK if not using Pi)"
fi

echo ""
echo "[5/6] Updating .env.example..."
if [ -f ".env.example" ]; then
    # Fix DB_USER if it's wrong
    sed -i 's/^DB_USER=memu$/DB_USER=memu_user/g' .env.example
    echo "✓ Updated .env.example"
else
    echo "⚠ .env.example not found"
fi

echo ""
echo "[6/6] Updating .gitignore..."
# Add missing entries if not present
GITIGNORE_ENTRIES=(
    "synapse/homeserver.yaml"
    "synapse/homeserver-production.yaml"
    "synapse/*.signing.key"
    "synapse_data/"
    "element-config.json"
    ".env"
    "nginx/conf.d/"
    "photos/"
    "backups/"
)

for entry in "${GITIGNORE_ENTRIES[@]}"; do
    if ! grep -q "^${entry}$" .gitignore 2>/dev/null; then
        echo "$entry" >> .gitignore
        echo "  Added: $entry"
    fi
done
echo "✓ Updated .gitignore"

echo ""
echo "═══════════════════════════════════════"
echo "  Fixes Applied!"
echo "═══════════════════════════════════════"
echo ""
echo "Next steps:"
echo "1. Review changes: git diff"
echo "2. Replace scripts/install.sh with the fixed version"
echo "3. Commit: git add -A && git commit -m 'Apply audit fixes'"
echo "4. Push: git push"
echo "5. Test fresh install on clean machine"
echo ""
