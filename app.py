import os
from dotenv import load_dotenv
from flask import Flask, redirect, render_template_string
from authlib.integrations.flask_client import OAuth
import secrets

# Load environment variables
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID")
REDIRECT_URI = os.getenv("REDIRECT_URI")
AUTHORITY = os.getenv('AUTHORITY')

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

oauth = OAuth(app)
oauth.register(
    name='entra',
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    server_metadata_url=f'https://login.microsoftonline.com/{TENANT_ID}/v2.0/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid profile email'}
)

@app.route('/')
def index():
    # Landing page with a login button
    return render_template_string("""
        <html>
        <head><title>SAML Test App</title></head>
        <body style="font-family: Arial; text-align: center; margin-top: 50px;">
            <h1>Welcome to the SAML Test App</h1>
            <p>Click below to authenticate via Entra ID:</p>
            <a href="/login/">
  	            <button>Click me</button>
            </a>
        </body>
        </html>
    """)

@app.route('/login')
def login():
    once = secrets.token_urlsafe(16)
    session['nonce'] = nonce
    return oauth.entra.authorize_redirect(redirect_uri=REDIRECT_URI)

@app.route('/callback')
def callback():
    token = oauth.entra.authorize_access_token() 
    nonce = session.get('nonce')
    user_info = oauth.entra.parse_id_token(token, nonce=nonce)
    return f"Hello, {user_info.get('name', 'User')}"



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
