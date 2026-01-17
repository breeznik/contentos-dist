"""Setup command - Initialize ContentOS for new users with guided onboarding."""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

SETUP_GUIDE = """
==================================================
CONTENTOS SETUP - FULL ONBOARDING
==================================================

ContentOS is a YouTube content production CLI.
This setup will guide you through everything needed.

REQUIREMENTS
------------
1. Python 3.10+ (you have this if you're running this)
2. Google Cloud Project (for YouTube API - optional)
3. Ollama (for AI features - optional)

"""

GOOGLE_SETUP_GUIDE = """
--------------------------------------------------
YOUTUBE API SETUP (Required for analytics)
--------------------------------------------------

If you want to use YouTube analytics features (sync, retention, scout),
you need to set up Google Cloud credentials:

STEP 1: Create Google Cloud Project
  1. Go to: https://console.cloud.google.com/
  2. Click "New Project"
  3. Name it "ContentOS" (or anything)
  4. Click "Create"

STEP 2: Enable APIs
  1. Go to "APIs & Services" > "Enable APIs"
  2. Search and enable:
     - YouTube Data API v3
     - YouTube Analytics API
     - YouTube Reporting API

STEP 3: Create OAuth Credentials
  1. Go to "APIs & Services" > "Credentials"
  2. Click "Create Credentials" > "OAuth client ID"
  3. Application type: "Desktop app"
  4. Name: "ContentOS"
  5. Click "Create"
  6. Click "Download JSON"
  7. Rename to: client_secret.json
  8. Move to: credentials/client_secret.json

STEP 4: Configure OAuth Consent Screen
  1. Go to "OAuth consent screen"
  2. User type: "External"
  3. Fill in app name: "ContentOS"
  4. Add your email to "Test users"
  5. Save

STEP 5: Authenticate
  Run: python contentos.py sync
  A browser window will open for authentication.

--------------------------------------------------
"""

OLLAMA_GUIDE = """
--------------------------------------------------
AI FEATURES SETUP (Optional)
--------------------------------------------------

ContentOS uses Ollama for AI features (scout, scan, suggestions).

STEP 1: Install Ollama
  Download from: https://ollama.ai/
  
STEP 2: Pull a model
  ollama pull deepseek-r1:8b
  
STEP 3: Enable in ContentOS
  python contentos.py config enable llm_swarm

--------------------------------------------------
"""

def check_credentials():
    """Check if credentials are set up."""
    base_path = Path(__file__).parent.parent
    creds_path = base_path / "credentials" / "client_secret.json"
    return creds_path.exists()

def run(args):
    """Initialize ContentOS for first-time setup."""
    print(SETUP_GUIDE)
    
    base_path = Path(__file__).parent.parent
    
    # 1. Create directories
    print("[STEP 1] Creating directories...")
    
    dirs_to_create = [
        base_path / "channels",
        base_path / ".contentos",
        base_path / "credentials"
    ]
    
    for dir_path in dirs_to_create:
        if not dir_path.exists():
            dir_path.mkdir(parents=True)
            print(f"  [OK] Created {dir_path.name}/")
        else:
            print(f"  [OK] {dir_path.name}/ exists")
    
    # 2. Create config files
    print("\n[STEP 2] Creating config files...")
    
    config_path = base_path / ".contentos"
    
    # config.json
    config_file = config_path / "config.json"
    if not config_file.exists():
        with open(config_file, 'w') as f:
            json.dump({"active_channel": None, "version": "4.0"}, f, indent=2)
        print("  [OK] Created config.json")
    else:
        print("  [OK] config.json exists")
    
    # settings.json
    settings_file = config_path / "settings.json"
    if not settings_file.exists():
        with open(settings_file, 'w') as f:
            json.dump({"features": {"llm_swarm": False}}, f, indent=2)
        print("  [OK] Created settings.json")
    else:
        print("  [OK] settings.json exists")
    
    # channels.json
    channels_file = config_path / "channels.json"
    if not channels_file.exists():
        with open(channels_file, 'w') as f:
            json.dump({"channels": {}}, f, indent=2)
        print("  [OK] Created channels.json")
    else:
        print("  [OK] channels.json exists")
    
    # 3. Check credentials
    print("\n[STEP 3] Checking credentials...")
    if check_credentials():
        print("  [OK] client_secret.json found")
    else:
        print("  [!] client_secret.json NOT FOUND")
        print("      YouTube features will not work until you set this up.")
        print("      See guide below for setup instructions.")
    
    # 4. Show next steps
    print("\n" + "=" * 50)
    print("BASIC SETUP COMPLETE!")
    print("=" * 50)
    
    print("""
QUICK START (No YouTube API needed)
------------------------------------
1. Create a channel:
   python contentos.py channel create mychannel

2. Initialize brain:
   python contentos.py brain init

3. Create your first kit:
   python contentos.py kit create "my_video" --theme loop
""")
    
    # 5. Show credential guide if needed
    if not check_credentials():
        print(GOOGLE_SETUP_GUIDE)
    
    # 6. Show Ollama guide
    print(OLLAMA_GUIDE)
    
    print("=" * 50)
    print("Run 'python contentos.py health' to check system status")
    print("=" * 50)
