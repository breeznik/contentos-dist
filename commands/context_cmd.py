"""Context command - Display and manage AI context for channels."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.context import context_manager
from core.ledger import list_production_kits

def cmd_show(args):
    """Show the current AI context window usage."""
    ctx = context_manager.get_current_context()
    if not ctx:
        print("No active channel.")
        return
    
    # Count active vs archived kits
    production_path = ctx.production_path
    archive_path = production_path / "archive"
    
    active_kits = list_production_kits(ctx)
    archived_count = 0
    if archive_path.exists():
        archived_count = len([f for f in archive_path.iterdir() if f.is_dir()])
    
    # Estimate token usage (rough: 1KB = ~250 tokens)
    active_size_kb = 0
    archived_size_kb = 0
    
    for kit in active_kits:
        kit_path = production_path / f"{kit['id']}_{kit['name']}"
        if kit_path.exists():
            for f in kit_path.glob('*'):
                if f.is_file():
                    active_size_kb += f.stat().st_size / 1024
    
    if archive_path.exists():
        for kit_folder in archive_path.iterdir():
            if kit_folder.is_dir():
                for f in kit_folder.glob('*'):
                    if f.is_file():
                        archived_size_kb += f.stat().st_size / 1024
    
    active_tokens = int(active_size_kb * 250)
    archived_tokens = int(archived_size_kb * 250)
    
    print(f"\nCONTEXT REPORT: {ctx.name}")
    print("=" * 40)
    print(f"Active Kits:    {len(active_kits)}")
    print(f"Archived Kits:  {archived_count}")
    print("-" * 40)
    print(f"Active Size:    {active_size_kb:.1f} KB (~{active_tokens:,} tokens)")
    print(f"Archived Size:  {archived_size_kb:.1f} KB (~{archived_tokens:,} tokens)")
    print(f"Total Saved:    {archived_tokens:,} tokens from context window")
    print("=" * 40)
    
    if active_tokens > 50000:
        print("\n[!] Warning: Active context is large.")
        print("    Consider archiving old kits: contentos archive list")

def cmd_optimize(args):
    """Suggest optimizations to reduce context size."""
    ctx = context_manager.get_current_context()
    if not ctx:
        print("No active channel.")
        return
    
    print(f"\nOPTIMIZATION SUGGESTIONS: {ctx.name}")
    print("=" * 40)
    
    # Check for large files
    production_path = ctx.production_path
    large_files = []
    
    for kit_folder in production_path.iterdir():
        if kit_folder.is_dir() and kit_folder.name != 'archive':
            for f in kit_folder.glob('*'):
                if f.is_file() and f.stat().st_size > 10 * 1024:  # > 10KB
                    large_files.append((f.name, f.stat().st_size / 1024, kit_folder.name))
    
    if large_files:
        print(f"\n[!] Large Files (>10KB):")
        for name, size_kb, kit in large_files[:5]:
            print(f"    - {kit}/{name}: {size_kb:.1f} KB")
        print(f"\n    Consider moving images/videos to external storage.")
    else:
        print("\n[OK] No unusually large files found.")
    
    # Check for old kits
    kits = list_production_kits(ctx)
    published = [k for k in kits if k.get('status') == 'published']
    
    if len(published) > 10:
        print(f"\n[!] {len(published)} published kits in active context.")
        print("    Run: contentos archive list  (to see archiving options)")
    else:
        print(f"\n[OK] {len(published)} published kits (threshold: 10)")
    
    print("\n" + "=" * 40)

def run(args):
    """Entry point for context command."""
    if args.context_action == 'show':
        cmd_show(args)
    elif args.context_action == 'optimize':
        cmd_optimize(args)
    else:
        print("Usage: contentos context {show|optimize}")
