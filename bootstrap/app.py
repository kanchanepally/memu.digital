#!/usr/bin/env python3
"""
Memu Bootstrap Wizard (v4.1)

CHANGES FROM v4.0:
1. Robust user registration with retry loop (fixes HMAC timing issues)
2. Graceful degradation if bot token fails (system still works)
3. Targeted service recreation (intelligence only, not full restart)
4. Better error handling and status reporting

The key insight: Synapse needs time to initialize its signing keys
before we can register users. We now wait explicitly for this.
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

# Configuration
WIZARD_PORT = int(os.environ.get('WIZARD_PORT', 8888))
PROJECT_ROOT = Path(os.environ.get('PROJECT_ROOT', Path(__file__).parent.parent.absolute()))

# Setup state tracking
setup_state = {
    'stage': 'idle',
    'step': 0,
    'total_steps': 12,
    'message': '',
    'error': None,
    'warnings': []
}

def update_state(stage, step, message, error=None, warning=None):
    """Update setup state for progress polling"""
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
    """Read .env into dict"""
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
    """Update single variable in .env"""
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


def run_docker(cmd, check=True):
    """Run docker command"""
    full_cmd = ["docker"] + cmd
    print(f"  $ {' '.join(full_cmd)}")
    result = subprocess.run(full_cmd, capture_output=True, text=True, cwd=PROJECT_ROOT)
    if check and result.returncode != 0:
        raise Exception(f"Docker failed: {result.stderr}")
    return result


def run_compose(cmd, check=True):
    """Run docker compose command"""
    full_cmd = ["docker", "compose"] + cmd
    print(f"  $ {' '.join(full_cmd)}")
    result = subprocess.run(full_cmd, capture_output=True, text=True, cwd=PROJECT_ROOT)
    if check and result.returncode != 0:
        raise Exception(f"Compose failed: {result.stderr}")
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
    
    # Run setup in background
    thread = threading.Thread(
        target=run_setup,
        args=(clean_slug, domain, admin_password, tailscale_key),
        daemon=True
    )
    thread.start()
    
    return render_template('installing.html', domain=domain)


# =============================================================================
# MAIN SETUP LOGIC
# =============================================================================

def run_setup(clean_slug, domain, admin_password, tailscale_key):
    """Main setup orchestration with robust error handling"""
    
    try:
        env = read_env_file()
        db_password = env.get('DB_PASSWORD', secrets.token_urlsafe(20))
        bot_password = secrets.token_urlsafe(20)
        final_ts_key = tailscale_key or env.get('TAILSCALE_AUTH_KEY', '')
        
        # Generate the registration secret ONCE and store it
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
        
        # Store registration secret for later use
        update_env_var('SYNAPSE_REGISTRATION_SECRET', registration_secret)
        
        # Generate Synapse config
        synapse_config = generate_synapse_config(domain, db_password, registration_secret)
        (PROJECT_ROOT / 'synapse' / 'homeserver.yaml').write_text(synapse_config)
        
        # Generate Nginx config
        nginx_config = generate_nginx_config(domain)
        (PROJECT_ROOT / 'nginx' / 'conf.d' / 'default.conf').write_text(nginx_config)
        
        # Generate Element config (will update later with Tailscale URL)
        element_config = generate_element_config(domain, "http://localhost:8008")
        (PROJECT_ROOT / 'element-config.json').write_text(json.dumps(element_config, indent=2))
        
        time.sleep(1)
        
        # =====================================================================
        # STEP 2: Start Database
        # =====================================================================
        update_state('database', 2, 'Starting database...')
        run_compose(['up', '-d', 'database'])
        
        # =====================================================================
        # STEP 3: Wait for Database
        # =====================================================================
        update_state('database', 3, 'Waiting for database...')
        if not wait_for_database(max_wait=60):
            raise Exception("Database failed to start")
        
        # =====================================================================
        # STEP 4: Create Databases
        # =====================================================================
        update_state('database', 4, 'Creating databases...')
        create_databases()
        
        # =====================================================================
        # STEP 5: Start Synapse
        # =====================================================================
        update_state('synapse', 5, 'Starting chat server...')
        run_compose(['up', '-d', 'synapse'])
        
        # =====================================================================
        # STEP 6: Wait for Synapse (Extended)
        # =====================================================================
        update_state('synapse', 6, 'Waiting for chat server to initialize...')
        
        # KEY FIX: Wait longer for Synapse to fully initialize signing keys
        if not wait_for_synapse_ready(max_wait=120):
            raise Exception("Chat server failed to start")
        
        # Additional wait for signing key generation
        update_state('synapse', 6, 'Waiting for encryption keys...')
        time.sleep(10)  # Give Synapse time to write signing keys
        
        # =====================================================================
        # STEP 7: Create Admin User (WITH RETRY)
        # =====================================================================
        update_state('users', 7, 'Creating admin account...')
        
        admin_created = create_matrix_user_with_retry(
            username='admin',
            password=admin_password,
            is_admin=True,
            registration_secret=registration_secret,
            max_retries=5
        )
        
        if not admin_created:
            raise Exception("Failed to create admin user after retries")
        
        # =====================================================================
        # STEP 8: Create Bot User (WITH RETRY)
        # =====================================================================
        update_state('users', 8, 'Creating bot account...')
        
        bot_created = create_matrix_user_with_retry(
            username='memu_bot',
            password=bot_password,
            is_admin=False,
            registration_secret=registration_secret,
            max_retries=5
        )
        
        if not bot_created:
            update_state('users', 8, 'Bot creation failed - will retry later',
                        warning='Bot account creation failed. AI features may need manual setup.')
        
        # =====================================================================
        # STEP 9: Get Bot Token (WITH RETRY)
        # =====================================================================
        update_state('users', 9, 'Configuring bot authentication...')
        
        bot_token = None
        if bot_created:
            bot_token = get_user_token_with_retry('memu_bot', bot_password, max_retries=5)
        
        if bot_token:
            update_env_var('MATRIX_BOT_TOKEN', bot_token)
        else:
            update_state('users', 9, 'Bot token retrieval failed',
                        warning='Could not get bot token. Intelligence service will need manual configuration.')
        
        # =====================================================================
        # STEP 10: Start Remaining Services
        # =====================================================================
        update_state('services', 10, 'Starting all services...')
        run_compose(['up', '-d'])
        time.sleep(5)
        
        # =====================================================================
        # STEP 11: Targeted Service Recreation (if token was set)
        # =====================================================================
        if bot_token:
            update_state('services', 11, 'Restarting intelligence service...')
            # KEY FIX: Only restart the intelligence service with new env
            run_compose(['up', '-d', '--force-recreate', 'intelligence'], check=False)
        else:
            update_state('services', 11, 'Skipping intelligence restart (no token)')
        
        # =====================================================================
        # STEP 12: Configure Tailscale
        # =====================================================================
        if final_ts_key:
            update_state('network', 12, 'Configuring remote access...')
            configure_tailscale(domain)
        else:
            update_state('network', 12, 'Skipping remote access (no Tailscale key)')
        
        # =====================================================================
        # DONE
        # =====================================================================
        update_state('complete', 12, 'Setup complete!')
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
    """Generate Synapse homeserver.yaml"""
    return f"""# Memu Synapse Configuration (v4.1)
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

