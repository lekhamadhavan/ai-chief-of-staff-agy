# Complete Deployment & Setup Guide: AI Chief of Staff

> **Goal**: Complete step-by-step guide to set up and run the AI Chief of Staff system on any fresh computer (Windows, macOS, or Linux).

---

## 📋 Prerequisites

The system is 100% cross-platform and runs natively on **Windows** (PowerShell / Command Prompt / WSL), **macOS**, and **Linux**.

Before starting, ensure the target system has the following installed:

1. **Python**: `python` or `python3` (v3.10 or higher)
   - Windows: `python --version`
   - Linux/macOS: `python3 --version`
2. **Node.js & npx**: `node` (v18 or higher) and `npx`
   ```cmd
   node -v
   npx -v
   ```
3. **Git**: Installed
   ```cmd
   git --version
   ```
4. **Google Account**: Access to Google Cloud Console.
5. **Google Antigravity Runtime**: Installed on the system.

---

## 🚀 Step 1: Clone Repository & Install Dependencies

```bash
# 1. Clone the repository
git clone <repository-url> ai-chief-of-staff
cd ai-chief-of-staff

# 2. Install Python package in editable mode with dependencies
python3 -m pip install -e .
```

---

## ⚙️ Step 2: Initialize Starter Context & Data

Run the auto-scaffolding command to generate starter profile, goals, and task files:

```bash
python3 -m cos_core.orchestration.cli init
```

This creates the `cos-data/` directory with:
- `cos-data/profile.yaml` (Executive name, email, working hours)
- `cos-data/goals.yaml` (Active strategic goals)
- `cos-data/tasks.yaml` (Pending tasks & priority tiers)
- `cos-data/workflow_state.yaml` (Recency cursors)

> **Customize profile**: Edit `cos-data/profile.yaml` to update the user's name and email address.

---

## 🔑 Step 3: Set Up Google Cloud OAuth 2.0 Credentials

1. Go to **[Google Cloud Console](https://console.cloud.google.com)** and sign in.
2. **Create Project**:
   - Click the project dropdown → **New Project** → Name: `ai-chief-of-staff` → Click **Create**.
3. **Enable APIs**:
   - Go to **APIs & Services** → **Library**.
   - Search & Enable **Gmail API** ✅.
   - Search & Enable **Google Calendar API** ✅.
4. **Configure OAuth Consent Screen**:
   - Go to **APIs & Services** → **OAuth consent screen**.
   - Select **External** → Click **Create**.
   - Fill in App Name (`AI Chief of Staff`) and support email.
   - Under **Test Users** → Add the user's Gmail address (e.g. `user@gmail.com`).
   - Click **Save and Continue**.
5. **Create OAuth Client Credentials**:
   - Go to **APIs & Services** → **Credentials** → Click **+ Create Credentials** → **OAuth client ID**.
   - **Application type**: Select **"Web application"** *(CRITICAL: Do NOT select "Desktop app")*.
   - **Name**: `CoS Client`.
   - **Authorized redirect URIs**: Add:
     - `http://localhost:3000/oauth2callback`
     - `http://localhost:4000/oauth2callback`
   - Click **Create** → Click **Download JSON**.

---

## 🔐 Step 4: Install Credentials & Run One-Time Auth

### 1. Position Credentials File

**On Linux / macOS:**
```bash
mkdir -p ~/.gmail-mcp
mv ~/Downloads/client_secret_*.json ~/.gmail-mcp/gcp-oauth.keys.json
```

**On Windows (PowerShell):**
```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.gmail-mcp"
Move-Item "$env:USERPROFILE\Downloads\client_secret_*.json" "$env:USERPROFILE\.gmail-mcp\gcp-oauth.keys.json" -Force
```

---

### 2. Run OAuth Authentication

Choose one of the authentication options below:

#### Option A: Strictly Read-Only Auth (Recommended)
Requests **ONLY** `gmail.readonly` and `calendar.readonly` (no write, compose, or send permissions):

```bash
# Windows (PowerShell) or Linux/macOS
python -m cos_core.connectors.google_auth_login
```

#### Option B: standard MCP Auth Server
```bash
npx -y @gongrzhe/server-gmail-autoauth-mcp auth
```

**In your browser**:
1. Open the URL generated in the terminal (or complete browser sign-in).
2. Sign in with the authorized Google account.
3. If prompted with *"App isn't verified"*, click **Advanced** → **Go to AI Chief of Staff (unsafe)**.
4. Review requested permissions (`gmail.readonly` and `calendar.readonly`) and click **Allow**.
5. Terminal will output: **`Authentication completed successfully`**.
6. Token is saved to `~/.gmail-mcp/credentials.json` (or `%USERPROFILE%\.gmail-mcp\credentials.json` on Windows).

---

## 🛠️ Step 5: Configure Antigravity MCP Server (Optional)

Add the Gmail MCP server configuration to your Antigravity config file:

- **Linux / macOS**: `~/.gemini/config/mcp_config.json`
- **Windows**: `C:\Users\<YourUsername>\.gemini\config\mcp_config.json`

**To open and edit `mcp_config.json` in Windows PowerShell:**
```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.gemini\config"
notepad "$env:USERPROFILE\.gemini\config\mcp_config.json"
```

**JSON Content:**
```json
{
  "mcpServers": {
    "gmail": {
      "command": "npx",
      "args": ["-y", "@gongrzhe/server-gmail-autoauth-mcp"],
      "env": {
        "GMAIL_CREDENTIALS_PATH": "C:\\Users\\<YourUsername>\\.gmail-mcp\\credentials.json"
      }
    }
  }
}
```
*(Note for Windows: Use double backslashes `\\` in JSON paths).*


---

## 🎯 Step 6: Verify & Run Workflows

You are now ready to run executive workflows!

### Option A: Using Antigravity Slash Commands (Recommended)
Type any of these directly into the prompt box:
- `/morning-briefing` → Generates executive daily briefing with live Gmail inbox & calendar items
- `/inbox-triage` → Triages unread emails into Tier 1/2/3 and drafts responses
- `/meeting-prep` → Compiles strategic meeting preparation briefs
- `/weekly-briefing` → Generates weekly goal-calendar alignment review
- `/relationship-audit` → Checks contact interaction recency & staleness

### Option B: Using Terminal CLI
```bash
# Linux/macOS
python3 -m cos_core.orchestration.cli morning-briefing

# Windows (PowerShell)
python -m cos_core.orchestration.cli morning-briefing
```

---

## ❓ Troubleshooting

| Issue | Solution |
|:---|:---|
| `ModuleNotFoundError: No module named 'pydantic'` | Run `python -m pip install -e .` inside project root |
| `npx : cannot be loaded... execution policy` (Windows) | Run `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` in PowerShell |
| `npx : command not found` | Install Node.js via `winget install OpenJS.NodeJS.LTS` then restart PowerShell |
| `HTTP Error 401: Unauthorized` | Re-run `python -m cos_core.connectors.google_auth_login` to refresh credentials |
| Redirect URI Mismatch | Ensure `http://localhost:3000/oauth2callback` is exact in Google Cloud Console |
| No live emails appearing | Ensure test user email in Google Cloud Consent Screen matches the logged-in email |

