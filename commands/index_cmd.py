"""Index command - AI-friendly context surfing with progressive disclosure."""
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.context import context_manager
from core.config import load_global_config
from core.brain import brain_exists, load_state, list_themes, get_themes_path, load_learnings

def get_system_index() -> Dict[str, Any]:
    """Build the root system index."""
    global_cfg = load_global_config()
    ctx = context_manager.get_current_context()
    
    # Count channels
    channels_path = Path(__file__).parent.parent / "channels"
    channels = [d.name for d in channels_path.iterdir() 
                if d.is_dir() and not d.name.startswith('.')]
    
    return {
        "_path": "",
        "_type": "root",
        "system": {
            "name": "ContentOS",
            "version": "4.0",
            "active_channel": ctx.name if ctx else None
        },
        "nodes": {
            "channels": {"_type": "list", "_count": len(channels), "_items": channels},
            "brain": {"_type": "object", "_desc": "Channel knowledge system"},
            "kits": {"_type": "list", "_desc": "Production kits"},
            "commands": {"_type": "list", "_count": 16, "_desc": "CLI commands"},
            "config": {"_type": "object", "_desc": "System settings"}
        }
    }

def get_brain_index(ctx) -> Dict[str, Any]:
    """Build brain section index."""
    if not brain_exists(ctx):
        return {"_error": "Brain not initialized. Run: contentos brain init"}
    
    state = load_state(ctx)
    themes = list_themes(ctx)
    
    return {
        "_path": "brain",
        "_type": "object",
        "_desc": f"Knowledge system for {ctx.name}",
        "identity": {
            "_type": "object",
            "_preview": state.get('identity', {}).get('name', 'Unknown'),
            "name": state.get('identity', {}).get('name'),
            "niche": state.get('identity', {}).get('niche'),
            "audience": state.get('identity', {}).get('audience'),
            "tone": state.get('identity', {}).get('tone')
        },
        "themes": {
            "_type": "list",
            "_count": len(themes),
            "_items": themes,
            "_active": state.get('active_theme', 'loop')
        },
        "audience": {
            "_type": "object",
            "_preview": f"Sentiment: {state.get('audience', {}).get('sentiment', 0)}",
            "wants": state.get('audience', {}).get('wants', []),
            "complaints": state.get('audience', {}).get('complaints', []),
            "sentiment": state.get('audience', {}).get('sentiment', 0)
        },
        "learnings": {
            "_type": "file",
            "_size": len(load_learnings(ctx)),
            "_desc": "Accumulated insights from agents"
        }
    }

def get_theme_content(ctx, theme_name: str) -> Dict[str, Any]:
    """Get specific theme file content."""
    theme_path = get_themes_path(ctx) / f"{theme_name}.md"
    if not theme_path.exists():
        return {"_error": f"Theme '{theme_name}' not found"}
    
    content = theme_path.read_text(encoding='utf-8')
    return {
        "_path": f"brain.themes.{theme_name}",
        "_type": "file",
        "_format": "markdown",
        "content": content
    }

def get_kits_index(ctx) -> Dict[str, Any]:
    """Build kits section index."""
    prod_path = ctx.production_path
    if not prod_path.exists():
        return {"_error": "No production folder"}
    
    kits = sorted([d.name for d in prod_path.iterdir() if d.is_dir()])
    
    return {
        "_path": "kits",
        "_type": "list",
        "_count": len(kits),
        "_items": kits[-10:],  # Last 10
        "_note": f"Showing last 10 of {len(kits)}" if len(kits) > 10 else None
    }

def get_kit_detail(ctx, kit_id: str) -> Dict[str, Any]:
    """Get specific kit details."""
    prod_path = ctx.production_path
    matches = list(prod_path.glob(f"{kit_id}*"))
    
    if not matches:
        return {"_error": f"Kit '{kit_id}' not found"}
    
    kit_path = matches[0]
    files = {f.name: f.stat().st_size for f in kit_path.iterdir() if f.is_file()}
    
    result = {
        "_path": f"kits.{kit_id}",
        "_type": "object",
        "name": kit_path.name,
        "files": files
    }
    
    # Include script preview if exists
    script = kit_path / "script.txt"
    if script.exists():
        result["script_preview"] = script.read_text(encoding='utf-8')[:300]
    
    return result

def get_commands_index() -> Dict[str, Any]:
    """List available commands."""
    return {
        "_path": "commands",
        "_type": "list",
        "categories": {
            "channel": ["list", "use", "status", "create"],
            "brain": ["init", "show", "set-theme", "learn", "context"],
            "content": ["kit create", "kit list", "kit publish"],
            "research": ["scout", "scan comments"],
            "analytics": ["sync", "retention"],
            "system": ["health", "boot", "index", "config"]
        }
    }

