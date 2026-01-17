"""Brain command - Manage channel knowledge system."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.context import context_manager
from core.brain import (
    init_brain, load_state, load_playbook, load_learnings,
    add_learning, set_active_theme, brain_exists, get_prompt_context
)

def cmd_init(args):
    """Initialize brain for current channel."""
    ctx = context_manager.get_current_context()
    if not ctx:
        print("No active channel.")
        return
    
    if brain_exists(ctx):
        print(f"Brain already exists for {ctx.name}.")
        print("Use 'contentos brain show' to view current state.")
        return
    
    init_brain(ctx)
    print(f"Brain initialized for {ctx.name}!")
    print(f"  Created: brain/state.json")
    print(f"  Created: brain/themes/ (loop, advice, cinematic)")
    print(f"  Created: brain/learnings.md")
    print("\nNext: Run 'contentos scout' or 'contentos scan' to populate learnings.")

def cmd_show(args):
    """Display current brain state."""
    ctx = context_manager.get_current_context()
    if not ctx:
        print("No active channel.")
        return
    
    if not brain_exists(ctx):
        print(f"No brain found for {ctx.name}.")
        print("Run: contentos brain init")
        return
    
    state = load_state(ctx)
    
    print(f"\n{'='*50}")
    print(f"CHANNEL BRAIN: {ctx.name}")
    print(f"{'='*50}")
    
    # Identity
    identity = state.get('identity', {})
    print(f"\n[Identity]")
    print(f"  Name:     {identity.get('name', 'Not set')}")
    print(f"  Niche:    {identity.get('niche', 'Not set')}")
    print(f"  Audience: {identity.get('audience', 'Not set')}")
    print(f"  Tone:     {identity.get('tone', 'Not set')}")
    
    # Performance
    perf = state.get('performance', {})
    print(f"\n[Performance]")
    print(f"  Total Videos: {perf.get('total_videos', 0)}")
    print(f"  Avg Views:    {perf.get('avg_views', 0)}")
    print(f"  Best Format:  {perf.get('best_format', 'Unknown')}")
    print(f"  Best Time:    {perf.get('best_post_time', 'Unknown')}")
    
    # Audience
    audience = state.get('audience', {})
    print(f"\n[Audience]")
    wants = audience.get('wants', [])
    complaints = audience.get('complaints', [])
    print(f"  Sentiment: {audience.get('sentiment', 0):.2f}")
    print(f"  Wants:     {', '.join(wants[:3]) if wants else 'No data'}")
    print(f"  Complaints: {', '.join(complaints[:3]) if complaints else 'No data'}")
    
    # Active Theme
    print(f"\n[Active Theme]")
    print(f"  {state.get('active_theme', 'loop')}")
    
    print(f"\n{'='*50}")
    print(f"Updated: {state.get('updated_at', 'Never')}")

def cmd_set_theme(args):
    """Set the active theme for kit creation."""
    ctx = context_manager.get_current_context()
    if not ctx:
        print("No active channel.")
        return
    
    if not brain_exists(ctx):
        print("Brain not initialized. Run: contentos brain init")
        return
    
    theme_name = args.theme_name.lower()
    set_active_theme(ctx, theme_name)
    print(f"Active theme set to: {theme_name}")
    print("Next kit will use this theme's prompt formula.")

def cmd_learn(args):
    """Add a manual learning to the brain."""
    ctx = context_manager.get_current_context()
    if not ctx:
        print("No active channel.")
        return
    
    if not brain_exists(ctx):
        init_brain(ctx)
    
    category = args.category.lower()
    valid_categories = ['performance', 'audience', 'gaps', 'failures']
    if category not in valid_categories:
        print(f"Invalid category. Use: {', '.join(valid_categories)}")
        return
    
    add_learning(ctx, category, args.insight, evidence="Manual entry")
    print(f"Learning added to {category}:")
    print(f"  {args.insight}")

def cmd_context(args):
    """Show the full prompt context that would be injected into kit creation."""
    ctx = context_manager.get_current_context()
    if not ctx:
        print("No active channel.")
        return
    
    if not brain_exists(ctx):
        print("Brain not initialized. Run: contentos brain init")
        return
    
    context = get_prompt_context(ctx)
    print(context)

def run(args):
    """Entry point for brain command."""
    if args.brain_action == 'init':
        cmd_init(args)
    elif args.brain_action == 'show':
        cmd_show(args)
    elif args.brain_action == 'set-theme':
        cmd_set_theme(args)
    elif args.brain_action == 'learn':
        cmd_learn(args)
    elif args.brain_action == 'context':
        cmd_context(args)
    else:
        print("Usage: contentos brain {init|show|set-theme|learn|context}")
