#!/usr/bin/env python3
"""
Memu Bootstrap Wizard (v4.0)
Web-based setup interface for first-time configuration

KEY CHANGE FROM v3: This wizard now STARTS containers in the correct order,
rather than assuming they're already running.

Flow:
1. User fills in form (family name, password, optional tailscale key)
2. Wizard creates all config files FIRST
3. Wizard starts database container
4. Wizard waits for database to be healthy
5. Wizard creates required databases (immich, synapse)
6. Wizard starts Synapse container
7. Wizard waits for Synapse to be healthy
8. Wizard creates Matrix users
9. Wizard starts remaining containers
10. Wizard configures Tailscale serve (if key provided)
11. Done!
"""

import os
import subprocess
import secrets
import time
import json
import requests
from pathlib import Path
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Configuration
WIZARD_PORT = int(os.environ.get('WIZARD_PORT', 8888))
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

# Setup state tracking (for progress polling)
setup_state = {
    'stage': 'idle',
    'step': 0,
    'total_steps': 10,
    'message': '',
    'error': None
}

def update_state(stage, step, message, error=None):
    """Update the global setup state for progress polling"""
    global setup_state
    setup_state = {
        'stage': stage,
        'step': step,
        'total_steps': 10,
        'message': message,
        'error': error
    }
    print(f"[{stage}] Step {step}/10: {message}")


def read_env_file():
    """Read current .env values into a dict"""
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
    """Update a single variable in .env"""
    env_path = PROJECT_ROOT / '.env'
    if not env_path.exists():
        env_path.write_text(f"{key}={value}\n")
        return
    
    lines = env_path.read_text().splitlines()
    found = False
    
    for i, line in enumerate(lines):
        if line.strip().startswith(f"{key}="):
            lines[i] = f"{key}={value}"
            found = True
            break
    
    if not found:
        lines.append(f"{key}={value}")
    
    env_path.write_text('\n'.join(lines) + '\n')


def get_system_timezone():
    """Get system timezone, fallback to UTC"""
    try:
        return Path('/etc/timezone').read_text().strip()
    except:
        return 'UTC'


def run_docker_command(cmd, check=True):
    """Run a docker command and return result"""
    full_cmd = ["docker"] + cmd
    print(f"  Running: {' '.join(full_cmd)}")
    result = subprocess.run(full_cmd, capture_output=True, text=True, cwd=PROJECT_ROOT)
    if check and result.returncode != 0:
        raise Exception(f"Docker command failed: {result.stderr}")
    return result


def run_compose_command(cmd, check=True):
    """Run a docker compose command"""
    full_cmd = ["docker", "compose"] + cmd
    print(f"  Running: {' '.join(full_cmd)}")
    result = subprocess.run(full_cmd, capture_output=True, text=True, cwd=PROJECT_ROOT)
    if check and result.returncode != 0:
        raise Exception(f"Compose command failed: {result.stderr}")
    return result


# =============================================================================
# ROUTES
# =============================================================================

@app.route('/')
def welcome():
    """Show initial setup form"""
    return render_template('setup.html')


@app.route('/status')
def status():
    """Return current setup status for progress polling"""
    return jsonify(setup_state)


@app.route('/configure', methods=['POST'])
def configure():
    """Process setup form and begin configuration"""
    
    # Get form data
    family_name = request.form.get('family_name', '').strip()
    admin_password = request.form.get('password', '').strip()
    tailscale_key = request.form.get('tailscale_key', '').strip()
    
    # Validate
    if not family_name or not admin_password:
        return "Missing required information (family name or password)", 400
    
    if len(admin_password) < 8:
        return "Password must be at least 8 characters", 400
    
    # Clean family name for domain
    clean_slug = "".join(c for c in family_name if c.isalnum()).lower()
    if not clean_slug:
        return "Family name must contain at least one letter or number", 400
    
    domain = f"{clean_slug}.memu.digital"
    
    # Show progress page immediately (actual work happens via polling)
    # We'll spawn the actual setup in a background thread
    import threading
    thread = threading.Thread(
        target=run_setup,
        args=(clean_slug, domain, admin_password, tailscale_key)
    )
    thread.start()
    
    return render_template('installing.html', domain=domain)


