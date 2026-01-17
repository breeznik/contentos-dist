"""Boot command - AI onboarding for any system."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.context import context_manager
from core.brain import brain_exists, load_state, load_playbook, load_learnings, list_themes

def run(args):
    """Generate AI onboarding context for any AI system."""
    ctx = context_manager.get_current_context()
    
    print("=" * 60)
    print("CONTENTOS AI ONBOARDING CONTEXT")
    print("=" * 60)
    print("\nCopy everything below and paste to any AI assistant.\n")
    print("-" * 60)
    
    # System Overview
    print("""
## ContentOS System

ContentOS is a CLI-based YouTube content production system.
Each channel has its own folder with brain/, production/, and analytics/.

### Core Commands
| Command | Purpose |
|---------|---------|
| `contentos channel use <name>` | Switch active channel |
| `contentos brain show` | View channel knowledge |
| `contentos brain set-theme <name>` | Switch theme |
| `contentos kit create "<name>"` | Create production kit |
| `contentos health` | System diagnostics |
| `contentos scout --keyword "<kw>"` | Market research |
| `contentos scan comments` | Audience analysis |
""")

    # Active Channel
    if ctx:
        print(f"### Active Channel: {ctx.name}")
        print(f"Path: `{ctx.path}`\n")
        
        # Brain State
        if brain_exists(ctx):
            state = load_state(ctx)
            identity = state.get('identity', {})
            audience = state.get('audience', {})
            
            print("### Channel Identity")
            print(f"- **Name**: {identity.get('name', 'Unknown')}")
            print(f"- **Niche**: {identity.get('niche', 'Not set')}")
            print(f"- **Audience**: {identity.get('audience', 'Not set')}")
            print(f"- **Tone**: {identity.get('tone', 'Not set')}")
            
            print(f"\n### Active Theme: `{state.get('active_theme', 'loop')}`")
            
            themes = list_themes(ctx)
            if themes:
                print(f"Available themes: {', '.join(themes)}")
            
            # Audience Wants
            wants = audience.get('wants', [])
            if wants:
                print("\n### Audience Wants")
                for w in wants[:5]:
                    print(f"- {w}")
            
            # Recent Learnings (truncated)
            learnings = load_learnings(ctx)
            if learnings and len(learnings) > 100:
                print("\n### Recent Learnings (Summary)")
                # Extract first 500 chars
                print(learnings[:500] + "...")
        else:
            print("\n[!] Brain not initialized. Run: `contentos brain init`")
        
        # Production kits count
        prod_path = ctx.production_path
        if prod_path.exists():
            kits = [d for d in prod_path.iterdir() if d.is_dir()]
            print(f"\n### Production Kits: {len(kits)} active")
    else:
        print("\n[!] No active channel. Run: `contentos channel use <name>`")
    
    print("\n" + "-" * 60)
    print("\nTo create content, ask the AI to run:")
    print("  contentos kit create \"<video_name>\" --theme loop")
    print("\nThe AI should read the prompt.txt and script.txt in the created kit.")
    print("=" * 60)
