import os
import requests
from flask import Flask, redirect, request, session, url_for, render_template_string
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
TENANT_ID = os.getenv('TENANT_ID')
REDIRECT_URI = os.getenv('REDIRECT_URI')
AUTHORITY = os.getenv('AUTHORITY')

AUTH_ENDPOINT = f"{AUTHORITY}/oauth2/v2.0/authorize"
TOKEN_ENDPOINT = f"{AUTHORITY}/oauth2/v2.0/token"
USERINFO_ENDPOINT = "https://graph.microsoft.com/oidc/userinfo"

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

@app.route('/login/')
def login():
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "response_mode": "query",
        "scope": "openid profile email",
        "state": "12345"
    }
    return redirect(f"{AUTH_ENDPOINT}?{urlencode(params)}")


@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return "Error: No code returned"

    # Exchange code for tokens
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }
    token_response = requests.post(TOKEN_ENDPOINT, data=data).json()
    access_token = token_response.get("access_token")
    id_token = token_response.get("id_token")

    # Decode ID Token to inspect claims (without signature verification for testing)
    import jwt
    claims = jwt.decode(id_token, options={"verify_signature": False})

    # Build HTML table of claims
    html = """
    <h1>OIDC Login Successful</h1>
    <h2>ID Token Claims:</h2>
    <table border="1" cellpadding="8" style="border-collapse: collapse;">
        <tr><th>Claim</th><th>Value</th></tr>
    """
    for k, v in claims.items():
        html += f"<tr><td>{k}</td><td>{v}</td></tr>"
    html += "</table>"

    # Optionally fetch UserInfo from Microsoft Graph
    headers = {"Authorization": f"Bearer {access_token}"}
    userinfo = requests.get(USERINFO_ENDPOINT, headers=headers).json()
    html += "<h2>UserInfo:</h2><pre>{}</pre>".format(userinfo)

    html += "<br>/Back to Home</a>"
    return html


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
