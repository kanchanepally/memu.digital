#!/bin/bash
# Memu Emergency Fix Script for Digital Ocean
# This fixes the immediate "services not accessible" issue

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚑 Memu Emergency Fix"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Get the IP address
IP=$(curl -s ifconfig.me)
echo "📍 Your server IP: $IP"
echo ""

# 1. Fix Firewall
echo "🔒 Configuring firewall..."
if sudo ufw status | grep -q "Status: active"; then
    echo "   UFW is active, opening required ports..."
    sudo ufw allow 80/tcp comment 'Memu HTTP'
    sudo ufw allow 443/tcp comment 'Memu HTTPS'
    sudo ufw reload
    echo "   ✅ Firewall configured"
else
    echo "   ℹ️  UFW not active, skipping"
fi

# 2. Check Services
echo ""
echo "🔍 Checking services..."
echo ""

SERVICES=("synapse" "element" "immich_server" "database" "proxy")
ALL_RUNNING=true

for service in "${SERVICES[@]}"; do
    if docker ps | grep -q "$service"; then
        echo "   ✅ $service is running"
    else
        echo "   ❌ $service is NOT running"
        ALL_RUNNING=false
    fi
done

if [ "$ALL_RUNNING" = false ]; then
    echo ""
    echo "⚠️  Some services are down. Attempting restart..."
    docker compose restart
    sleep 5
    echo "   ✅ Services restarted"
fi

# 3. Create Simple Nginx Config (if not exists)
echo ""
echo "🔧 Checking Nginx configuration..."

NGINX_CONFIG="./nginx/conf.d/default.conf"
if [ ! -f "$NGINX_CONFIG" ]; then
    echo "   Creating new Nginx configuration..."
    mkdir -p ./nginx/conf.d
    
    cat > "$NGINX_CONFIG" << 'EOF'
server {
    listen 80;
    server_name _;
    
    # Docker DNS
    resolver 127.0.0.11 valid=30s;
    
    # Element (Chat UI)
    location / {
        set $upstream_element http://element:80;
        proxy_pass $upstream_element;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Synapse (Matrix API)
    location ~ ^/(_matrix|_synapse) {
        set $upstream_synapse http://synapse:8008;
        proxy_pass $upstream_synapse;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        client_max_body_size 50M;
    }
    
    # Immich (Photos)
    location /photos {
        set $upstream_immich http://immich_server:3001;
        proxy_pass $upstream_immich;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        client_max_body_size 500M;
    }
    
    # Immich API
    location /api {
        set $upstream_immich http://immich_server:3001;
        proxy_pass $upstream_immich;
        proxy_set_header Host $host;
        client_max_body_size 500M;
    }
}
EOF
    
    echo "   ✅ Nginx config created"
    echo "   ♻️  Restarting proxy..."
    docker compose restart proxy
    sleep 2
else
    echo "   ℹ️  Nginx config already exists"
fi

# 4. Test Connectivity
echo ""
echo "🧪 Testing connectivity..."
echo ""

# Test local connectivity
if curl -s -o /dev/null -w "%{http_code}" http://localhost/ | grep -q "200"; then
    echo "   ✅ Nginx is responding locally"
else
    echo "   ❌ Nginx is NOT responding"
fi

if curl -s -o /dev/null -w "%{http_code}" http://localhost/_matrix/client/versions | grep -q "200"; then
    echo "   ✅ Matrix API is responding"
else
    echo "   ⚠️  Matrix API not ready (may still be starting)"
fi

# 5. Display Connection Info
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Fix Applied!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 Access your Memu server:"
echo ""
echo "   Web Interface: http://$IP"
echo "   Chat (Element): http://$IP"
echo "   Photos (Immich): http://$IP/photos"
echo ""
echo "📱 Mobile App Setup:"
echo ""
echo "   Element X:"
echo "   1. Tap 'Change homeserver'"
echo "   2. Enter: http://$IP"
echo "   3. Login with: admin / [your password]"
echo ""
echo "   Immich:"
echo "   1. Server URL: http://$IP"
echo "   2. Create new account (any email)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 Troubleshooting:"
echo "   - View logs: docker compose logs -f"
echo "   - Restart all: docker compose restart"
echo "   - Check status: docker ps"
echo ""