#!/usr/bin/env python3
"""
Memu Bootstrap Wizard
Web-based setup interface for first-time configuration
"""

import os
import subprocess
import secrets
import time
import requests
from pathlib import Path
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Detect project root dynamically
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

# Setup state tracking
setup_state = {
    'stage': 'idle',
    'message': '',
    'error': None
}

@app.route('/')
def welcome():
    """Show initial setup form"""
    return render_template('setup.html')

@app.route('/configure', methods=['POST'])
def configure():
    """Process setup form and begin configuration"""
    global setup_state
    
    # Reset state
    setup_state = {'stage': 'starting', 'message': 'Starting setup...', 'error': None}
    
    # Get form data
    family_name = request.form.get('family_name', '').strip()
    admin_password = request.form.get('password', '').strip()
    cloudflare_token = request.form.get('cloudflare_token', '').strip()
    
    # Validate inputs
    if not family_name or not admin_password:
        return "Missing required information (family name or password)", 400
    
    if len(admin_password) < 8:
        return "Password must be at least 8 characters", 400
    
    # Clean family name for URL
    clean_slug = "".join(c for c in family_name if c.isalnum()).lower()
    if not clean_slug:
        return "Family name must contain at least one letter or number", 400
    
    domain = f"{clean_slug}.memu.digital"
    
    try:
        # Generate secure secrets
        setup_state['stage'] = 'secrets'
        setup_state['message'] = 'Generating secure secrets...'
        
        db_password = secrets.token_urlsafe(20)
        bot_password = secrets.token_urlsafe(20)
        
        # Create .env file
        setup_state['stage'] = 'config'
        setup_state['message'] = 'Creating configuration files...'
        
        env_content = f"""# Memu Configuration
# Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

# === SERVER IDENTITY ===
SERVER_NAME={domain}
TZ={get_system_timezone()}

# === DATABASE ===
DB_USER=memu_user
DB_PASSWORD={db_password}
DB_NAME=immich

# === PHOTOS ===
UPLOAD_LOCATION=./photos
IMMICH_VERSION=release

# === NETWORK ===
CLOUDFLARED_TOKEN={cloudflare_token}

# === CHAT ===
SYNAPSE_REPORT_STATS=no

# === AI ===
AI_ENABLED=true
OLLAMA_MODEL=llama3.2
MACHINE_LEARNING_WORKERS=1
MACHINE_LEARNING_WORKER_TIMEOUT=120

# === BOT (will be populated after user creation) ===
MATRIX_BOT_USERNAME=@memu_bot:{domain}
MATRIX_BOT_TOKEN=
"""
        
        env_path = PROJECT_ROOT / '.env'
        env_path.write_text(env_content)
        
        # Generate Nginx config
        setup_state['message'] = 'Configuring web server...'
        generate_nginx_config(domain)

        # Generate Synapse config
        setup_state['message'] = 'Configuring chat server...'
        generate_synapse_config(domain, db_password)
        
        # Generate Element config
        generate_element_config(domain)
        
        # Create necessary directories
        (PROJECT_ROOT / 'photos').mkdir(exist_ok=True)
        (PROJECT_ROOT / 'backups').mkdir(exist_ok=True)
        
        # Start core services
        setup_state['stage'] = 'services'
        setup_state['message'] = 'Starting database and chat server...'
        
        start_core_services()
        
        # Wait for Synapse to be ready
        setup_state['message'] = 'Waiting for chat server to initialize...'
        if not wait_for_synapse(max_wait=60):
            raise Exception("Chat server failed to start. Check logs: docker compose logs synapse")
        
        # Create users
        setup_state['stage'] = 'users'
        setup_state['message'] = 'Creating admin account...'
        
        create_matrix_user('admin', admin_password, is_admin=True)
        
        setup_state['message'] = 'Creating bot account...'
        create_matrix_user('memu_bot', bot_password, is_admin=False)
        
        # Get bot token
        setup_state['message'] = 'Configuring bot authentication...'
        bot_token = get_user_token('memu_bot', bot_password)
        
        if not bot_token:
            # Non-fatal - can be added manually later
            setup_state['error'] = 'Could not auto-generate bot token. You can add it manually later.'
        else:
            # Update .env with bot token
            update_env_var('MATRIX_BOT_TOKEN', bot_token)
        
        # Launch production
        setup_state['stage'] = 'production'
        setup_state['message'] = 'Launching all services...'
        
        launch_production(clean_slug)
        
        # Success!
        setup_state['stage'] = 'complete'
        setup_state['message'] = f'Setup complete! Your server is ready at https://{domain}'
        
        return render_template('installing.html', domain=domain)
        
    except subprocess.CalledProcessError as e:
        error_msg = f"Command failed: {e.cmd}. Check Docker is running."
        setup_state['error'] = error_msg
        return error_msg, 500
        
    except Exception as e:
        error_msg = f"Setup failed: {str(e)}"
        setup_state['error'] = error_msg
        return error_msg, 500

@app.route('/status')
def status():
    """Return current setup status (for progress polling)"""
    return jsonify(setup_state)

def get_system_timezone():
    """Get system timezone, fallback to UTC"""
    try:
        with open('/etc/timezone', 'r') as f:
            return f.read().strip()
    except:
        return 'UTC'

