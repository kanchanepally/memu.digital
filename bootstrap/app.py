import os
import subprocess
from flask import Flask, render_template, request
import secrets

app = Flask(__name__)

# Path to your project root (Dynamic detection)
import os
import subprocess
from flask import Flask, render_template, request
import secrets

app = Flask(__name__)

# Path to your project root (Dynamic detection)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@app.route('/')
def welcome():
    return render_template('setup.html')

@app.route('/configure', methods=['POST'])
def configure():
    family_name = request.form.get('family_name')
    admin_password = request.form.get('password')
    cloudflare_token = request.form.get('cloudflare_token')
    
    if not family_name or not admin_password or not cloudflare_token:
        return "Missing information", 400

    # Clean the family name to be safe for URLs
    clean_slug = "".join(c for c in family_name if c.isalnum()).lower()
    domain = f"{clean_slug}.memu.digital"
    
    # Generate Secrets
    db_pass = secrets.token_urlsafe(20)
    bot_pass = secrets.token_urlsafe(20)
    # Admin password is provided by user
    
    # Create initial .env content
    env_content = f"""
MEMU_DOMAIN={domain}
DB_NAME=immich
DB_USER=memu_user
DB_PASSWORD={db_pass}
ENABLE_REGISTRATION=true
TZ=Europe/London
CLOUDFLARED_TOKEN={cloudflare_token}
UPLOAD_LOCATION=/mnt/immich-data
SERVER_NAME={domain}
AI_ENABLED=true
LOG_LEVEL=info
MATRIX_BOT_USERNAME=@memu_bot:{domain}
# Token will be added shortly
"""
    
    # Write .env
    with open(os.path.join(PROJECT_ROOT, '.env'), 'w') as f:
        f.write(env_content)

    # --- AUTOMATION START ---
    try:
        # 1. Start Synapse & DB
        subprocess.run(["docker", "compose", "up", "-d", "database", "synapse"], cwd=PROJECT_ROOT, check=True)
        
        # 2. Wait for Synapse
        import time
        import requests
        print("Waiting for Synapse...")
        for _ in range(30):
            try:
                if requests.get("http://localhost:8008/health").status_code == 200:
                    break
            except:
                pass
            time.sleep(2)
            
        # 3. Register Users & Get Tokens
        def get_token(user, password):
            # Register
            subprocess.run([
                "docker", "compose", "exec", "synapse", 
                "register_new_matrix_user", "-u", user, "-p", password, 
                "--admin", "-c", "/data/homeserver.yaml", "--no-user-interactive"
            ], cwd=PROJECT_ROOT) # Ignore errors if user exists
            
            # Login
            resp = requests.post("http://localhost:8008/_matrix/client/r0/login", json={
                "type": "m.login.password", "user": user, "password": password
            })
            return resp.json().get("access_token")

        # Register Admin
        admin_token = get_token("admin", admin_password)
        
        # Register Bot
        bot_token = get_token("memu_bot", bot_pass)
        
        if not bot_token:
            return "Failed to generate bot token", 500

        # 4. Update .env with Bot Token
        with open(os.path.join(PROJECT_ROOT, '.env'), 'a') as f:
            f.write(f"\nMATRIX_BOT_TOKEN={bot_token}\n")
            
    except Exception as e:
        return f"Setup failed: {str(e)}", 500
    # --- AUTOMATION END ---

    # Trigger the shell script to generate Nginx config and start production
    # We run this in a detached process so the web request can finish
    subprocess.Popen([os.path.join(PROJECT_ROOT, 'scripts', 'launch_production.sh'), clean_slug])
    
    return render_template('installing.html', domain=domain)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)