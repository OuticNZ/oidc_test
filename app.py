import os
from dotenv import load_dotenv
from flask import Flask, redirect, render_template_string, session, request
import msal
import secrets

# Load environment variables
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID")
REDIRECT_URI = os.getenv("REDIRECT_URI")
AUTHORITY = os.getenv('AUTHORITY')
SCOPE = os.getenv("SCOPE").split()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

def build_msal_app(cache=None):
    return msal.ConfidentialClientApplication(
        CLIENT_ID, authority=AUTHORITY,
        client_credential=CLIENT_SECRET,
        token_cache=cache
    )

@app.route('/')
def index():
    # Landing page with a login button
    return render_template_string("""
        <html>
        <head><title>OIDC Test App</title></head>
        <body style="font-family: Arial; text-align: center; margin-top: 50px;">
            <h1>Welcome to the SAML Test App</h1>
            <p>Click below to authenticate via Entra ID:</p>
            <a href="/login/">
  	            <button>Click me</button>
            </a>
        </body>
        </html>
    """)


@app.route("/login")
def login():
    msal_app = build_msal_app()
    auth_url = msal_app.get_authorization_request_url(
        scopes=SCOPE,
        redirect_uri=REDIRECT_URI
    )
    return redirect(auth_url)


@app.route("/callback")
def authorized():
    code = request.args.get('code')
    if not code:
        return "No code returned from Entra ID", 400

    msal_app = build_msal_app()
    result = msal_app.acquire_token_by_authorization_code(
        code,
        scopes=SCOPE,
        redirect_uri=REDIRECT_URI
    )
 
    if "id_token_claims" in result:
        session["user"] = result["id_token_claims"]
        return f"Hello, {session['user'].get('name', 'User')}"

    return f"Error: {result.get('error_description')}", 400


@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/logout"
        f"?post_logout_redirect_uri=http://localhost:5000"
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
