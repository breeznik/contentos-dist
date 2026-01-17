"""Asset management commands - Place generated images into kits."""
import sys
import os
import shutil
from pathlib import Path
from typing import Optional, List

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.context import context_manager

def get_artifact_dir() -> Path:
    """
    Returns the artifact directory for AI-generated images.
    
    Checks in order:
    1. CONTENTOS_ARTIFACT_DIR environment variable
    2. Default Gemini Antigravity path
    """
    env_path = os.environ.get('CONTENTOS_ARTIFACT_DIR')
    if env_path:
        return Path(env_path)
    return Path.home() / ".gemini" / "antigravity" / "brain"

def find_latest_image(name_contains: str) -> Optional[Path]:
    """Finds the most recent image matching the name in any brain folder."""
    artifact_dir = get_artifact_dir()
    
    if not artifact_dir.exists():
        return None
    
    matches: List[Path] = []
    for brain_folder in artifact_dir.iterdir():
        if brain_folder.is_dir():
            for f in brain_folder.glob(f"*{name_contains}*.png"):
                matches.append(f)
    
    if not matches:
        return None
    
    # Return most recently modified
    return max(matches, key=lambda p: p.stat().st_mtime)

def cmd_place(args):
    """Place an asset into a kit's production folder."""
    ctx = context_manager.get_current_context()
    if not ctx:
        print("❌ No active channel.")
        return
    
    kit_id = args.kit
    asset_name = args.name
    slot = args.slot  # forward_start, forward_end, reverse_start, reverse_end
    
    # Find kit
    kit_path = None
    for item in ctx.production_path.iterdir():
        if item.is_dir() and item.name.startswith(f"{kit_id}_"):
            kit_path = item
            break
    
    if not kit_path:
        print(f"❌ Kit {kit_id} not found.")
        return
    
    # Find source image
    source = find_latest_image(asset_name)
    if not source:
        # Try as absolute path
        source = Path(asset_name)
        if not source.exists():
            print(f"❌ Asset '{asset_name}' not found.")
            return
    
    import yaml
    from core.templates import FORMULAS

    # Read kit formula
    kit_yaml_path = kit_path / 'kit.yaml'
    formula_name = 'stitch_2clip'
    
    if kit_yaml_path.exists():
        with open(kit_yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
            formula_name = data.get('ingredients', {}).get('formula', 'stitch_2clip')

    f_config = FORMULAS.get(formula_name, FORMULAS['stitch_2clip'])
    valid_slots = f_config.get('slots', [])

    # Map user shorthand to actual paths
    # Heuristic: 'start' maps to first occurrence of 'start_frame', etc.
    destination_rel = None

    # explicit full match check (e.g. forward/start_frame.png)
    if slot in valid_slots:
        destination_rel = slot
    
    # shorthand mapping logic
    else:
        # Simple flexible matching
        # e.g. "fs" -> matches "forward" and "start"
        # "start" -> matches "start"
        
        candidates = []
        target_tokens = []
        if slot in ['fs', 'forward_start']: target_tokens = ['forward', 'start']
        elif slot in ['fe', 'forward_end']: target_tokens = ['forward', 'end']
        elif slot in ['rs', 'reverse_start']: target_tokens = ['reverse', 'start']
        elif slot in ['re', 'reverse_end']: target_tokens = ['reverse', 'end']
        elif slot == 'start': target_tokens = ['start']
        elif slot == 'end': target_tokens = ['end']
        else: target_tokens = [slot] # Custom guess

        # Find best match in valid_slots
        from pathlib import Path as P # local alias
        for vs in valid_slots:
            if all(t in vs for t in target_tokens):
                candidates.append(vs)
        
        if candidates:
            # Pick the shortest match or first one? 
            # For circular: 'start' matches 'loop_source/start_frame.png' -> Perfect.
            destination_rel = candidates[0]

    if not destination_rel:
        print(f"❌ Invalid slot '{slot}' for formula '{formula_name}'.")
        print(f"   Valid slots: {valid_slots}")
        return

    dest = kit_path / destination_rel
    subdir = dest.parent.name
    filename = dest.name
    dest = kit_path / subdir / filename
    dest.parent.mkdir(exist_ok=True)
    
    shutil.copy2(source, dest)
    print(f"✅ Placed: {source.name}")
    print(f"   → {kit_path.name}/{subdir}/{filename}")

def cmd_list(args):
    """List recent generated assets."""
    print("📸 Recent Generated Assets:\n")
    
    matches = []
    for brain_folder in ARTIFACT_DIR.iterdir():
        if brain_folder.is_dir():
            for f in brain_folder.glob("*.png"):
                matches.append((f, f.stat().st_mtime))
    
    if not matches:
        print("  (No images found)")
        return
    
    # Sort by most recent
    matches.sort(key=lambda x: x[1], reverse=True)
    
    for f, _ in matches[:10]:
        print(f"  • {f.name}")

def run(args):
    """Main entry point for asset command."""
    if args.asset_action == 'place':
        cmd_place(args)
    elif args.asset_action == 'list':
        cmd_list(args)
    else:
        print("Usage: contentos asset {place|list}")
