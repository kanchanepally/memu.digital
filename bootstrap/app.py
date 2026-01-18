#!/usr/bin/env python3
"""
Memu Bootstrap Wizard (v4.2)

TESTED: January 18, 2026 on DigitalOcean

FIXES FROM v4.1:
1. Element config now uses Tailscale hostname for correct HTTPS access
2. Tailscale hostname auto-detected after connection
3. Better status reporting for UI progress tracking

FIXES FROM v4.0:
1. Database creation uses simple CREATE DATABASE (not \gexec)
2. Synapse is RESTARTED after config is written (fixes HMAC)
3. Element config generated with correct IP after Synapse works
4. Retry loops for user registration and token retrieval
5. Graceful degradation if bot fails (system still works)
"""

import os
import subprocess
import secrets
import time
import json
import requests
import threading
from pathlib import Path
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

WIZARD_PORT = int(os.environ.get('WIZARD_PORT', 8888))
PROJECT_ROOT = Path(os.environ.get('PROJECT_ROOT', Path(__file__).parent.parent.absolute()))

# Setup state
setup_state = {
    'stage': 'idle',
    'step': 0,
    'total_steps': 12,
    'message': '',
    'error': None,
    'warnings': [],
    'tailscale_hostname': None
}

def update_state(stage, step, message, error=None, warning=None):
    global setup_state
    setup_state['stage'] = stage
    setup_state['step'] = step
    setup_state['message'] = message
    setup_state['error'] = error
    if warning:
        setup_state['warnings'].append(warning)
    print(f"[{stage}] Step {step}/12: {message}")
    if warning:
        print(f"  ⚠️  {warning}")


def read_env_file():
    env_path = PROJECT_ROOT / '.env'
    if not env_path.exists():
        return {}
    values = {}
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, val = line.split('=', 1)
        values[key.strip()] = val.strip()
    return values


def update_env_var(key, value):
    env_path = PROJECT_ROOT / '.env'
    content = env_path.read_text() if env_path.exists() else ""
    lines = content.splitlines()
    found = False
    for i, line in enumerate(lines):
        if line.strip().startswith(f"{key}="):
            lines[i] = f"{key}={value}"
            found = True
            break
    if not found:
        lines.append(f"{key}={value}")
    env_path.write_text('\n'.join(lines) + '\n')


