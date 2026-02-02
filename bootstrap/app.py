#!/usr/bin/env python3
"""
Memu Bootstrap & Admin Server (v5.1)

This combines:
1. Initial setup wizard (existing functionality)
2. Admin dashboard API (new)
3. Family member management (new)
4. QR code generation (new)

CHANGELOG v5.1:
- Added SQLite persistence (memu.db)
- Added Authentication (Session-based)

ENDPOINTS:
  Public:
    GET  /                    → Setup wizard (if not configured) or Login redirect
    POST /configure           → Run initial configuration
    GET  /status              → Installation progress
    GET  /login               → Login page
    POST /login               → Handle login
    GET  /welcome/<username>  → Welcome page for new member

  Protected (Login Required):
    GET  /admin               → Admin dashboard
    GET  /logout              → Logout
    GET  /api/sanctuary       → Sanctuary info (name, URL, stats)
    GET  /api/health          → Service health status
    GET  /api/family/members  → List all family members
    POST /api/family/members  → Create new family member
    GET  /api/family/members/<username>/qr  → QR code image
    GET  /api/family/members/<username>/card → Printable welcome card
"""

import os
import subprocess
import secrets
import time
import json
import requests
import threading
import io
import base64
import sqlite3
import logging
from pathlib import Path
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, render_template, render_template_string, request, jsonify, send_file, redirect, url_for, session, g

# QR Code generation
try:
    import qrcode
    from qrcode.image.styledpil import StyledPilImage
    from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False
    print("Warning: qrcode not installed. Run: pip install qrcode[pil]")

SERVER_IP = "127.0.0.1" # Default fallback

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', secrets.token_hex(32))
app.permanent_session_lifetime = timedelta(days=7)

WIZARD_PORT = int(os.environ.get('WIZARD_PORT', 8888))
PROJECT_ROOT = Path(os.environ.get('PROJECT_ROOT', Path(__file__).parent.parent.absolute()))
DATABASE = PROJECT_ROOT / 'bootstrap' / 'memu.db'

# =============================================================================
# DATABASE & PERSISTENCE
# =============================================================================

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    """Initialize the database tables"""
    with app.app_context():
        db = get_db()
        # Members table
        db.execute('''
            CREATE TABLE IF NOT EXISTS members (
                username TEXT PRIMARY KEY,
                display_name TEXT NOT NULL,
                password TEXT,
                user_id TEXT,
                is_admin BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'invited'
            )
        ''')
        # Sanctuary Settings table
        db.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        db.commit()

# Initialize DB on start
if not DATABASE.exists():
    init_db()

# =============================================================================
# STATE MANAGEMENT
# =============================================================================

setup_state = {
    'stage': 'idle',
    'step': 0,
    'total_steps': 12,
    'message': '',
    'error': None,
    'warnings': [],
    'tailscale_hostname': None,
    'configured': False,
    'family_name': None,
    'domain': None
}

def load_sanctuary_config():
    """Load sanctuary configuration from .env"""
    env_path = PROJECT_ROOT / '.env'
    config = {
        'family_name': None,
        'domain': None,
        'tailscale_hostname': None,
        'configured': False
    }
    
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, val = line.split('=', 1)
            key, val = key.strip(), val.strip()
            
            if key == 'SERVER_NAME' and val != 'memu.local':
                config['domain'] = val
                # Extract family name from domain or get from DB
                try:
                    # Only try DB if exists to avoid recursion or startup issues
                    if DATABASE.exists():
                        # We need to be careful not to trigger get_db() outside context if not active
                        # But load_sanctuary_config is often called inside views.
                        # If called outside, we might have issues.
                        # Let's rely on .env for critical boostrap, DB for display name if safe.
                        # For simple script usage, stick to .env parsing + safe DB check if possible.
                        pass 
                except:
                    pass
                
                # Check DB for family name override if we are in app context
                if g: 
                    try:
                        db = get_db()
                        row = db.execute("SELECT value FROM settings WHERE key='family_name'").fetchone()
                        if row:
                             config['family_name'] = row['value']
                    except:
                        pass # Outside app context or DB error
                
                if not config['family_name']:
                    config['family_name'] = val.split('.')[0].title()
                
                config['configured'] = True
            elif key == 'TAILSCALE_HOSTNAME':
                config['tailscale_hostname'] = val
    
    return config


def is_configured():
    """Check if initial setup has been completed"""
    config = load_sanctuary_config()
    return config['configured']


