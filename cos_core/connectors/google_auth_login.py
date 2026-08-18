import json
import os
import sys
import urllib.parse
import urllib.request
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler

CREDS_PATH = os.path.expanduser("~/.gmail-mcp/credentials.json")
KEYS_PATH = os.path.expanduser("~/.gmail-mcp/gcp-oauth.keys.json")

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.readonly",
]

auth_code = None

class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        if "code" in params:
            auth_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h1>Authentication Successful!</h1><p>You can close this window now and return to terminal.</p>")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Authentication failed.")

    def log_message(self, format, *args):
        return  # Suppress default server logs

def run_read_only_auth():
    if not os.path.exists(KEYS_PATH):
        print(f"Error: {KEYS_PATH} not found. Please place gcp-oauth.keys.json there first.")
        sys.exit(1)

    with open(KEYS_PATH, "r") as f:
        keys_data = json.load(f)

    web_keys = keys_data.get("web", keys_data.get("installed", {}))
    client_id = web_keys.get("client_id")
    client_secret = web_keys.get("client_secret")
    redirect_uris = web_keys.get("redirect_uris", ["http://localhost:3000/oauth2callback"])
    redirect_uri = redirect_uris[0] if redirect_uris else "http://localhost:3000/oauth2callback"

    parsed_uri = urllib.parse.urlparse(redirect_uri)
    port = parsed_uri.port or 3000

    auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        + urllib.parse.urlencode({
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(SCOPES),
            "access_type": "offline",
            "prompt": "consent",
        })
    )

    print(f"\n========================================================")
    print(f"🔒 Starting Strictly READ-ONLY OAuth Authentication...")
    print(f"========================================================\n")
    print(f"Opening browser to authenticate with scopes:")
    for scope in SCOPES:
        print(f" - {scope}")
    print(f"\nIf browser doesn't open automatically, copy & paste this URL into your browser:\n{auth_url}\n")

    webbrowser.open(auth_url)

    server = HTTPServer(("localhost", port), OAuthHandler)
    while auth_code is None:
        server.handle_request()

    # Exchange code for tokens
    token_url = "https://oauth2.googleapis.com/token"
    token_data = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "code": auth_code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
    }).encode("utf-8")

    req = urllib.request.Request(token_url, data=token_data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req) as resp:
        tokens = json.loads(resp.read().decode("utf-8"))

    os.makedirs(os.path.dirname(CREDS_PATH), exist_ok=True)
    with open(CREDS_PATH, "w") as f:
        json.dump(tokens, f, indent=2)

    print("\n✅ READ-ONLY Authentication completed successfully!")
    print(f"Tokens saved to: {CREDS_PATH}\n")

if __name__ == "__main__":
    run_read_only_auth()
