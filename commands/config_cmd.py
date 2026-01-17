"""Config command - Manage system settings and feature flags."""
import sys
from pathlib import Path
from core.context import context_manager
from core.config import save_global_config

def run(args):
    """Main entry for config command."""
    if args.config_action == 'show':
        show_config()
    elif args.config_action in ['enable', 'disable']:
        toggle_feature(args.feature_name, enable=(args.config_action == 'enable'))
    else:
        print("❌ Unknown action.")

def show_config():
    """Display current global configuration."""
    cfg = context_manager.global_config
    print("\nContentOS Configuration")
    print("==========================")
    print(f"Version: {cfg.version}")
    print(f"Active Channel: {cfg.active_channel}")
    print(f"Auto-Sync: {cfg.auto_sync_on_publish}")
    
    print("\nModular Features:")
    features = cfg.features.__dict__
    for name, enabled in features.items():
        status = "[ON] " if enabled else "[OFF]"
        print(f"  - {name:<15} {status}")
    print("")

def toggle_feature(feature_name: str, enable: bool):
    """Enable or disable a system feature."""
    cfg = context_manager.global_config
    
    if not hasattr(cfg.features, feature_name):
        print(f"Unknown feature: '{feature_name}'")
        print("Available features:", ", ".join(cfg.features.__dict__.keys()))
        return

    # Update state
    setattr(cfg.features, feature_name, enable)
    save_global_config(cfg)
    
    action = "Enabled" if enable else "Disabled"
    print(f"\n{action} feature: {feature_name}")
    print("Restart any running agents for changes to take effect.\n")