# =============================================================================
# AUTHENTICATION
# =============================================================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def check_auth(password):
    """Check against admin password in .env or settings"""
    # 1. Check DB for admin user
    try:
        db = get_db()
        user = db.execute("SELECT password FROM members WHERE username='admin'").fetchone()
        if user and user['password'] == password:
            return True
    except:
        pass
        
    # 2. Fallback: Check if it matches what we might have in .env or setup state?
    # Actually, if DB is down we are in trouble anyway.
    
    return False

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def read_env_file():
    """Read .env file into dict"""
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
    """Update a single variable in .env file"""
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


def generate_password(length=12):
    """Generate a human-friendly password"""
    # Avoid confusing characters: 0/O, 1/l/I
    chars = 'abcdefghjkmnpqrstuvwxyzABCDEFGHJKMNPQRSTUVWXYZ23456789'
    return ''.join(secrets.choice(chars) for _ in range(length))


def get_tailscale_hostname():
    """Get the Tailscale FQDN for this machine"""
    try:
        result = run_cmd([
            'docker', 'exec', 'memu_tailscale',
            'tailscale', 'status', '--json'
        ], check=False)
        
        if result.returncode == 0:
            status = json.loads(result.stdout)
            dns_name = status.get('Self', {}).get('DNSName', '')
            if dns_name:
                return dns_name.rstrip('.')
    except Exception as e:
        print(f"Could not get Tailscale hostname: {e}")
    
    return None


def get_base_url():
    """Get the base URL for the sanctuary"""
    config = load_sanctuary_config()
    
    # Try Tailscale hostname first
    ts_hostname = config.get('tailscale_hostname') or get_tailscale_hostname()
    if ts_hostname:
        return f"http://{ts_hostname}"
    
    # Fallback to local IP
    try:
        host_ip = request.host.split(':')[0]
    except:
        host_ip = SERVER_IP
        
    return f"http://{host_ip}"


# =============================================================================
# QR CODE GENERATION
# =============================================================================

def generate_qr_code(data, size=300):
    """Generate a QR code image"""
    if not QR_AVAILABLE:
        return None
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    # Create styled image with rounded modules
    try:
        img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=RoundedModuleDrawer()
        )
    except:
        # Fallback to basic image
        img = qr.make_image(fill_color="black", back_color="white")
    
    # Resize
    img = img.resize((size, size))
    
    # Convert to bytes
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    return img_buffer


def generate_qr_base64(data, size=200):
    """Generate QR code as base64 string for embedding in HTML"""
    img_buffer = generate_qr_code(data, size)
    if img_buffer:
        return base64.b64encode(img_buffer.getvalue()).decode('utf-8')
    return None


# =============================================================================
# MATRIX USER MANAGEMENT
# =============================================================================

def create_matrix_user(username, password, display_name=None):
    """Create a Matrix user via Synapse admin API"""
    config = load_sanctuary_config()
    domain = config.get('domain', 'memu.local')
    
    # Use register_new_matrix_user command
    result = run_cmd([
        'docker', 'compose', 'exec', '-T', 'synapse',
        'register_new_matrix_user',
        '-u', username,
        '-p', password,
        '--no-admin',
        '-c', '/data/homeserver.yaml',
        'http://localhost:8008'
    ], check=False)
    
    if result.returncode == 0:
        return {'success': True, 'user_id': f'@{username}:{domain}'}
    
    if "already taken" in result.stderr or "already in use" in result.stderr:
        return {'success': True, 'user_id': f'@{username}:{domain}', 'existed': True}
    
    return {'success': False, 'error': result.stderr}


