import json
import os
import time
import urllib.request
import urllib.parse
from typing import Optional, Dict, Any

CREDS_PATH = os.path.expanduser("~/.gmail-mcp/credentials.json")
KEYS_PATH = os.path.expanduser("~/.gmail-mcp/gcp-oauth.keys.json")

def get_valid_access_token() -> Optional[str]:
    """
    Loads OAuth credentials from ~/.gmail-mcp/credentials.json,
    refreshes access_token using refresh_token if expired, and returns a valid access token.
    Returns None if credentials are missing or invalid.
    """
    if not os.path.exists(CREDS_PATH):
        return None

    try:
        with open(CREDS_PATH, "r") as f:
            creds = json.load(f)
    except Exception:
        return None

    access_token = creds.get("access_token")
    expiry_date = creds.get("expiry_date", 0)  # Epoch ms
    now_ms = time.time() * 1000

    # Refresh if expired or expiring within 60 seconds
    if not access_token or (expiry_date and now_ms >= (expiry_date - 60000)):
        new_token = refresh_access_token(creds)
        if new_token:
            return new_token

    return access_token

def refresh_access_token(creds: Dict[str, Any]) -> Optional[str]:
    """Refreshes access token using stored refresh token."""
    refresh_token = creds.get("refresh_token")
    if not refresh_token or not os.path.exists(KEYS_PATH):
        return creds.get("access_token")

    try:
        with open(KEYS_PATH, "r") as f:
            keys_data = json.load(f)
        
        web_keys = keys_data.get("web", keys_data.get("installed", {}))
        client_id = web_keys.get("client_id")
        client_secret = web_keys.get("client_secret")

        if not client_id or not client_secret:
            return creds.get("access_token")

        data = urllib.parse.urlencode({
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://oauth2.googleapis.com/token",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        with urllib.request.urlopen(req, timeout=10) as resp:
            token_resp = json.loads(resp.read().decode("utf-8"))
            new_access_token = token_resp.get("access_token")
            expires_in = token_resp.get("expires_in", 3600)

            if new_access_token:
                creds["access_token"] = new_access_token
                creds["expiry_date"] = int((time.time() + expires_in) * 1000)
                try:
                    with open(CREDS_PATH, "w") as f:
                        json.dump(creds, f, indent=2)
                except Exception:
                    pass
                return new_access_token
    except Exception as e:
        print(f"[GoogleAuth] Token refresh error: {e}")

    return creds.get("access_token")