def run_setup(clean_slug, domain, admin_password, tailscale_key):
    """
    Main setup logic - runs in background thread.
    This is where the magic happens.
    """
    
    try:
        # Read existing env
        env = read_env_file()
        db_password = env.get('DB_PASSWORD', secrets.token_urlsafe(20))
        bot_password = secrets.token_urlsafe(20)
        
        # Merge Tailscale key (form input takes priority over .env)
        final_ts_key = tailscale_key or env.get('TAILSCALE_AUTH_KEY', '')
        
        # =========================================================
        # STEP 1: Generate Configuration Files
        # =========================================================
        update_state('config', 1, 'Generating configuration files...')
        
        # Update .env with final values
        update_env_var('SERVER_NAME', domain)
        update_env_var('DB_PASSWORD', db_password)
        update_env_var('MATRIX_BOT_USERNAME', f'@memu_bot:{domain}')
        if final_ts_key:
            update_env_var('TAILSCALE_AUTH_KEY', final_ts_key)
        
        # Generate Synapse config (uses SEPARATE database)
        synapse_config = generate_synapse_config(domain, db_password)
        synapse_path = PROJECT_ROOT / 'synapse' / 'homeserver.yaml'
        synapse_path.write_text(synapse_config)
        
        # Generate Nginx config
        nginx_config = generate_nginx_config(domain)
        nginx_path = PROJECT_ROOT / 'nginx' / 'conf.d' / 'default.conf'
        nginx_path.write_text(nginx_config)
        
        # Generate Element config (will be updated again after Tailscale)
        element_config = generate_element_config(domain, "http://localhost:8008")
        element_path = PROJECT_ROOT / 'element-config.json'
        element_path.write_text(json.dumps(element_config, indent=2))
        
        time.sleep(1)  # Brief pause for filesystem
        
        # =========================================================
        # STEP 2: Start Database Container
        # =========================================================
        update_state('database', 2, 'Starting database...')
        
        run_compose_command(['up', '-d', 'database'])
        
        # =========================================================
        # STEP 3: Wait for Database Health
        # =========================================================
        update_state('database', 3, 'Waiting for database to be ready...')
        
        if not wait_for_database(max_wait=60):
            raise Exception("Database failed to start. Check: docker compose logs database")
        
        # =========================================================
        # STEP 4: Create Separate Databases
        # =========================================================
        update_state('database', 4, 'Creating databases...')
        
        create_databases(db_password)
        
        # =========================================================
        # STEP 5: Start Synapse
        # =========================================================
        update_state('synapse', 5, 'Starting chat server...')
        
        run_compose_command(['up', '-d', 'synapse'])
        
        # =========================================================
        # STEP 6: Wait for Synapse Health
        # =========================================================
        update_state('synapse', 6, 'Waiting for chat server...')
        
        if not wait_for_synapse(max_wait=90):
            raise Exception("Chat server failed to start. Check: docker compose logs synapse")
        
        # =========================================================
        # STEP 7: Create Matrix Users
        # =========================================================
        update_state('users', 7, 'Creating user accounts...')
        
        # Create admin user
        create_matrix_user('admin', admin_password, is_admin=True)
        time.sleep(2)
        
        # Create bot user
        create_matrix_user('memu_bot', bot_password, is_admin=False)
        time.sleep(2)
        
        # Get bot token
        bot_token = get_user_token('memu_bot', bot_password)
        if bot_token:
            update_env_var('MATRIX_BOT_TOKEN', bot_token)
        else:
            print("WARNING: Could not get bot token. Bot features may not work.")
        
        # =========================================================
        # STEP 8: Start Remaining Services
        # =========================================================
        update_state('services', 8, 'Starting all services...')
        
        # Start everything else
        run_compose_command(['up', '-d'])
        
        time.sleep(5)  # Let services settle
        
        # =========================================================
        # STEP 9: Configure Tailscale (if key provided)
        # =========================================================
        if final_ts_key:
            update_state('network', 9, 'Configuring remote access...')
            configure_tailscale(domain)
        else:
            update_state('network', 9, 'Skipping remote access (no Tailscale key)')
        
        # =========================================================
        # STEP 10: Success!
        # =========================================================
        update_state('complete', 10, f'Setup complete! Your server is ready.')
        
        # Schedule handoff to production service
        schedule_handoff()
        
    except Exception as e:
        update_state('error', setup_state['step'], str(e), error=str(e))
        print(f"SETUP FAILED: {e}")
        import traceback
        traceback.print_exc()


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def generate_synapse_config(domain, db_password):
    """Generate Synapse homeserver.yaml"""
    
    registration_secret = secrets.token_urlsafe(32)
    
    return f"""# Memu Synapse Configuration
# Generated by Setup Wizard

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

# CRITICAL: Synapse uses its OWN database (not shared with Immich)
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
enable_registration_captcha: false
report_stats: false

media_store_path: /data/media_store

registration_shared_secret: "{registration_secret}"

# Logging
log_config: "/data/memu.local.log.config"
"""


