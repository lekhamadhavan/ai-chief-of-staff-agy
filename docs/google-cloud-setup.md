# Google Cloud Console Setup Guide
## AI Chief of Staff — Gmail + Google Calendar MCP Integration

> **Account**: lekhatestml@gmail.com  
> **Goal**: Enable live Gmail + Calendar data in your morning briefing via MCP

---

## Overview

```
Step 1 → Create / Select Project
Step 2 → Enable Gmail API
Step 3 → Enable Google Calendar API
Step 4 → Configure OAuth Consent Screen + Scopes
Step 5 → Add Test User
Step 6 → Create OAuth 2.0 Credential (Web Application type)
Step 7 → Add Redirect URIs
Step 8 → Download credentials.json → install to ~/.gmail-mcp/
Step 9 → Run one-time auth in terminal
```

---

## Step 1 — Create or Select a Project

1. Go to → **https://console.cloud.google.com**
2. Sign in with **lekhatestml@gmail.com**
3. Click the **project dropdown** at the top left (next to "Google Cloud" logo)
4. Click **"New Project"**
   - **Project name**: `ai-chief-of-staff`
   - Click **Create**
5. Wait ~10 seconds, then select the new project from the dropdown

---

## Step 2 — Enable Gmail API

1. Left sidebar → **"APIs & Services"** → **"Library"**
2. Search: `Gmail API`
3. Click **"Gmail API"** → Click **"Enable"** ✅

---

## Step 3 — Enable Google Calendar API

1. Left sidebar → **"APIs & Services"** → **"Library"**
2. Search: `Google Calendar API`
3. Click **"Google Calendar API"** → Click **"Enable"** ✅

---

## Step 4 — Configure OAuth Consent Screen

1. Left sidebar → **"APIs & Services"** → **"OAuth consent screen"**
2. Select **"External"** → Click **Create**
3. Fill in **App Information**:

   | Field | Value |
   |:------|:------|
   | App name | `AI Chief of Staff` |
   | User support email | `lekhatestml@gmail.com` |
   | Developer contact email | `lekhatestml@gmail.com` |

4. Click **"Save and Continue"**

5. **Test Users page** → Go to Audience **"+ Add Users"**
   - Add: `lekhatestml@gmail.com`
   - Click **"Add"** → **"Save and Continue"**

6. **Summary page** → Click **"Back to Dashboard"** ✅


---

## Step 6 — Create OAuth 2.0 Credentials

> **IMPORTANT**: You MUST select **"Web application"** — NOT "Desktop app".
> Desktop app hides the redirect URI field, which is required for the MCP auth flow.

1. Left sidebar → **"APIs & Services"** → **"Credentials"**
2. Click **"+ Create Credentials"** → **"OAuth client ID"**
3. **Application type**: Select **"Web application"** ← Critical
4. **Name**: `CoS MCP Client`
5. Do NOT click Create yet — continue to Step 7 first

---

## Step 7 — Add Redirect URIs (on the same Create page)

After selecting "Web application" in Step 6, you will now see the **"Authorized redirect URIs"** section on the same page.

1. Under **"Authorized redirect URIs"** → click **"+ ADD URI"**
2. Add:
   ```
   http://localhost:3000/oauth2callback
   ```
3. Click **"+ ADD URI"** again → add:
   ```
   http://localhost:4000/oauth2callback
   ```
4. Now click **"Create"** ✅

A popup appears showing your Client ID and Client Secret → click **"Download JSON"**

---

## Step 8 — Install Credentials File

Move the downloaded file to the required location:

```bash
# Create the Gmail MCP credentials directory
mkdir -p ~/.gmail-mcp

# Move downloaded file (adjust filename if different)
mv ~/Downloads/client_secret_*.json ~/.gmail-mcp/gcp-oauth.keys.json

# Verify
ls ~/.gmail-mcp/
# Should show: gcp-oauth.keys.json
```

---

## Step 9 — Run One-Time Authorization (Gmail + Calendar)

> **Note**: This single auth flow grants readonly access to **both** Gmail and Google Calendar.

```bash
cd /home/lekha/Documents/ai-chief-of-staff-agy
npx -y @gongrzhe/server-gmail-autoauth-mcp auth
```

**What happens:**
1. A URL appears in the terminal — open it in your browser
2. Sign in with `lekhatestml@gmail.com`
3. If you see **"This app isn't verified"** → click **"Continue"**
4. You will see **two permissions** requested:
   - ✅ **View your email messages and settings** (Gmail readonly)
   - ✅ **View your calendars** (Calendar readonly)
5. Click **Allow**
6. Terminal prints: **Authentication successful!** ✅
7. Token saved to `~/.gmail-mcp/credentials.json` (covers both Gmail + Calendar)

---

## Final Checklist

| # | Task | Done? |
|:--|:-----|:-----:|
| 1 | Created project `ai-chief-of-staff` | ☐ |
| 2 | Gmail API enabled | ☐ |
| 3 | Google Calendar API enabled | ☐ |
| 4 | OAuth Consent Screen configured (External) | ☐ |
| 5 | Added `lekhatestml@gmail.com` as test user | ☐ |
| 6 | Created OAuth client as **Web application** type | ☐ |
| 7 | Added redirect URI: `http://localhost:3000/oauth2callback` | ☐ |
| 8 | Added redirect URI: `http://localhost:4000/oauth2callback` | ☐ |
| 9 | Downloaded JSON → moved to `~/.gmail-mcp/gcp-oauth.keys.json` | ☐ |
| 10 | Ran auth → Authorized Gmail + Calendar (readonly) | ☐ |

---

## After Setup — What Changes in Your Briefing

Once authorized, your `/morning-briefing` will show:

- **📅 Today's Schedule** — Real events from Google Calendar
- **✉️ Urgent Inbox Items** — Real unread emails, triaged Tier 1/2/3

> **Next step after completing this**: Tell me and I'll wire the live MCP connectors into the CoS briefing service so real data flows automatically.
