import os
import subprocess
from flask import Flask, render_template, request
import secrets

app = Flask(__name__)

# Path to your project root
PROJECT_ROOT = "/home/hareesh/memu-os"

@app.route('/')
def welcome():
    return render_template('setup.html')

@app.route('/configure', methods=['POST'])
def configure():
    family_name = request.form.get('family_name')
    password = request.form.get('password')
    
    if not family_name or not password:
        return "Missing information", 400

    # Clean the family name to be safe for URLs
    clean_slug = "".join(c for c in family_name if c.isalnum()).lower()
    domain = f"{clean_slug}.memu.digital"
    
    # Generate Secrets
    db_pass = secrets.token_urlsafe(16)
    synapse_token = secrets.token_hex(32)
    
    # Create .env content
    env_content = f"""
MEMU_DOMAIN={domain}
DB_NAME=memu_core
DB_USER=memu_user
DB_PASSWORD={db_pass}
SYNAPSE_ADMIN_TOKEN={synapse_token}
ENABLE_REGISTRATION=true
TZ=Europe/London
"""
    
    # Write .env
    with open(os.path.join(PROJECT_ROOT, '.env'), 'w') as f:
        f.write(env_content)

    # Trigger the shell script to generate Nginx config and start production
    # We run this in a detached process so the web request can finish
    subprocess.Popen([os.path.join(PROJECT_ROOT, 'scripts', 'launch_production.sh'), clean_slug])
    
    return render_template('installing.html', domain=domain)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)