def run_cmd(cmd, check=True, cwd=None):
    """Run shell command"""
    print(f"  $ {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd or PROJECT_ROOT)
    if check and result.returncode != 0:
        raise Exception(f"Command failed: {result.stderr}")
    return result


# =============================================================================
# ROUTES
# =============================================================================

@app.route('/')
def welcome():
    return render_template('setup.html')

@app.route('/status')
def status():
    return jsonify(setup_state)

@app.route('/configure', methods=['POST'])
def configure():
    family_name = request.form.get('family_name', '').strip()
    admin_password = request.form.get('password', '').strip()
    tailscale_key = request.form.get('tailscale_key', '').strip()
    
    if not family_name or not admin_password:
        return "Missing family name or password", 400
    if len(admin_password) < 8:
        return "Password must be at least 8 characters", 400
    
    clean_slug = "".join(c for c in family_name if c.isalnum()).lower()
    if not clean_slug:
        return "Family name must contain at least one letter or number", 400
    
    domain = f"{clean_slug}.memu.digital"
    
    # Get server IP for Element config
    try:
        server_ip = request.host.split(':')[0]
    except:
        server_ip = 'localhost'
    
    thread = threading.Thread(
        target=run_setup,
        args=(clean_slug, domain, admin_password, tailscale_key, server_ip),
        daemon=True
    )
    thread.start()
    
    return render_template('installing.html', domain=domain)


# =============================================================================
# MAIN SETUP
# =============================================================================

def run_setup(clean_slug, domain, admin_password, tailscale_key, server_ip):
    try:
        env = read_env_file()
        db_password = env.get('DB_PASSWORD', secrets.token_urlsafe(20))
        bot_password = secrets.token_urlsafe(20)
        final_ts_key = tailscale_key or env.get('TAILSCALE_AUTH_KEY', '')
        registration_secret = secrets.token_urlsafe(32)
        
        # =====================================================================
        # STEP 1: Generate Configs
        # =====================================================================
        update_state('config', 1, 'Generating configuration files...')
        
        update_env_var('SERVER_NAME', domain)
        update_env_var('DB_PASSWORD', db_password)
        update_env_var('MATRIX_BOT_USERNAME', f'@memu_bot:{domain}')
        if final_ts_key:
            update_env_var('TAILSCALE_AUTH_KEY', final_ts_key)
        
        # Synapse config
        synapse_config = generate_synapse_config(domain, db_password, registration_secret)
        (PROJECT_ROOT / 'synapse' / 'homeserver.yaml').write_text(synapse_config)
        
        # Nginx config
        nginx_config = generate_nginx_config(domain)
        (PROJECT_ROOT / 'nginx' / 'conf.d' / 'default.conf').write_text(nginx_config)
        
        time.sleep(1)
        
        # =====================================================================
        # STEP 2: Start Database
        # =====================================================================
        update_state('database', 2, 'Starting database...')
        run_cmd(['docker', 'compose', 'up', '-d', 'database'])
        
        # =====================================================================
        # STEP 3: Wait for Database
        # =====================================================================
        update_state('database', 3, 'Waiting for database...')
        if not wait_for_database(max_wait=60):
            raise Exception("Database failed to start")
        
        # =====================================================================
        # STEP 4: Create Databases (FIXED - simple SQL, not \gexec)
        # =====================================================================
        update_state('database', 4, 'Creating databases...')
        create_databases()
        
        # =====================================================================
        # STEP 5: Start Synapse
        # =====================================================================
        update_state('synapse', 5, 'Starting chat server...')
        run_cmd(['docker', 'compose', 'up', '-d', 'synapse'])
        
        # =====================================================================
        # STEP 6: Wait for Synapse + RESTART (FIXED - ensures config is loaded)
        # =====================================================================
        update_state('synapse', 6, 'Waiting for chat server...')
        
        if not wait_for_synapse(max_wait=90):
            raise Exception("Chat server failed to start")
        
        # KEY FIX: Restart Synapse to ensure it loaded the config with our secret
        update_state('synapse', 6, 'Restarting chat server to load config...')
        run_cmd(['docker', 'compose', 'restart', 'synapse'])
        time.sleep(10)  # Wait for restart
        
        if not wait_for_synapse(max_wait=60):
            raise Exception("Chat server failed after restart")
        
        # =====================================================================
        # STEP 7: Create Admin User
        # =====================================================================
        update_state('users', 7, 'Creating admin account...')
        
        admin_created = create_matrix_user_with_retry('admin', admin_password, is_admin=True)
        if not admin_created:
            raise Exception("Failed to create admin user")
        
        # =====================================================================
        # STEP 8: Create Bot User
        # =====================================================================
        update_state('users', 8, 'Creating bot account...')
        
        bot_created = create_matrix_user_with_retry('memu_bot', bot_password, is_admin=False)
        if not bot_created:
            update_state('users', 8, 'Bot creation had issues',
                        warning='Bot account may need manual setup. Core features still work.')
        
        # =====================================================================
        # STEP 9: Get Bot Token
        # =====================================================================
        update_state('users', 9, 'Configuring bot authentication...')
        
        bot_token = None
        if bot_created:
            bot_token = get_user_token_with_retry('memu_bot', bot_password)
        
        if bot_token:
            update_env_var('MATRIX_BOT_TOKEN', bot_token)
        else:
            update_state('users', 9, 'Bot token retrieval had issues',
                        warning='AI assistant may need manual configuration.')
        
        # =====================================================================
        # STEP 10: Generate Element Config (initial - may be updated by Tailscale)
        # =====================================================================
        update_state('services', 10, 'Configuring chat interface...')
        
        # Initial config uses server IP (for local access)
        element_config = {
            "default_server_config": {
                "m.homeserver": {
                    "base_url": f"http://{server_ip}:8008",
                    "server_name": domain
                }
            },
            "brand": "Memu",
            "default_theme": "light"
        }
        (PROJECT_ROOT / 'element-config.json').write_text(json.dumps(element_config, indent=2))
        
        # =====================================================================
        # STEP 11: Start All Services
        # =====================================================================
        update_state('services', 11, 'Starting all services...')
        run_cmd(['docker', 'compose', 'up', '-d'])
        time.sleep(5)
        
        # Force recreate intelligence to pick up bot token
        if bot_token:
            run_cmd(['docker', 'compose', 'up', '-d', '--force-recreate', 'intelligence'], check=False)
        
        # =====================================================================
        # STEP 12: Configure Tailscale (if provided)
        # =====================================================================
        if final_ts_key:
            update_state('network', 12, 'Configuring remote access...')
            configure_tailscale(domain, server_ip)
        else:
            update_state('network', 12, 'Skipping remote access (no Tailscale key provided)')
        
        # =====================================================================
        # DONE
        # =====================================================================
        ts_hostname = setup_state.get('tailscale_hostname')
        if ts_hostname:
            update_state('complete', 12, f'Setup complete! Access via https://{ts_hostname}')
        else:
            update_state('complete', 12, f'Setup complete! Access via http://{server_ip}')
        
        schedule_handoff()
        
    except Exception as e:
        update_state('error', setup_state['step'], str(e), error=str(e))
        print(f"SETUP FAILED: {e}")
        import traceback
        traceback.print_exc()


# =============================================================================
# CONFIG GENERATORS
# =============================================================================

def generate_synapse_config(domain, db_password, registration_secret):
    return f"""# Memu Synapse Configuration (v4.2)
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
    database: memu_synapse
    host: database
    cp_min: 5
    cp_max: 10

enable_registration: false
report_stats: false
media_store_path: /data/media_store
log_config: "/data/memu.local.log.config"

registration_shared_secret: "{registration_secret}"
signing_key_path: "/data/{domain}.signing.key"
"""


def generate_nginx_config(domain):
    return f"""server {{
    listen 80;
    server_name localhost;
    resolver 127.0.0.11 valid=30s;

    location ~ ^/(_matrix|_synapse/client) {{
        set $upstream_synapse http://synapse:8008;
        proxy_pass $upstream_synapse;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $host;
        client_max_body_size 50M;
    }}

    location / {{
        set $upstream_element http://element:80;
        proxy_pass $upstream_element;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header Host $host;
    }}

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


# =============================================================================
# DATABASE
# =============================================================================

def wait_for_database(max_wait=60):
    start = time.time()
    while time.time() - start < max_wait:
        result = run_cmd(['docker', 'exec', 'memu_postgres', 'pg_isready', '-U', 'memu_user'], check=False)
        if result.returncode == 0:
            return True
        time.sleep(2)
    return False


def create_databases():
    """Create databases using simple SQL (FIX: no \gexec)"""
    databases = ['memu_synapse', 'memu_immich', 'immich']
    
    for db in databases:
        # Check if exists first
        check = run_cmd([
            'docker', 'exec', 'memu_postgres',
            'psql', '-U', 'memu_user', '-d', 'postgres', '-tAc',
            f"SELECT 1 FROM pg_database WHERE datname = '{db}'"
        ], check=False)
        
        if '1' not in check.stdout:
            # Create it
            run_cmd([
                'docker', 'exec', 'memu_postgres',
                'psql', '-U', 'memu_user', '-d', 'postgres', '-c',
                f"CREATE DATABASE {db};"
            ], check=False)
            print(f"    Created database: {db}")
        else:
            print(f"    Database exists: {db}")


# =============================================================================
# SYNAPSE
# =============================================================================

def wait_for_synapse(max_wait=90):
    start = time.time()
    while time.time() - start < max_wait:
        try:
            resp = requests.get("http://localhost:8008/_matrix/client/versions", timeout=5)
            if resp.status_code == 200:
                return True
        except:
            pass
        time.sleep(3)
    return False


def create_matrix_user_with_retry(username, password, is_admin=False, max_retries=5):
    """Create Matrix user with retry logic (FIX: handles HMAC timing)"""
    admin_flag = "--admin" if is_admin else "--no-admin"
    
    for attempt in range(max_retries):
        print(f"  Creating user {username} (attempt {attempt + 1}/{max_retries})...")
        
        result = run_cmd([
            'docker', 'compose', 'exec', '-T', 'synapse',
            'register_new_matrix_user',
            '-u', username, '-p', password, admin_flag,
            '-c', '/data/homeserver.yaml',
            'http://localhost:8008'
        ], check=False)
        
        if result.returncode == 0:
            print(f"  ✓ User {username} created")
            return True
        
        if "already taken" in result.stderr or "already in use" in result.stderr:
            print(f"  ✓ User {username} already exists")
            return True
        
        if "HMAC" in result.stderr:
            wait_time = 5 * (attempt + 1)
            print(f"  ⚠ HMAC error - waiting {wait_time}s...")
            time.sleep(wait_time)
            continue
        
        print(f"  ⚠ Error: {result.stderr[:100]}")
        time.sleep(3)
    
    return False


def get_user_token_with_retry(username, password, max_retries=5):
    """Get token with retry"""
    for attempt in range(max_retries):
        time.sleep(2)
        try:
            resp = requests.post(
                "http://localhost:8008/_matrix/client/r0/login",
                json={"type": "m.login.password", "user": username, "password": password},
                timeout=10
            )
            if resp.status_code == 200:
                token = resp.json().get("access_token")
                if token:
                    print(f"  ✓ Got token for {username}")
                    return token
        except Exception as e:
            print(f"  ⚠ Login attempt {attempt + 1} failed: {e}")
        time.sleep(3)
    return None


# =============================================================================
# TAILSCALE
# =============================================================================

def get_tailscale_hostname():
    """Get the Tailscale FQDN for this machine"""
    try:
        result = run_cmd([
            'docker', 'exec', 'memu_tailscale',
            'tailscale', 'status', '--json'
        ], check=False)
        
        if result.returncode == 0:
            status = json.loads(result.stdout)
            # Get our own DNS name
            dns_name = status.get('Self', {}).get('DNSName', '')
            if dns_name:
                # Remove trailing dot if present
                return dns_name.rstrip('.')
    except Exception as e:
        print(f"  ⚠ Could not get Tailscale hostname: {e}")
    
    return None


def configure_tailscale(domain, server_ip):
    """Configure Tailscale serve and update Element config with correct hostname"""
    global setup_state
    
    # Wait for Tailscale to be fully connected
    time.sleep(5)
    
    # Get Docker network gateway
    try:
        result = run_cmd([
            'docker', 'network', 'inspect', 'memu-suite_memu_net',
            '--format', '{{range .IPAM.Config}}{{.Gateway}}{{end}}'
        ], check=False)
        gateway = result.stdout.strip() or '172.18.0.1'
    except:
        gateway = '172.18.0.1'
    
    print(f"  Using gateway: {gateway}")
    
    # Configure Tailscale serve for Element (port 443) and Immich (port 8443)
    run_cmd([
        'docker', 'exec', 'memu_tailscale',
        'tailscale', 'serve', '--bg', '--https', '443', f'http://{gateway}:80'
    ], check=False)
    
    run_cmd([
        'docker', 'exec', 'memu_tailscale',
        'tailscale', 'serve', '--bg', '--https', '8443', f'http://{gateway}:2283'
    ], check=False)
    
    # Wait a moment for Tailscale to register
    time.sleep(3)
    
    # Get the Tailscale hostname
    ts_hostname = get_tailscale_hostname()
    
    if ts_hostname:
        print(f"  ✓ Tailscale hostname: {ts_hostname}")
        setup_state['tailscale_hostname'] = ts_hostname
        
        # Update Element config to use Tailscale HTTPS URL
        element_config = {
            "default_server_config": {
                "m.homeserver": {
                    "base_url": f"https://{ts_hostname}",
                    "server_name": domain
                }
            },
            "brand": "Memu",
            "default_theme": "light"
        }
        (PROJECT_ROOT / 'element-config.json').write_text(json.dumps(element_config, indent=2))
        
        # Restart Element to pick up new config
        run_cmd(['docker', 'restart', 'memu_element'], check=False)
        print("  ✓ Element config updated for Tailscale access")
        
        update_state('network', 12, f'Remote access configured: https://{ts_hostname}')
    else:
        print("  ⚠ Could not detect Tailscale hostname - Element config unchanged")
        update_state('network', 12, 'Remote access configured (hostname detection failed)',
                    warning='Could not auto-detect Tailscale URL. You may need to edit Element homeserver manually.')


def schedule_handoff():
    """Schedule the handoff from setup wizard to production services"""
    subprocess.run([
        "sudo", "systemd-run",
        "--unit=memu-handoff", "--description=Memu Handoff", "--no-block",
        "/bin/bash", "-c",
        "sleep 5; systemctl stop memu-setup.service; systemctl disable memu-setup.service; systemctl enable memu-production.service; systemctl start memu-production.service"
    ], check=False)


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("Memu Setup Wizard (v4.2)")
    print(f"Port: {WIZARD_PORT} | Project: {PROJECT_ROOT}")
    print("=" * 60)
    app.run(host='0.0.0.0', port=WIZARD_PORT, debug=False, threaded=True)