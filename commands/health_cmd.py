"""Health command - system diagnostic checks."""
import sys
import json
from pathlib import Path
from typing import List, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.context import context_manager
from core.brain import brain_exists, get_brain_path

def check_json_file(path: Path) -> Tuple[bool, str]:
    """Check if a JSON file exists and is valid."""
    if not path.exists():
        return False, "File not found"
    try:
        text = path.read_text(encoding='utf-8')
        json.loads(text)
        return True, "Valid JSON"
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"
    except Exception as e:
        return False, f"Error: {e}"

def check_brain_health(ctx) -> List[str]:
    """Check integrity of the channel brain."""
    issues = []
    brain_path = get_brain_path(ctx)
    
    if not brain_path.exists():
        issues.append("[X] Brain folder missing (Run 'contentos brain init')")
        return issues
        
    # Check state.json
    ok, msg = check_json_file(brain_path / "state.json")
    if not ok:
        issues.append(f"[X] brain/state.json: {msg}")
        
    # Check themes folder
    themes_path = brain_path / "themes"
    if not themes_path.exists():
        issues.append("[X] brain/themes/ folder missing")
    else:
        themes = list(themes_path.glob("*.md"))
        if not themes:
            issues.append("[!] No themes found in brain/themes/")
            
    # Check learnings.md
    if not (brain_path / "learnings.md").exists():
        issues.append("[X] brain/learnings.md missing")
        
    return issues

def check_channel_structure(ctx) -> List[str]:
    """Check core channel folders."""
    issues = []
    
    required = [
        ctx.production_path,
        ctx.path / "archive",
        ctx.analytics_path
    ]
    
    for path in required:
        if not path.exists():
            issues.append(f"[!] Missing folder: {path.name}/")
            
    # Check config
    channel_json = ctx.path / ".channel.json"
    ok, msg = check_json_file(channel_json)
    if not ok:
        issues.append(f"[X] .channel.json: {msg}")
        
    return issues

def run(args):
    """Run health checks."""
    ctx = context_manager.get_current_context()
    if not ctx:
        print("[X] No active channel. Run: contentos channel use <name>")
        return
        
    print(f"\nHEALTH CHECK: {ctx.name}")
    print("=" * 40)
    
    all_issues = []
    
    # 1. Brain Health
    brain_issues = check_brain_health(ctx)
    print(f"\n[BRAIN SYSTEM]")
    if not brain_issues:
        print("[OK] Structured Brain")
        print("[OK] State JSON")
        print("[OK] Knowledge Base")
    else:
        for issue in brain_issues:
            print(issue)
        all_issues.extend(brain_issues)
            
    # 2. Channel Structure
    struct_issues = check_channel_structure(ctx)
    print(f"\n[FILE SYSTEM]")
    if not struct_issues:
        print("[OK] Core Folders")
        print("[OK] Configuration")
    else:
        for issue in struct_issues:
            print(issue)
        all_issues.extend(struct_issues)
            
    # 3. Credentials (shallow check)
    print(f"\n[ACCESS]")
    creds_ok = True
    token_pickle = ctx.analytics_path / "token.pickle"
    if token_pickle.exists():
        print("[OK] YouTube Token")
    else:
        print("[!] YouTube Token .... MISSING (Run 'contentos sync' to auth)")
        creds_ok = False
        
    print("\n" + "=" * 40)
    if not all_issues and creds_ok:
        print("SYSTEM HEALTHY. Ready to create.")
    else:
        print(f"[!] Found {len(all_issues)} issues.")