def generate_nginx_config(domain):
    """Generate Nginx reverse proxy configuration"""
    nginx_dir = PROJECT_ROOT / 'nginx' / 'conf.d'
    nginx_dir.mkdir(parents=True, exist_ok=True)
    
    config = f"""server {{
    listen 80;
    server_name localhost;

    # Matrix API
    location ~ ^/(_matrix|_synapse/client) {{
        proxy_pass http://synapse:8008;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $host;
        client_max_body_size 50M;
    }}

    # Element Web
    location / {{
        proxy_pass http://element:80;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header Host $host;
    }}

    # Matrix discovery
    location /.well-known/matrix/server {{
        return 200 '{{"m.server": "{domain}:443"}}';
        add_header Content-Type application/json;
    }}

    location /.well-known/matrix/client {{
        return 200 '{{"m.homeserver": {{"base_url": "https://{domain}"}}}}';
        add_header Content-Type application/json;
        add_header Access-Control-Allow-Origin *;
    }}
}}
"""
    
    config_path = nginx_dir / 'default.conf'
    config_path.write_text(config)

def generate_element_config(domain):
    """Generate Element Web configuration"""
    config = {
        "default_server_config": {
            "m.homeserver": {
                "base_url": f"https://{domain}",
                "server_name": domain
            }
        },
        "brand": "Memu",
        "default_theme": "light",
        "show_labs_settings": True
    }
    
    import json
    config_path = PROJECT_ROOT / 'element-config.json'
    config_path.write_text(json.dumps(config, indent=2))

def generate_synapse_config(domain, db_password):
    """Generate clean Synapse configuration to avoid duplicates"""
    
    # We use a clean template that avoids the duplicate database/listener issues
    # found in the default generated config
    config = f"""# Memu Synapse Configuration
# Generated by Bootstrap Wizard

server_name: "{domain}"
pid_file: /data/homeserver.pid
listeners:
  - port: 8008
    tls: false
    type: http
    x_forwarded: true
    resources:
      - names: [client, federation]
        compress: false

database:
  name: psycopg2
  args:
    user: memu_user
    password: "{db_password}"
    database: immich
    host: database
    cp_min: 5
    cp_max: 10

enable_registration: false
enable_registration_captcha: false
enable_registration_without_verification: false

report_stats: false

# Media storage
media_store_path: /data/media_store

# Signing keys will be generated automatically by Synapse on first run
# because we cleaned the directory and set permissions in install.sh
"""
    
    # Ensure directory exists
    synapse_dir = PROJECT_ROOT / 'synapse'
    synapse_dir.mkdir(parents=True, exist_ok=True)
    
    # Write config
    config_path = synapse_dir / 'homeserver.yaml'
    config_path.write_text(config)

def start_core_services():
    """Start database and Synapse"""
    subprocess.run(
        ["docker", "compose", "up", "-d", "database", "synapse"],
        cwd=PROJECT_ROOT,
        check=True
    )

def wait_for_synapse(max_wait=60):
    """Wait for Synapse to be ready"""
    start = time.time()
    
    while time.time() - start < max_wait:
        try:
            resp = requests.get("http://localhost:8008/_matrix/client/versions", timeout=2)
            if resp.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            pass
        
        time.sleep(2)
    
    return False

def create_matrix_user(username, password, is_admin=False):
    """Create a Matrix user account"""
    cmd = [
        "docker", "compose", "exec", "-T", "synapse",
        "register_new_matrix_user",
        "-u", username,
        "-p", password,
        "-c", "/data/homeserver.yaml"
    ]
    
    if is_admin:
        cmd.insert(-1, "--admin")
    
    # Ignore error if user already exists
    subprocess.run(cmd, cwd=PROJECT_ROOT)

    """Get access token for a user via login with retries"""
    max_retries = 10
    retry_delay = 3
    
    for attempt in range(max_retries):
        try:
            # Wait a moment for consistency
            time.sleep(retry_delay)
            
            resp = requests.post(
                "http://localhost:8008/_matrix/client/r0/login",
                json={
                    "type": "m.login.password",
                    "user": username,
                    "password": password
                },
                timeout=10
            )
            
            if resp.status_code == 403:
                print(f"Login failed (attempt {attempt+1}/{max_retries}): Invalid credentials (or user not ready)")
                continue
                
            resp.raise_for_status()
            data = resp.json()
            return data.get("access_token")
            
        except requests.exceptions.RequestException as e:
            print(f"Login connection failed (attempt {attempt+1}/{max_retries}): {e}")
            continue
            
    return None

def update_env_var(key, value):
    """Update a variable in the .env file"""
    env_path = PROJECT_ROOT / '.env'
    
    if not env_path.exists():
        return
    
    lines = env_path.read_text().splitlines()
    updated = False
    
    for i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[i] = f"{key}={value}"
            updated = True
            break
    
    if not updated:
        lines.append(f"{key}={value}")
    
    env_path.write_text('\n'.join(lines) + '\n')

def launch_production(family_slug):
    """Launch all production services"""
    # Launch the script that handles production startup
    script_path = PROJECT_ROOT / 'scripts' / 'launch_production.sh'
    
    if script_path.exists():
        subprocess.Popen([str(script_path), family_slug])
    else:
        # Fallback: just start all services
        subprocess.run(
            ["docker", "compose", "up", "-d"],
            cwd=PROJECT_ROOT
        )

if __name__ == '__main__':
    print("=" * 50)
    print("Memu Setup Wizard")
    print("=" * 50)
    print(f"Visit: http://{os.uname().nodename}.local")
    print("   or: http://localhost")
    print("=" * 50)
    
    # Run on all interfaces (accessible from network)
    app.run(host='0.0.0.0', port=80, debug=False)