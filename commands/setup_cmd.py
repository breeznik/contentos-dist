"""Setup command - Initialize ContentOS for new users."""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

def run(args):
    """Initialize ContentOS for first-time setup."""
    print("\n" + "=" * 50)
    print("CONTENTOS SETUP")
    print("=" * 50)
    
    base_path = Path(__file__).parent.parent
    
    # 1. Create channels directory
    channels_path = base_path / "channels"
    if not channels_path.exists():
        channels_path.mkdir()
        print("[OK] Created channels/ directory")
    else:
        print("[OK] channels/ directory exists")
    
    # 2. Create .contentos directory
    config_path = base_path / ".contentos"
    if not config_path.exists():
        config_path.mkdir()
        print("[OK] Created .contentos/ directory")
    else:
        print("[OK] .contentos/ directory exists")
    
    # 3. Create default config
    config_file = config_path / "config.json"
    if not config_file.exists():
        import json
        default_config = {
            "active_channel": None,
            "version": "4.0"
        }
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        print("[OK] Created default config.json")
    else:
        print("[OK] config.json exists")
    
    # 4. Create settings
    settings_file = config_path / "settings.json"
    if not settings_file.exists():
        import json
        default_settings = {
            "features": {
                "llm_swarm": False
            }
        }
        with open(settings_file, 'w') as f:
            json.dump(default_settings, f, indent=2)
        print("[OK] Created default settings.json")
    else:
        print("[OK] settings.json exists")
    
    # 5. Create channels.json
    channels_file = config_path / "channels.json"
    if not channels_file.exists():
        import json
        with open(channels_file, 'w') as f:
            json.dump({"channels": {}}, f, indent=2)
        print("[OK] Created channels.json")
    else:
        print("[OK] channels.json exists")
    
    # 6. Create credentials directory
    creds_path = base_path / "credentials"
    if not creds_path.exists():
        creds_path.mkdir()
        print("[OK] Created credentials/ directory")
    else:
        print("[OK] credentials/ directory exists")
    
    print("\n" + "=" * 50)
    print("SETUP COMPLETE!")
    print("=" * 50)
    print("\nNext steps:")
    print("  1. Create a channel:")
    print("     python contentos.py channel create mychannel")
    print("")
    print("  2. Initialize brain:")
    print("     python contentos.py brain init")
    print("")
    print("  3. Create your first kit:")
    print("     python contentos.py kit create \"my_video\" --theme loop")
    print("")
    print("  4. (Optional) Enable AI features:")
    print("     python contentos.py config enable llm_swarm")
    print("     # Requires Ollama running locally")
    print("=" * 50)