# =============================================================================
# ROUTES: AUTHENTICATION
# =============================================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if check_auth(password):
            session.permanent = True
            session['logged_in'] = True
            
            # Check for redirect
            next_url = request.args.get('next')
            if next_url and next_url.startswith('/'):
                 return redirect(next_url)
            return redirect('/admin')
        else:
            config = load_sanctuary_config()
            return render_template('login.html', 
                                  family_name=config.get('family_name', 'Family'),
                                  error="Invalid password")
    
    # GET
    if session.get('logged_in'):
        return redirect('/admin')
        
    config = load_sanctuary_config()
    return render_template('login.html', family_name=config.get('family_name', 'Family'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# =============================================================================
# ROUTES: SETUP WIZARD & PUBLIC
# =============================================================================

@app.route('/')
def index():
    """Main entry point"""
    if is_configured():
        return redirect('/admin') # Will redirect to login if needed via login_required logic on /admin
    return render_template('setup.html')


@app.route('/status')
def status():
    """Installation progress status"""
    return jsonify(setup_state)


@app.route('/configure', methods=['POST'])
def configure():
    """Run initial configuration"""
    family_name = request.form.get('family_name', '').strip()
    admin_name = request.form.get('admin_name', 'Admin').strip()
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
    
    # Store for later use
    setup_state['family_name'] = family_name
    setup_state['domain'] = domain
    
    # Capture server IP for the thread
    try:
        server_ip = request.host.split(':')[0]
    except:
        server_ip = 'localhost'
    
    # Start setup thread
    thread = threading.Thread(
        target=run_setup,
        args=(clean_slug, domain, admin_password, tailscale_key, server_ip, admin_name, app.app_context),
        daemon=True
    )
    thread.start()
    
    return render_template('creating-sanctuary.html', 
                          family_name=family_name.title(),
                          domain=domain)


# =============================================================================
# ROUTES: ADMIN DASHBOARD (PROTECTED)
# =============================================================================

@app.route('/admin')
@login_required
def admin_dashboard():
    """Admin dashboard"""
    if not is_configured():
        return redirect('/')
    
    config = load_sanctuary_config()
    
    # Get Admin Name
    admin_name = "Admin"
    try:
        db = get_db()
        user = db.execute("SELECT display_name FROM members WHERE username='admin'").fetchone()
        if user:
            admin_name = user['display_name']
    except:
        pass

    return render_template('admin-dashboard.html',
                          family_name=config.get('family_name', 'Family'),
                          domain=config.get('domain', 'memu.local'),
                          tailscale_hostname=config.get('tailscale_hostname'),
                          admin_name=admin_name)


@app.route('/api/sanctuary')
@login_required
def api_sanctuary():
    """Get sanctuary information"""
    config = load_sanctuary_config()
    ts_hostname = get_tailscale_hostname()
    
    base_url = f"https://{ts_hostname}" if ts_hostname else f"http://{request.host.split(':')[0]}"
    
    return jsonify({
        'family_name': config.get('family_name', 'Family'),
        'domain': config.get('domain', 'memu.local'),
        'base_url': base_url,
        'tailscale_hostname': ts_hostname,
        'configured': config.get('configured', False)
    })


@app.route('/api/health')
@login_required
def api_health():
    """Get service health status"""
    services = []
    
    # Check each service
    service_checks = [
        ('synapse', 'Chat (Matrix)', '💬', 'http://localhost:8008/_matrix/client/versions'),
        ('immich_server', 'Photos (Immich)', '📷', 'http://localhost:2283/api/server-info/ping'),
        ('ollama', 'AI (Ollama)', '🤖', 'http://localhost:11434/api/tags'),
        ('database', 'Database', '🗄️', None),  # Check via docker
        ('tailscale', 'Network (Tailscale)', '🌐', None),  # Check via docker
    ]
    
    # Service ID to Container Name mapping
    container_map = {
        'synapse': 'memu_synapse',
        'immich_server': 'memu_photos',
        'ollama': 'memu_brain',
        'database': 'memu_postgres',
        'tailscale': 'memu_tailscale'
    }

    for service_id, name, icon, health_url in service_checks:
        status = 'unknown'
        
        # Try HTTP health check
        if health_url:
            try:
                resp = requests.get(health_url, timeout=3)
                status = 'running' if resp.status_code == 200 else 'stopped'
            except:
                # If HTTP fails, fall back to Docker check
                status = 'stopped'

        # If stopped or no URL, double check via Docker status
        if not health_url or status == 'stopped':
            container_name = container_map.get(service_id, f'memu_{service_id}')
            result = run_cmd(['docker', 'ps', '--filter', f'name={container_name}', 
                            '--format', '{{.Status}}'], check=False)
            if 'Up' in result.stdout:
                status = 'running'
            elif result.stdout.strip():
                status = 'stopped'
            else:
                status = 'not_found'
        
        services.append({
            'id': service_id,
            'name': name,
            'icon': icon,
            'status': status
        })
    
    return jsonify({'services': services})


# =============================================================================
# ROUTES: FAMILY MEMBER MANAGEMENT (PROTECTED)
# =============================================================================

@app.route('/api/family/members', methods=['GET'])
@login_required
def list_family_members():
    """List all family members from DB"""
    db = get_db()
    rows = db.execute("SELECT * FROM members ORDER BY is_admin DESC, created_at ASC").fetchall()
    members = [dict(row) for row in rows]
    return jsonify({'members': members})


@app.route('/api/family/members', methods=['POST'])
@login_required
def create_family_member():
    """Create a new family member"""
    data = request.get_json()
    
    display_name = data.get('display_name', '').strip()
    username = data.get('username', '').strip().lower()
    password = data.get('password', '').strip()
    
    if not display_name:
        return jsonify({'error': 'Display name is required'}), 400
    
    if not username:
        # Generate from display name
        username = ''.join(c for c in display_name.lower() if c.isalnum())[:20]
    
    if not username:
        return jsonify({'error': 'Valid username is required'}), 400
    
    # Check if already exists
    db = get_db()
    existing = db.execute("SELECT 1 FROM members WHERE username = ?", (username,)).fetchone()
    if existing:
        return jsonify({'error': 'Username already exists'}), 409
    
    # Generate password if not provided
    if not password:
        password = generate_password()
    
    # Create Matrix user (system level)
    result = create_matrix_user(username, password, display_name)
    
    if not result.get('success'):
        return jsonify({'error': result.get('error', 'Failed to create user')}), 500
    
    config = load_sanctuary_config()
    domain = config.get('domain', 'memu.local')
    base_url = get_base_url()
    
    user_id = f'@{username}:{domain}'
    welcome_url = f'{base_url}/welcome/{username}'
    
    # Store member info in DB
    try:
        db.execute("""
            INSERT INTO members (username, display_name, password, user_id, status)
            VALUES (?, ?, ?, ?, 'invited')
        """, (username, display_name, password, user_id))
        db.commit()
    except Exception as e:
        return jsonify({'error': f"Database error: {e}"}), 500
    
    return jsonify({
        'success': True,
        'member': {
            'username': username,
            'display_name': display_name,
            'password': password,
            'user_id': user_id,
            'welcome_url': welcome_url,
            'qr_url': f'/api/family/members/{username}/qr'
        }
    })


@app.route('/api/family/members/<username>/qr')
@login_required
def get_member_qr(username):
    """Generate QR code for family member welcome page"""
    base_url = get_base_url()
    welcome_url = f'{base_url}/welcome/{username}'
    
    if not QR_AVAILABLE:
        # Return a redirect to external QR service as fallback
        return redirect(f'https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={welcome_url}')
    
    img_buffer = generate_qr_code(welcome_url, size=250)
    
    if img_buffer:
        return send_file(img_buffer, mimetype='image/png')
    
    return jsonify({'error': 'Failed to generate QR code'}), 500


@app.route('/api/family/members/<username>/card')
@login_required
def get_member_card(username):
    """Get printable welcome card for a family member"""
    db = get_db()
    member = db.execute("SELECT * FROM members WHERE username = ?", (username,)).fetchone()
    
    if not member:
        # Valid only if trying to print card for a non-persisted user? unlikely.
        # Fallback just in case logic
        member = {
            'username': username,
            'display_name': username.title(),
            'password': '(ask admin)'
        }
    
    config = load_sanctuary_config()
    base_url = get_base_url()
    welcome_url = f'{base_url}/welcome/{username}'
    
    return render_template('welcome-card.html',
                          family_name=config.get('family_name', 'Family'),
                          display_name=member['display_name'],
                          username=member['username'],
                          password=member['password'],
                          welcome_url=welcome_url,
                          qr_base64=generate_qr_base64(welcome_url))


# =============================================================================
# ROUTES: WELCOME PAGE (Public, with UUID/Username)
# =============================================================================

@app.route('/welcome/<username>')
def welcome_page(username):
    """Welcome page for new family members - what they see after scanning QR"""
    config = load_sanctuary_config()
    
    # Get member info from DB
    db = get_db()
    member = db.execute("SELECT * FROM members WHERE username = ?", (username,)).fetchone()
    
    if not member:
         return "Member not found", 404

    # Determine URLs
    ts_hostname = get_tailscale_hostname()
    if ts_hostname:
        chat_url = f'http://{ts_hostname}'
        photos_url = f'http://{ts_hostname}:2283'
    else:
        chat_url = f'http://{request.host.split(":")[0]}'
        photos_url = f'http://{request.host.split(":")[0]}:2283'
    
    return render_template('welcome-member.html',
                          family_name=config.get('family_name', 'Family'),
                          display_name=member['display_name'],
                          username=username,
                          password=member['password'],
                          domain=config.get('domain', 'memu.local'),
                          chat_url=chat_url,
                          photos_url=photos_url)


# =============================================================================
# SETUP PROCESS
# =============================================================================

def update_state(stage, step, message, error=None, warning=None):
    """Update setup state"""
    global setup_state
    setup_state['stage'] = stage
    setup_state['step'] = step
    setup_state['message'] = message
    setup_state['error'] = error
    if warning:
        setup_state['warnings'].append(warning)
    print(f"[{stage}] Step {step}/12: {message}")


def run_setup(clean_slug, domain, admin_password, tailscale_key, server_ip, admin_name, app_context_provider):
    """Main setup process"""
    # Need new app context since this is a separate thread
    with app_context_provider():
        try:
            env = read_env_file()
            db_password = env.get('DB_PASSWORD', secrets.token_urlsafe(20))
            bot_password = secrets.token_urlsafe(20)
            final_ts_key = tailscale_key or env.get('TAILSCALE_AUTH_KEY', '')
            registration_secret = secrets.token_urlsafe(32)
            
            # Save settings to DB
            db = get_db()
            db.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('family_name', ?)", (setup_state['family_name'],))
            db.commit()

            # Step 1: Generate configs
            update_state('config', 1, 'Preparing your private space...')
            
            update_env_var('SERVER_NAME', domain)
            update_env_var('DB_PASSWORD', db_password)
            update_env_var('MATRIX_BOT_USERNAME', f'@memu_bot:{domain}')
            if final_ts_key:
                update_env_var('TAILSCALE_AUTH_KEY', final_ts_key)
            
            synapse_config = generate_synapse_config(domain, db_password, registration_secret)
            (PROJECT_ROOT / 'synapse' / 'homeserver.yaml').write_text(synapse_config)
            
            nginx_config = generate_nginx_config(domain)
            (PROJECT_ROOT / 'nginx' / 'conf.d' / 'default.conf').write_text(nginx_config)
            
            time.sleep(1)
            
            # Step 2-4: Database
            update_state('database', 2, 'Setting up the foundation...')
            run_cmd(['docker', 'compose', 'up', '-d', 'database'])
            
            update_state('database', 3, 'Waiting for database...')
            if not wait_for_database(max_wait=60):
                raise Exception("Database failed to start")
            
            update_state('database', 4, 'Creating data stores...')
            create_databases()
            
            # Step 5-6: Synapse
            update_state('synapse', 5, 'Building the family chat room...')
            run_cmd(['docker', 'compose', 'up', '-d', 'synapse'])
            
            update_state('synapse', 6, 'Preparing chat server...')
            if not wait_for_synapse(max_wait=90):
                raise Exception("Chat server failed to start")
            
            run_cmd(['docker', 'compose', 'restart', 'synapse'])
            time.sleep(10)
            
            if not wait_for_synapse(max_wait=60):
                raise Exception("Chat server failed after restart")
            
            # Step 7-9: Users
            update_state('users', 7, 'Creating your admin account...')
            admin_created = create_matrix_user_with_retry('admin', admin_password, is_admin=True)
            if not admin_created:
                raise Exception("Failed to create admin user")
            
            # Persist admin in local DB
            try:
                db.execute("INSERT OR REPLACE INTO members (username, display_name, password, user_id, is_admin, status) VALUES (?, ?, ?, ?, 1, 'online')",
                           ('admin', admin_name, admin_password, f'@admin:{domain}'))
                db.commit()
            except Exception as e:
                print(f"Warning: Failed to persist admin: {e}")

            update_state('users', 8, 'Setting up your photo vault...')
            bot_created = create_matrix_user_with_retry('memu_bot', bot_password, is_admin=False)
            
            update_state('users', 9, 'Waking up your AI assistant...')
            bot_token = None
            if bot_created:
                bot_token = get_user_token_with_retry('memu_bot', bot_password)
            
            if bot_token:
                update_env_var('MATRIX_BOT_TOKEN', bot_token)
            
            # Step 10-11: Services
            update_state('services', 10, 'Starting all services...')
            
            element_config = {
                "default_server_config": {
                    "m.homeserver": {
                        "base_url": "/",
                        "server_name": domain
                    }
                },
                "brand": "Memu",
                "default_theme": "light"
            }
            (PROJECT_ROOT / 'element-config.json').write_text(json.dumps(element_config, indent=2))
            
            update_state('services', 11, 'Bringing everything online...')
            run_cmd(['docker', 'compose', 'up', '-d'])
            time.sleep(5)
            
            if bot_token:
                run_cmd(['docker', 'compose', 'up', '-d', '--force-recreate', 'intelligence'], check=False)
            
            # Step 12: Network
            if final_ts_key:
                update_state('network', 12, 'Connecting to your private network...')
                configure_tailscale(domain, server_ip)
            else:
                update_state('network', 12, 'Finalizing...')
            
            # Done
            ts_hostname = setup_state.get('tailscale_hostname')
            setup_state['configured'] = True
            
            if ts_hostname:
                update_env_var('TAILSCALE_HOSTNAME', ts_hostname)
                update_state('complete', 12, f'Welcome home! Your sanctuary is ready.')
            else:
                update_state('complete', 12, f'Welcome home! Your sanctuary is ready.')
            
        except Exception as e:
            update_state('error', setup_state['step'], str(e), error=str(e))
            print(f"SETUP FAILED: {e}")
            import traceback
            traceback.print_exc()


# =============================================================================
# HELPER FUNCTIONS (from original app.py)
# =============================================================================

def generate_synapse_config(domain, db_password, registration_secret):
    return f"""# Memu Synapse Configuration
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

    # === Admin & Setup Routes (Bootstrap Service) ===
    # These need to go to the bootstrap container on port 8888
    location ~ ^/(admin|login|logout|welcome|api|status|static) {{
        set $upstream_bootstrap http://bootstrap:8888;
        proxy_pass $upstream_bootstrap;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $host;
    }}

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


def wait_for_database(max_wait=60):
    start = time.time()
    while time.time() - start < max_wait:
        result = run_cmd(['docker', 'exec', 'memu_postgres', 'pg_isready', '-U', 'memu_user'], check=False)
        if result.returncode == 0:
            return True
        time.sleep(2)
    return False


def create_databases():
    """Create Synapse and Immich databases"""
    cmds = [
        "CREATE DATABASE memu_synapse;",
        "CREATE DATABASE immich;"
    ]
    for sql in cmds:
        run_cmd(['docker', 'exec', 'memu_postgres', 'psql', '-U', 'memu_user', '-d', 'postgres', '-c', sql], check=False)


def wait_for_synapse(max_wait=60):
    """Wait for Synapse to be healthy"""
    start = time.time()
    while time.time() - start < max_wait:
        try:
            r = requests.get('http://localhost:8008/_matrix/client/versions', timeout=2)
            if r.status_code == 200:
                return True
        except:
            pass
        time.sleep(2)
    return False


def create_matrix_user_with_retry(username, password, is_admin=False, retries=5):
    """Create matrix user with retries"""
    for i in range(retries):
        try:
            cmd = [
                'docker', 'compose', 'exec', '-T', 'synapse',
                'register_new_matrix_user',
                '-u', username,
                '-p', password,
                '-c', '/data/homeserver.yaml',
                'http://localhost:8008'
            ]
            if is_admin:
                cmd.insert(6, '--admin')
            else:
                cmd.insert(6, '--no-admin')
            
            res = run_cmd(cmd, check=False)
            if res.returncode == 0 or "already in use" in res.stderr:
                return True
        except:
            pass
        time.sleep(3)
    return False


def get_user_token_with_retry(username, password, retries=5):
    """Get access token for a user"""
    for i in range(retries):
        try:
            r = requests.post('http://localhost:8008/_matrix/client/v3/login', json={
                "type": "m.login.password",
                "identifier": {"type": "m.id.user", "user": username},
                "password": password
            })
            if r.status_code == 200:
                return r.json().get('access_token')
        except:
            pass
        time.sleep(3)
    return None


def configure_tailscale(domain, server_ip):
    """Configure Tailscale settings"""
    # 1. Advertise routes if needed (skip for now, default is usually fine for simple setup)
    # 2. Get cert is handled by Tailscale automatically for the domain
    pass

if __name__ == '__main__':
    # Initialize DB
    init_db()
    
    # Run server
    port = int(os.environ.get('WIZARD_PORT', 8888))
    print(f"Starting Memu Bootstrap Server on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)