def get_config_index() -> Dict[str, Any]:
    """Get system config."""
    global_cfg = load_global_config()
    return {
        "_path": "config",
        "_type": "object",
        "features": {
            "llm_swarm": global_cfg.features.llm_swarm if hasattr(global_cfg, 'features') else False
        }
    }

def resolve_path(path: str, ctx) -> Dict[str, Any]:
    """Resolve dot-notation path to data."""
    if not path:
        return get_system_index()
    
    parts = path.split('.')
    root = parts[0]
    
    if root == "channels":
        return get_system_index()["nodes"]["channels"]
    elif root == "brain":
        if len(parts) == 1:
            return get_brain_index(ctx)
        elif parts[1] == "themes":
            if len(parts) == 2:
                return get_brain_index(ctx)["themes"]
            else:
                return get_theme_content(ctx, parts[2])
        elif parts[1] == "identity":
            return get_brain_index(ctx)["identity"]
        elif parts[1] == "audience":
            return get_brain_index(ctx)["audience"]
        elif parts[1] == "learnings":
            return {"_path": "brain.learnings", "_type": "file", "content": load_learnings(ctx)}
    elif root == "kits":
        if len(parts) == 1:
            return get_kits_index(ctx)
        else:
            return get_kit_detail(ctx, parts[1])
    elif root == "commands":
        return get_commands_index()
    elif root == "config":
        return get_config_index()
    
    return {"_error": f"Unknown path: {path}"}

def format_human(data: Dict[str, Any], indent: int = 0) -> str:
    """Format data for human reading."""
    lines = []
    prefix = "  " * indent
    
    # Handle metadata
    if "_path" in data:
        lines.append(f"{prefix}PATH: {data['_path'] or '/'}")
    if "_type" in data:
        lines.append(f"{prefix}TYPE: {data['_type']}")
    if "_error" in data:
        lines.append(f"{prefix}[!] {data['_error']}")
        return "\n".join(lines)
    if "_desc" in data:
        lines.append(f"{prefix}DESC: {data['_desc']}")
    
    lines.append("")
    
    # Handle content
    for key, val in data.items():
        if key.startswith('_'):
            continue
        
        if isinstance(val, dict):
            if "_type" in val:
                # It's a node reference
                node_type = val.get('_type', 'object')
                count = val.get('_count', '')
                preview = val.get('_preview', '')
                items = val.get('_items', [])
                active = val.get('_active', '')
                
                if items:
                    items_str = ', '.join(items[:5])
                    if len(items) > 5:
                        items_str += f" (+{len(items)-5} more)"
                    lines.append(f"{prefix}[{key}] ({node_type}, {count}) -> {items_str}")
                    if active:
                        lines.append(f"{prefix}  ACTIVE: {active}")
                elif preview:
                    lines.append(f"{prefix}[{key}] ({node_type}) -> {preview}")
                else:
                    lines.append(f"{prefix}[{key}] ({node_type})")
                lines.append(f"{prefix}  Drill: contentos index {data.get('_path', '')}.{key}".replace('..', '.').strip('.'))
            else:
                # Regular dict
                for k, v in val.items():
                    if not k.startswith('_'):
                        lines.append(f"{prefix}{k}: {v}")
        elif isinstance(val, list):
            lines.append(f"{prefix}{key}: {', '.join(str(v) for v in val[:5])}")
        elif key == "content":
            # File content - truncate
            lines.append(f"{prefix}--- CONTENT ---")
            lines.append(val[:1000] if len(val) > 1000 else val)
            if len(val) > 1000:
                lines.append(f"{prefix}... ({len(val) - 1000} more chars)")
        else:
            lines.append(f"{prefix}{key}: {val}")
    
    return "\n".join(lines)

def run(args):
    """Entry point for index command."""
    ctx = context_manager.get_current_context()
    path = args.path if hasattr(args, 'path') and args.path else ""
    use_json = args.json if hasattr(args, 'json') and args.json else False
    
    if not ctx and path and path != "commands":
        print("[!] No active channel. Run: contentos channel use <name>")
        return
    
    data = resolve_path(path, ctx)
    
    if use_json:
        print(json.dumps(data, indent=2))
    else:
        print("\n" + "=" * 50)
        print("CONTENTOS INDEX")
        print("=" * 50)
        print(format_human(data))
        print("\n" + "-" * 50)
        if not path:
            print("Navigate: contentos index <path>")
            print("Examples:")
            print("  contentos index brain")
            print("  contentos index brain.themes.loop")
            print("  contentos index kits.018")
        print("=" * 50)