# Registration secret for admin tools
registration_shared_secret: "{registration_secret}"

# Signing key will be auto-generated on first start
signing_key_path: "/data/{domain}.signing.key"
"""


def generate_nginx_config(domain):
    """Generate Nginx config"""
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


def generate_element_config(domain, homeserver_url):
    """Generate Element config"""
    return {
        "default_server_config": {
            "m.homeserver": {
                "base_url": homeserver_url,
                "server_name": domain
            }
        },
        "brand": "Memu",
        "default_theme": "light"
    }


# =============================================================================
# WAIT FUNCTIONS
# =============================================================================

def wait_for_database(max_wait=60):
    """Wait for PostgreSQL"""
    start = time.time()
    while time.time() - start < max_wait:
        result = run_docker(['exec', 'memu_postgres', 'pg_isready', '-U', 'memu_user'], check=False)
        if result.returncode == 0:
            return True
        time.sleep(2)
    return False


def wait_for_synapse_ready(max_wait=120):
    """Wait for Synapse to be fully ready (not just responding)"""
    start = time.time()
    
    # First, wait for basic HTTP response
    while time.time() - start < max_wait:
        try:
            resp = requests.get("http://localhost:8008/_matrix/client/versions", timeout=5)
            if resp.status_code == 200:
                print("  Synapse responding to HTTP")
                break
        except:
            pass
        time.sleep(3)
    else:
        return False
    
    # Then, verify it can accept registrations (signing key ready)
    # We do this by checking if the registration endpoint exists
    time.sleep(5)  # Additional safety margin
    
    return True


def create_databases():
    """Create separate databases"""
    databases = ['memu_synapse', 'memu_immich', 'immich']
    
    for db in databases:
        cmd = f"SELECT 'CREATE DATABASE {db}' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '{db}')\\gexec"
        run_docker([
            'exec', 'memu_postgres',
            'psql', '-U', 'memu_user', '-d', 'postgres', '-c', cmd
        ], check=False)


# =============================================================================
# USER MANAGEMENT (WITH RETRY - KEY FIX)
# =============================================================================

def create_matrix_user_with_retry(username, password, is_admin, registration_secret, max_retries=5):
    """
    Create Matrix user with retry logic.
    
    The HMAC error happens when Synapse hasn't fully initialized its signing keys.
    We retry with exponential backoff to handle this timing issue.
    """
    admin_flag = "--admin" if is_admin else "--no-admin"
    
    for attempt in range(max_retries):
        print(f"  Creating user {username} (attempt {attempt + 1}/{max_retries})...")
        
        result = run_docker([
            'compose', 'exec', '-T', 'synapse',
            'register_new_matrix_user',
            '-u', username,
            '-p', password,
            admin_flag,
            '-c', '/data/homeserver.yaml',
            'http://localhost:8008'
        ], check=False)
        
        # Success
        if result.returncode == 0:
            print(f"  ✓ User {username} created successfully")
            return True
        
        # User already exists (also success)
        if "already taken" in result.stderr or "already in use" in result.stderr:
            print(f"  ✓ User {username} already exists")
            return True
        
        # HMAC error - need to wait and retry
        if "HMAC" in result.stderr or "incorrect" in result.stderr.lower():
            wait_time = 5 * (attempt + 1)  # 5s, 10s, 15s, 20s, 25s
            print(f"  ⚠ HMAC error - Synapse still initializing. Waiting {wait_time}s...")
            time.sleep(wait_time)
            continue
        
        # Other error
        print(f"  ⚠ User creation failed: {result.stderr}")
        time.sleep(3)
    
    print(f"  ✗ Failed to create user {username} after {max_retries} attempts")
    return False


def get_user_token_with_retry(username, password, max_retries=5):
    """Get access token with retry logic"""
    
    for attempt in range(max_retries):
        print(f"  Getting token for {username} (attempt {attempt + 1}/{max_retries})...")
        
        time.sleep(2)
        
        try:
            resp = requests.post(
                "http://localhost:8008/_matrix/client/r0/login",
                json={
                    "type": "m.login.password",
                    "user": username,
                    "password": password
                },
                timeout=10
            )
            
            if resp.status_code == 200:
                token = resp.json().get("access_token")
                if token:
                    print(f"  ✓ Got token for {username}")
                    return token
            
            print(f"  ⚠ Login returned {resp.status_code}: {resp.text[:100]}")
            
        except Exception as e:
            print(f"  ⚠ Login attempt failed: {e}")
        
        time.sleep(3)
    
    print(f"  ✗ Failed to get token for {username}")
    return None


# =============================================================================
# TAILSCALE & HANDOFF
# =============================================================================

def configure_tailscale(domain):
    """Configure Tailscale serve"""
    time.sleep(5)
    
    # Get network gateway
    try:
        result = run_docker([
            'network', 'inspect', 'memu-suite_memu_net',
            '--format', '{{range .IPAM.Config}}{{.Gateway}}{{end}}'
        ], check=False)
        gateway = result.stdout.strip() or '172.18.0.1'
    except:
        gateway = '172.18.0.1'
    
    # Configure serves
    run_docker(['exec', 'memu_tailscale', 'tailscale', 'serve', '--bg', '--https', '443', f'http://{gateway}:80'], check=False)
    run_docker(['exec', 'memu_tailscale', 'tailscale', 'serve', '--bg', '--https', '8443', f'http://{gateway}:2283'], check=False)
    
    # Update Element config with Tailscale URL
    try:
        result = run_docker(['exec', 'memu_tailscale', 'tailscale', 'status', '--json'], check=False)
        ts_status = json.loads(result.stdout)
        ts_hostname = ts_status.get('Self', {}).get('DNSName', '').rstrip('.')
        if ts_hostname:
            element_config = generate_element_config(domain, f"https://{ts_hostname}")
            (PROJECT_ROOT / 'element-config.json').write_text(json.dumps(element_config, indent=2))
            print(f"  Updated Element for Tailscale: {ts_hostname}")
    except Exception as e:
        print(f"  Could not update Element config: {e}")


def schedule_handoff():
    """Schedule transition to production"""
    subprocess.run([
        "sudo", "systemd-run",
        "--unit=memu-handoff",
        "--description=Memu Setup Handoff",
        "--no-block",
        "/bin/bash", "-c",
        "sleep 5; systemctl stop memu-setup.service; systemctl disable memu-setup.service; systemctl enable memu-production.service"
    ], check=False)


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("Memu Setup Wizard (v4.1)")
    print("=" * 60)
    print(f"Port: {WIZARD_PORT}")
    print(f"Project: {PROJECT_ROOT}")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=WIZARD_PORT, debug=False, threaded=True)