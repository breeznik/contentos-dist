"""Channel management commands."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.context import context_manager
from core.config import save_channel_config, ChannelConfig, CHANNELS_DIR

def cmd_list(args):
    """List all registered channels."""
    channels = context_manager.list_channels()
    
    if not channels:
        print("[!] No channels registered.")
        print("   Run: contentos channel create <name>")
        return
    
    print("Registered Channels:\n")
    for ch in channels:
        active = " (Active)" if ch['is_active'] else ""
        handle = f" - {ch['handle']}" if ch['handle'] else ""
        print(f"  * {ch['name']}{handle}{active}")
    print()

def cmd_use(args):
    """Switch to a different channel."""
    channel_name = args.name
    
    if context_manager.use_channel(channel_name):
        ctx = context_manager.get_context(channel_name)
        display = ctx.config.name if ctx and ctx.config.name else channel_name
        handle = f" ({ctx.config.handle})" if ctx and ctx.config.handle else ""
        print(f"[OK] Active channel: {display}{handle}")
    else:
        print(f"[!] Channel '{channel_name}' not found.")
        print(f"   Available: {', '.join([ch['name'] for ch in context_manager.list_channels()])}")

def cmd_create(args):
    """Create a new channel."""
    channel_name = args.name.lower().replace(' ', '_')
    channel_path = CHANNELS_DIR / channel_name
    
    if channel_path.exists():
        print(f"[!] Channel '{channel_name}' already exists.")
        return
    
    # Create directory structure
    (channel_path / 'analytics').mkdir(parents=True)
    (channel_path / 'production').mkdir(parents=True)
    (channel_path / 'strategy').mkdir(parents=True)
    
    # Create channel config
    config = ChannelConfig(
        name=args.name.replace('_', ' ').title(),
        handle=args.handle if hasattr(args, 'handle') and args.handle else '',
        themes=['loop', 'cinematic', 'voxel']
    )
    save_channel_config(channel_name, config)
    
    print(f"[OK] Created channel: {channel_name}")
    print(f"   path: {channel_path}")
    print(f"   |-- analytics/")
    print(f"   |-- production/")
    print(f"   |-- strategy/")
    print(f"\n[!] Next: Copy client_secrets.json to D:/projects/personal/content/credentials/")
    print(f"    (This one file works for ALL channels now)")

def cmd_status(args):
    """Show active channel status."""
    ctx = context_manager.get_current_context()
    
    if not ctx:
        print("[!] No active channel.")
        return
    
    from core.ledger import list_production_kits
    
    kits = list_production_kits(ctx)
    ready_kits = len([k for k in kits if 'Pending' in k['status']])
    
    print(f"\nACTIVE CHANNEL STATUS")
    print("=" * 40)
    print(f"Name:    {ctx.config.name}")
    print(f"Handle:  {ctx.config.handle or 'Not set'}")
    print(f"Path:    {ctx.path}")
    print(f"Themes:  {', '.join(ctx.config.themes)}")
    print(f"Kits:    {len(kits)} total ({ready_kits} pending upload)")
    
    # Growth Stats
    from core.growth import get_next_slot
    print("-" * 40)
    print(f"Next Slot: {get_next_slot()}")
    print("=" * 40)
    
    from core.ui import print_ai_hint
    print_ai_hint()

def run(args):
    """Main entry point for channel command."""
    if args.channel_action == 'list':
        cmd_list(args)
    elif args.channel_action == 'use':
        cmd_use(args)
    elif args.channel_action == 'create':
        cmd_create(args)
    elif args.channel_action == 'status':
        cmd_status(args)
    else:
        print("Usage: contentos channel {list|use|create|status}")