def generate_nginx_config(domain):
    """Generate Nginx reverse proxy config"""
    
    return f"""server {{
    listen 80;
    server_name localhost;

    resolver 127.0.0.11 valid=30s;

    # Matrix API
    location ~ ^/(_matrix|_synapse/client) {{
        set $upstream_synapse http://synapse:8008;
        proxy_pass $upstream_synapse;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $host;
        client_max_body_size 50M;
    }}

    # Element Web (Chat UI)
    location / {{
        set $upstream_element http://element:80;
        proxy_pass $upstream_element;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header Host $host;
    }}

    # Matrix Federation Discovery
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
    """Generate Element Web config"""
    return {
        "default_server_config": {
            "m.homeserver": {
                "base_url": homeserver_url,
                "server_name": domain
            }
        },
        "brand": "Memu",
        "default_theme": "light",
        "show_labs_settings": True
    }


def wait_for_database(max_wait=60):
    """Wait for PostgreSQL to be healthy"""
    start = time.time()
    
    while time.time() - start < max_wait:
        result = run_docker_command(
            ['exec', 'memu_postgres', 'pg_isready', '-U', 'memu_user'],
            check=False
        )
        if result.returncode == 0:
            return True
        time.sleep(2)
    
    return False


def create_databases(db_password):
    """Create separate databases for Synapse and Immich"""
    
    # Commands to create databases (if they don't exist)
    commands = [
        "SELECT 'CREATE DATABASE memu_synapse' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'memu_synapse')\\gexec",
        "SELECT 'CREATE DATABASE memu_immich' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'memu_immich')\\gexec",
    ]
    
    for cmd in commands:
        run_docker_command([
            'exec', 'memu_postgres',
            'psql', '-U', 'memu_user', '-d', 'postgres', '-c', cmd
        ], check=False)
    
    # Also ensure the 'immich' database exists (for backward compatibility)
    run_docker_command([
        'exec', 'memu_postgres',
        'psql', '-U', 'memu_user', '-d', 'postgres', '-c',
        "SELECT 'CREATE DATABASE immich' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'immich')\\gexec"
    ], check=False)


def wait_for_synapse(max_wait=90):
    """Wait for Synapse to respond"""
    start = time.time()
    
    while time.time() - start < max_wait:
        try:
            resp = requests.get("http://localhost:8008/_matrix/client/versions", timeout=3)
            if resp.status_code == 200:
                return True
        except:
            pass
        time.sleep(3)
    
    return False


def create_matrix_user(username, password, is_admin=False):
    """Create a Matrix user account"""
    admin_flag = "--admin" if is_admin else "--no-admin"
    
    result = run_docker_command([
        'compose', 'exec', '-T', 'synapse',
        'register_new_matrix_user',
        '-u', username,
        '-p', password,
        admin_flag,
        '-c', '/data/homeserver.yaml',
        'http://localhost:8008'
    ], check=False)
    
    if result.returncode != 0:
        if "already taken" in result.stderr or "already in use" in result.stderr:
            print(f"  User {username} already exists (ok)")
        else:
            print(f"  WARNING: User creation may have failed: {result.stderr}")


def get_user_token(username, password, retries=5):
    """Get access token via Matrix login"""
    
    for attempt in range(retries):
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
                return resp.json().get("access_token")
        except Exception as e:
            print(f"  Login attempt {attempt+1} failed: {e}")
    
    return None


def configure_tailscale(domain):
    """Configure Tailscale serve for ingress"""
    
    # Wait for Tailscale to be connected
    time.sleep(5)
    
    # Get the Docker network gateway (where nginx listens)
    # This is typically 172.x.0.1 on the memu_net bridge
    try:
        result = run_docker_command([
            'network', 'inspect', 'memu-suite_memu_net',
            '--format', '{{range .IPAM.Config}}{{.Gateway}}{{end}}'
        ], check=False)
        gateway = result.stdout.strip() or '172.18.0.1'
    except:
        gateway = '172.18.0.1'
    
    # Configure tailscale serve for main web interface (port 443)
    run_docker_command([
        'exec', 'memu_tailscale',
        'tailscale', 'serve', '--bg', '--https', '443',
        f'http://{gateway}:80'
    ], check=False)
    
    # Configure tailscale serve for Immich photos (port 8443)
    run_docker_command([
        'exec', 'memu_tailscale',
        'tailscale', 'serve', '--bg', '--https', '8443',
        f'http://{gateway}:2283'
    ], check=False)
    
    # Get Tailscale hostname for Element config
    result = run_docker_command([
        'exec', 'memu_tailscale',
        'tailscale', 'status', '--json'
    ], check=False)
    
    try:
        ts_status = json.loads(result.stdout)
        ts_hostname = ts_status.get('Self', {}).get('DNSName', '').rstrip('.')
        if ts_hostname:
            # Update Element config with Tailscale URL
            element_config = generate_element_config(domain, f"https://{ts_hostname}")
            element_path = PROJECT_ROOT / 'element-config.json'
            element_path.write_text(json.dumps(element_config, indent=2))
            print(f"  Updated Element config for Tailscale: {ts_hostname}")
    except:
        print("  Could not update Element config with Tailscale URL")


def schedule_handoff():
    """Schedule transition from setup wizard to production service"""
    
    handoff_script = (
        "sleep 5; "
        "systemctl stop memu-setup.service; "
        "systemctl disable memu-setup.service; "
        "systemctl enable memu-production.service; "
    )
    
    subprocess.run([
        "sudo", "systemd-run",
        "--unit=memu-handoff",
        "--description=Memu Setup Handoff",
        "--no-block",
        "/bin/bash", "-c", handoff_script
    ], check=False)


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("Memu Setup Wizard (v4.0)")
    print("=" * 60)
    print(f"Listening on port {WIZARD_PORT}")
    print(f"Project root: {PROJECT_ROOT}")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=WIZARD_PORT, debug=False, threaded=True)