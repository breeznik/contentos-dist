"""Archive command - Move old kits to archive for cleaner context."""
import sys
import shutil
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.context import context_manager
from core.ledger import list_production_kits

# Archive threshold (days since published)
ARCHIVE_THRESHOLD_DAYS = 30

def cmd_list(args):
    """List kits eligible for archiving."""
    ctx = context_manager.get_current_context()
    if not ctx:
        print("No active channel.")
        return
    
    kits = list_production_kits(ctx)
    archive_path = ctx.production_path / "archive"
    
    # Find old kits
    now = datetime.now()
    eligible = []
    
    for kit in kits:
        if kit.get('status') == 'published' and kit.get('published_at'):
            try:
                pub_date = datetime.fromisoformat(kit['published_at'].replace('Z', '+00:00'))
                age_days = (now - pub_date.replace(tzinfo=None)).days
                if age_days > ARCHIVE_THRESHOLD_DAYS:
                    eligible.append({**kit, 'age_days': age_days})
            except:
                pass
    
    if not eligible:
        print(f"No kits older than {ARCHIVE_THRESHOLD_DAYS} days.")
        print(f"All {len(kits)} kits are still in Active context.")
        return
    
    print(f"\nKits eligible for archiving (>{ARCHIVE_THRESHOLD_DAYS} days old):\n")
    print(f"{'ID':<5} {'Name':<30} {'Age (Days)':<10}")
    print("-" * 50)
    for kit in eligible:
        print(f"{kit['id']:<5} {kit['name']:<30} {kit['age_days']:<10}")
    
    print(f"\nTotal: {len(eligible)} kits")
    print(f"\nRun: contentos archive run --all  (to archive all)")
    print(f"Run: contentos archive run --kit <ID>  (to archive one)")

def cmd_run(args):
    """Archive kits to reduce active context."""
    ctx = context_manager.get_current_context()
    if not ctx:
        print("No active channel.")
        return
    
    archive_path = ctx.production_path / "archive"
    archive_path.mkdir(exist_ok=True)
    
    kits = list_production_kits(ctx)
    archived_count = 0
    
    # Filter by kit ID if specified
    if hasattr(args, 'kit_id') and args.kit_id:
        kits = [k for k in kits if k['id'] == args.kit_id]
    
    now = datetime.now()
    
    for kit in kits:
        if kit.get('status') != 'published':
            continue
        
        # Check age
        try:
            pub_date = datetime.fromisoformat(kit.get('published_at', '').replace('Z', '+00:00'))
            age_days = (now - pub_date.replace(tzinfo=None)).days
        except:
            age_days = 0
        
        if age_days <= ARCHIVE_THRESHOLD_DAYS and not (hasattr(args, 'force') and args.force):
            continue
        
        # Move to archive
        kit_folder = ctx.production_path / f"{kit['id']}_{kit['name']}"
        if kit_folder.exists():
            dest = archive_path / kit_folder.name
            shutil.move(str(kit_folder), str(dest))
            print(f"Archived: {kit['name']} ({age_days} days old)")
            archived_count += 1
    
    if archived_count == 0:
        print("No kits archived. Use --force to override age check.")
    else:
        print(f"\nArchived {archived_count} kits to {archive_path.relative_to(ctx.path)}")
        print("These kits are now out of Active context.")

def cmd_restore(args):
    """Restore an archived kit to active production."""
    ctx = context_manager.get_current_context()
    if not ctx:
        print("No active channel.")
        return
    
    archive_path = ctx.production_path / "archive"
    if not archive_path.exists():
        print("No archive folder found.")
        return
    
    # List archived kits
    if not hasattr(args, 'kit_id') or not args.kit_id:
        print("\nArchived Kits:\n")
        for kit_folder in archive_path.iterdir():
            if kit_folder.is_dir():
                print(f"  - {kit_folder.name}")
        print("\nRun: contentos archive restore --kit <FOLDER_NAME>")
        return
    
    # Restore specific kit
    target = archive_path / args.kit_id
    if not target.exists():
        print(f"Kit '{args.kit_id}' not found in archive.")
        return
    
    dest = ctx.production_path / target.name
    shutil.move(str(target), str(dest))
    print(f"Restored: {target.name} to active production.")

def run(args):
    """Entry point for archive command."""
    if args.archive_action == 'list':
        cmd_list(args)
    elif args.archive_action == 'run':
        cmd_run(args)
    elif args.archive_action == 'restore':
        cmd_restore(args)
    else:
        print("Usage: contentos archive {list|run|restore}")
